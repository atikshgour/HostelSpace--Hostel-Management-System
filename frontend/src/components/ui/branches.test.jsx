// US-21/22 | Shared form coercion, errors, dialogs and keyboard navigation.
import {act, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {useRouter} from 'next/navigation';
import AppShell, {ResourceForm, ErrorMessage, useResource} from './AppShell';
import Dialog from './Dialog';
import FormField from './FormField';
import HistoryTimeline from './HistoryTimeline';
import EmptyState from './EmptyState';
import ConfirmDialog from './ConfirmDialog';
import {installApi, portal, change, submit, stamp} from '../../../test-support/fixtures';

jest.mock('next/navigation', () => {
  const router={replace:jest.fn(),refresh:jest.fn()};
  return {useRouter:()=>router,usePathname:()=>global.__testPath || '/dashboard'};
});

beforeEach(() => {installApi(); jest.clearAllMocks();});

test('resource form serializes numbers, checkboxes, nullable and optional fields', async () => {
  const save = jest.fn().mockResolvedValue({}), cancel = jest.fn();
  render(<ResourceForm title="Policy" fields={[
    {name:'text', label:'Text', maxLength:10}, {name:'notes', label:'Notes', type:'textarea', maxLength:10},
    {name:'count', label:'Count', type:'number'}, {name:'enabled', label:'Enabled', type:'checkbox'},
    {name:'date', label:'Date', nullable:true, optional:true}, {name:'optional', label:'Optional', optional:true},
    {name:'choice', label:'Choice', options:[{value:1,label:'One'},'Two']},
  ]} onSave={save} onCancel={cancel}/>);
  change('Text','hello'); change('Notes','notes'); change('Count','2'); change('Choice','1');
  fireEvent.click(screen.getByLabelText('Enabled'));
  submit('Save');
  await screen.findByText('Changes saved.');
  expect(save).toHaveBeenCalledWith({text:'hello',notes:'notes',count:2,enabled:true,date:null,choice:'1'});
  expect(screen.getByLabelText('Text')).toHaveValue('');
  fireEvent.click(screen.getByText('Cancel edit')); expect(cancel).toHaveBeenCalled();
});

test('resource form preserves edit values and reports rejected writes', async () => {
  const save = jest.fn().mockRejectedValueOnce(Object.assign(Error('Conflict'), {fields:{name:['Unavailable'], other:'Invalid'}})).mockResolvedValue({});
  render(<ResourceForm title="Edit" fields={[{name:'name',label:'Name'}, {name:'optional',label:'Optional',optional:true}, {name:'flag',label:'Flag',type:'checkbox'}, {name:'notes',label:'Notes',type:'textarea'}, {name:'choice',label:'Choice',options:['A']}]} initial={{name:'Before', optional:'kept', flag:true, notes:'Note', choice:'A'}} onSave={save}/>);
  submit('Save'); expect(await screen.findByRole('alert')).toHaveTextContent('Conflict');
  expect(screen.getByText(/Unavailable/)).toBeVisible();
  submit('Save'); await screen.findByText('Changes saved.');
  expect(screen.getByLabelText('Name')).toHaveValue('Before');
});

test('shared presentation handles histories, optional error fields and dialog cancellation', () => {
  const close = jest.fn();
  const view = render(<><HistoryTimeline/><EmptyState title="Empty"/><FormField label="Required" error="Invalid" hint="Hint" required><input/></FormField><ErrorMessage error={Error('Failure')}/><Dialog title="Dialog" onClose={close}><p>Inside</p></Dialog></>);
  expect(screen.getByText('Failure')).toBeVisible();
  fireEvent.click(screen.getByText('Inside')); expect(close).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('dialog')); fireEvent(screen.getByRole('dialog'),new Event('cancel',{bubbles:true,cancelable:true}));
  expect(close).toHaveBeenCalledTimes(2);
  view.unmount();
  render(<><HistoryTimeline items={[{id:1,from_status:'Pending',to_status:'Approved',occurred_at:stamp},{id:2,to_status:'Open'}]}/><EmptyState>No data</EmptyState><FormField label="Auto"/></>);
  expect(screen.getByText(/Pending/)).toBeVisible();
});

