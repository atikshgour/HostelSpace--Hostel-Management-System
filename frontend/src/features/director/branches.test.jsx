// US-01/03/04/21 | Staff account/content/settings workflows and error handling.
import {fireEvent, render, screen, waitFor, within} from '@testing-library/react';
import UserManagement from './UserManagement';
import SettingsForm from './SettingsForm';
import DirectorPanel from './DirectorPanel';
import ContentEditor from '../information/ContentEditor';
import StudyRoomEditor from '../study-room/StudyRoomEditor';
import {installApi,portal,change,submit,users,writes,stamp} from '../../../test-support/fixtures';

jest.mock('next/navigation',()=>{const router={replace:jest.fn(),refresh:jest.fn()};return {useRouter:()=>router,usePathname:()=>global.__testPath || '/dashboard'};});

test('director creates student and service accounts, searches and edits',async()=>{
  installApi('DIRECTOR',{'/api/director/users/':users}); portal(<UserManagement/>);
  await screen.findByText('Synthetic Student');
  change('Search people','missing'); expect(screen.getByText(/No matching/)).toBeVisible(); change('Search people','');
  change('Account type','MESS_STAFF'); expect(screen.getByText('Inactive Staff')).toBeVisible(); change('Account type','All');
  fireEvent.click(screen.getByText('+ Create account'));
  change('Username','new');change('First name','New');change('Initial password','Synthetic-example-78214!');change('Student number / SRN','TEST-9');change('Room number','9');change('Assigned Warden','2');
  submit('Create account'); await screen.findByText(/Account created/);
  expect(JSON.parse(writes('/api/director/users/')[0][1].body)).toMatchObject({role:'STUDENT',assigned_warden:'2',is_active:true});
  fireEvent.click(screen.getByText('+ Create account'));
  const dialog=within(screen.getByRole('dialog'));change('Account type','WARDEN',dialog);change('Username','newwarden');change('First name','New');change('Initial password','Synthetic-example-78214!');change('Supervising Chief Warden','3');submit('Create account',dialog);
  await waitFor(()=>expect(writes('/api/director/users/')).toHaveLength(2));
  await waitFor(()=>expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  fireEvent.click(screen.getAllByText('Edit account')[0]);submit('Save changes');
  await screen.findByText('Account updated.');
  expect(writes('/api/director/users/1/')).toHaveLength(1);
});

test('account editing supports nonstudent rows and closes dialogs',async()=>{
  installApi('DIRECTOR',{'/api/director/users/':users});portal(<UserManagement/>);await screen.findAllByText('Edit account');
  fireEvent.click(screen.getAllByText('Edit account')[1]);expect(screen.getByLabelText('Supervising Chief Warden')).toBeVisible();fireEvent.click(screen.getByLabelText('Close dialog'));
  fireEvent.click(screen.getByText('+ Create account'));fireEvent.click(screen.getByLabelText('Close dialog'));
});

test('non-director account view has no creation controls',async()=>{
  installApi('WARDEN',{'/api/director/users/':users});portal(<UserManagement/>);await screen.findAllByText('Edit account');
  expect(screen.queryByText('+ Create account')).not.toBeInTheDocument();
  fireEvent.click(screen.getAllByText('Edit account')[0]);expect(screen.queryByLabelText('Assigned Warden')).not.toBeInTheDocument();
});

test('staff publishes, edits timed/untimed content and creates rules',async()=>{
  installApi('CONTENT_STAFF',{'/api/information/':[{id:1,title:'Timed',kind:'notice',active:true,starts_at:stamp,ends_at:stamp},{id:2,title:'Untimed',kind:'contact',active:false}],'/api/rules/':[{id:3,title:'Rule',active:false,weightage:'2'}]});portal(<ContentEditor/>);
  await screen.findByText('Timed');fireEvent.click(screen.getByText('+ Publish announcement'));
  change('Title','New');change('Content','Synthetic');change('Visible from','2026-11-17T10:00');change('Visible until','2026-11-18T10:00');submit('Save');
  await waitFor(()=>expect(writes('/api/information/')).toHaveLength(1));await waitFor(()=>expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  fireEvent.click(screen.getAllByText('Edit')[0]);submit('Save');await waitFor(()=>expect(writes('/api/information/1/')).toHaveLength(1));await waitFor(()=>expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  fireEvent.click(screen.getAllByText('Edit')[1]);fireEvent.click(screen.getByText('Cancel edit'));fireEvent.click(screen.getByLabelText('Close dialog'));
  fireEvent.click(screen.getByRole('button',{name:'Rules'}));await screen.findByText('Rule');fireEvent.click(screen.getByText('+ Create rule'));change('Rule title','New rule');change('Weightage','3');submit('Save');
  await waitFor(()=>expect(writes('/api/rules/')).toHaveLength(1));await waitFor(()=>expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  fireEvent.click(screen.getByText('Edit'));submit('Save');await waitFor(()=>expect(writes('/api/rules/3/')).toHaveLength(1));
  fireEvent.click(screen.getByRole('button',{name:'Announcements & contacts'}));
});

test('settings and study editor save backend values',async()=>{
  installApi('DIRECTOR',{'/api/director/settings/':[{key:'site_title',value:'HostelSpace'}]});
  const view=render(<SettingsForm/>);await screen.findByText('HostelSpace');change('Setting','support_contact');change('Value','Office');submit('Save');await screen.findByText('Changes saved.');expect(writes('/api/director/settings/')).toHaveLength(1);view.unmount();
  installApi('DIRECTOR',{'/api/study-room/':{status:'Open',timings:'9–5',message:'Quiet'}});render(<StudyRoomEditor/>);await screen.findByLabelText('Opening hours');change('Status','Closed');submit('Save');await screen.findByText('Changes saved.');expect(writes('/api/study-room/')).toHaveLength(1);
});

test.each([DirectorPanel,StudyRoomEditor])('staff panel exposes failed reads %#',async Component=>{
  installApi('DIRECTOR');fetch.mockRejectedValue(Error('Offline'));render(<Component/>);expect(await screen.findByRole('alert')).toHaveTextContent('Offline');
});

test('Director summary renders nonempty attendance sessions',async()=>{
  installApi('DIRECTOR',{'/api/director/summary/':{pending_leave:1,escalated_leave:1,open_complaints:1,unpaid_fees:1,active_students:2,attendance_by_session:[{id:1,title:'Evening',opens_at:stamp,accepted:2}]}});
  render(<DirectorPanel/>);expect(await screen.findByText('Evening')).toBeVisible();
});
