// US-22 | Retained legacy component, isolated from its unavailable old UI adapter.
// These tests are not evidence that this unregistered component is integrated.
import {act,fireEvent,render,screen,waitFor} from '@testing-library/react';
import Workspace,{LeaveForm,LeaveRecords,Decision} from './LeaveWorkspace';
import {useIdentity,useRows} from '../arin/common';

jest.mock('../arin/api',()=>({request:jest.fn()}),{virtual:true});
jest.mock('../arin/common',()=>({
  useIdentity:jest.fn(),useRows:jest.fn(),styles:{card:'card',muted:'muted',grid:'grid'},
  Frame:({children,title})=><main><h1>{title}</h1>{children}</main>,
  Field:({label,children,...props})=><label>{label}{children || <input {...props}/>}</label>,
  ErrorBox:({error})=>error?<p role="alert">{error.message}</p>:null,
  Pager:()=> <p>Pages</p>,Timeline:()=> <p>History</p>,
}),{virtual:true});
const {request}=require('../arin/api');
const row={id:'l1',student:'s1',reason:'Synthetic reason',status:'Pending',start_date:'2026-11-17',end_date:'2026-11-18',transitions:[]};
beforeEach(()=>{
  useIdentity.mockReturnValue({user:{role:'STUDENT'}});
  useRows.mockReturnValue({rows:[row],loading:false,error:null});
  request.mockReset().mockResolvedValue(row);
});
const input=(label,value)=>fireEvent.change(screen.getByLabelText(label),{target:{value}});

test.each(['STUDENT','WARDEN','CHIEF_WARDEN','DIRECTOR',undefined])('legacy role %s gates its workflow',role=>{
  useIdentity.mockReturnValue({user:role?{role}:null});render(<Workspace/>);
  if(!role || role==='DIRECTOR') expect(screen.getByText(/no leave workflow/)).toBeVisible();
  else expect(screen.getByText('Synthetic reason')).toBeVisible();
});

test('legacy leave form validates reversed dates and exposes write/retry outcomes',async()=>{
  const refresh=jest.fn();render(<LeaveForm refresh={refresh}/>);
  input('Start date','2026-11-18');input('End date','2026-11-17');input('Reason','Visit');fireEvent.submit(screen.getByText('Submit leave').closest('form'));
  expect(screen.getByRole('alert')).toHaveTextContent(/on or after/);expect(request).not.toHaveBeenCalled();
  input('End date','2026-11-19');request.mockRejectedValueOnce(Error('Offline'));fireEvent.submit(screen.getByText('Submit leave').closest('form'));expect(await screen.findByRole('alert')).toHaveTextContent('Offline');
  fireEvent.submit(screen.getByText('Submit leave').closest('form'));expect(await screen.findByText(/Pending status/)).toBeVisible();expect(refresh).toHaveBeenCalled();
});

test.each([['WARDEN','Pending'],['CHIEF_WARDEN','Escalated']])('legacy %s finalizes %s with retry feedback',async(role,status)=>{
  const refresh=jest.fn();render(<Decision row={{...row,status}} role={role} refresh={refresh}/>);
  input('Decision', 'Rejected');input('Decision remarks','Synthetic review');request.mockRejectedValueOnce(Error('Conflict'));fireEvent.submit(screen.getByText('Save decision').closest('form'));expect(await screen.findByRole('alert')).toHaveTextContent('Conflict');
  fireEvent.submit(screen.getByText('Save decision').closest('form'));await waitFor(()=>expect(refresh).toHaveBeenCalled());
});

test('legacy detail refreshes after a decision and ignores late responses',async()=>{
  const refresh=jest.fn();const view=render(<LeaveRecords detailId="l1" role="WARDEN" revision={0} refresh={refresh}/>);
  await screen.findByText('Synthetic reason');input('Decision remarks','Reviewed');fireEvent.submit(screen.getByText('Save decision').closest('form'));await waitFor(()=>expect(refresh).toHaveBeenCalled());
  request.mockRejectedValueOnce(Error('Gone'));fireEvent.click(screen.getByText('Load / refresh request'));expect(await screen.findByRole('alert')).toHaveTextContent('Gone');
  request.mockRejectedValueOnce(Error('No access'));view.rerender(<LeaveRecords detailId="l2" role="STUDENT" revision={1} refresh={refresh}/>);await waitFor(()=>expect(screen.getByRole('alert')).toHaveTextContent('No access'));
  let resolve;request.mockImplementation(()=>new Promise(r=>{resolve=r;}));view.rerender(<LeaveRecords detailId="l3" role="STUDENT" revision={2} refresh={refresh}/>);view.unmount();await act(async()=>resolve(row));
});

test('legacy empty and loading states distinguish availability',()=>{
  useRows.mockReturnValue({rows:[],loading:true,error:null});const view=render(<LeaveRecords role="STUDENT"/>);expect(screen.getByRole('status')).toHaveTextContent(/Loading/);
  useRows.mockReturnValue({rows:[],loading:false,error:null});view.rerender(<LeaveRecords role="STUDENT"/>);expect(screen.getByText('No records')).toBeVisible();
});