test.each(['STUDENT','WARDEN','CHIEF_WARDEN','DIRECTOR','LAUNDRY_STAFF','MESS_STAFF','MAINTENANCE_STAFF','CONTENT_STAFF','UNKNOWN'])('shell renders the %s menu and signs out', async (role) => {
  installApi(role, {}, role === 'UNKNOWN' ? '/unknown' : '/dashboard');
  const router = useRouter();
  portal(<p>Domain content</p>);
  expect(await screen.findByText('Domain content')).toBeVisible();
  fireEvent.click(screen.getByText('Sign out'));
  await waitFor(()=>expect(router.replace).toHaveBeenCalledWith('/login'));
});

test('mobile navigation restores focus, traps Tab, closes and responds to media changes', async () => {
  let mediaChange;
  const media = {matches:true,addEventListener:jest.fn((_,fn)=>{mediaChange=fn;}),removeEventListener:jest.fn()};
  window.matchMedia = jest.fn(()=>media);
  jest.spyOn(HTMLElement.prototype,'getClientRects').mockReturnValue([{}]);
  portal(<p>Content</p>); await screen.findByText('Content');
  const trigger=screen.getByLabelText('Open navigation menu');
  fireEvent.click(trigger);
  const aside=screen.getByRole('navigation',{name:'Main navigation'}).closest('aside');
  const controls=aside.querySelectorAll('a,button');
  controls[0].focus(); fireEvent.keyDown(document,{key:'Tab',shiftKey:true}); expect(document.activeElement).toBe(controls[controls.length-1]);
  fireEvent.keyDown(document,{key:'Tab'}); expect(document.activeElement).toBe(controls[0]);
  fireEvent.keyDown(document,{key:'ArrowDown'}); fireEvent.keyDown(document,{key:'Escape'});
  expect(trigger).toHaveAttribute('aria-expanded','false');
  fireEvent.click(trigger); fireEvent.click(screen.getByLabelText('Close navigation'));
  fireEvent.click(trigger); fireEvent.click(screen.getByLabelText('Close navigation menu'));
  act(()=>{media.matches=false;mediaChange();});
  expect(trigger).toHaveAttribute('aria-expanded','false');
  jest.restoreAllMocks();
});

test.each([401,403,500])('shell handles session status %s', async status => {
  fetch.mockImplementation(async()=>({ok:false,status,json:async()=>({message:'Unavailable'})}));
  render(<AppShell/>);
  if(status===500) expect(await screen.findByRole('alert')).toHaveTextContent('Unavailable');
  else await waitFor(()=>expect(useRouter().replace).toHaveBeenCalledWith('/login'));
});

test('resource ignores responses after unmount and exposes loading failures', async () => {
  function Probe(){const {data,error,refresh}=useResource(['/api/x/',null]); return <><button onClick={refresh}>Refresh</button><p>{data?'Loaded':'Loading'}</p><ErrorMessage error={error}/></>;}
  let resolve;
  fetch.mockImplementation(()=>new Promise(r=>{resolve=r;}));
  const view=render(<Probe/>); view.unmount();
  await act(async()=>resolve({ok:true,json:async()=>({results:[]})}));
  fetch.mockRejectedValue(Error('Offline')); render(<Probe/>);
  expect(await screen.findByRole('alert')).toHaveTextContent('Offline');
});

test('logout errors stay visible', async()=>{
  installApi('STUDENT',{'POST /api/auth/logout/':{httpStatus:500}});
  portal(<p>Content</p>); await screen.findByText('Content'); fireEvent.click(screen.getByText('Sign out'));
  expect(await screen.findByRole('alert')).toBeVisible();
});

test('confirmation dialog forwards the user decision',()=>{
  const confirm=jest.fn(),cancel=jest.fn();
  render(<ConfirmDialog title="Confirm" onConfirm={confirm} onCancel={cancel}>Continue?</ConfirmDialog>);
  fireEvent.click(screen.getByText('Confirm',{selector:'button'}));fireEvent.click(screen.getByText('Cancel'));
  expect(confirm).toHaveBeenCalled();expect(cancel).toHaveBeenCalled();
});
