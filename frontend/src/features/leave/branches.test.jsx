// US-05/06/07/08/22 | Workflow roles, final states and failed/late responses.
import {act,fireEvent,render,screen,waitFor} from '@testing-library/react';
import LeaveWorkspace,{LeaveForm,LeaveHistory,LeaveReviewPanel} from './LeaveList';
import AttendanceWorkspace,{AttendanceSessionForm,AttendanceSubmit} from '../attendance/AttendanceHistory';
import DeviationPanel from '../deviations/DeviationPanel';
import {installApi,portal,change,submit,writes,stamp} from '../../../test-support/fixtures';

jest.mock('next/navigation',()=>{const router={replace:jest.fn(),refresh:jest.fn()};return {useRouter:()=>router,usePathname:()=>global.__testPath || '/dashboard'};});
const leave={id:'leave-1',student_name:'Synthetic',warden_name:'Warden',reason:'Family',status:'Pending',start_date:'2026-11-17',end_date:'2026-11-18',transitions:[{id:1,to_status:'Pending',occurred_at:stamp}]};

test.each(['WARDEN','CHIEF_WARDEN','STUDENT'])('%s leave detail preserves review permissions',async role=>{
  const row={...leave,status:role==='CHIEF_WARDEN'?'Escalated':'Pending'};
  installApi(role,{'/api/leaves/leave-1/':row});render(<LeaveWorkspace detailId="leave-1"/>);await screen.findByText('Family');
  if(role!=='STUDENT'){
    window.confirm=jest.fn(()=>false);change('Decision remarks','Synthetic review');submit('Save decision');expect(writes('/api/leaves/leave-1/decision/')).toHaveLength(0);
    window.confirm.mockReturnValue(true);change('Decision',role==='WARDEN'?'Escalated':'Approved');submit('Save decision');expect(await screen.findByText(/Decision saved/)).toBeVisible();
  }else expect(screen.queryByText('Save decision')).not.toBeInTheDocument();
});

test('leave list follows pagination, searches and filters',async()=>{
  const rows=Array.from({length:11},(_,i)=>({...leave,id:`leave-${i}`,student_name:i?'Synthetic':'',status:i?'Pending':'Approved'}));
  installApi('WARDEN',{'/api/leaves/?page=1':{results:rows,next:'/api/leaves/?page=2'},'/api/leaves/?page=2':{results:[],next:null}});render(<LeaveWorkspace/>);await screen.findByText('Page 1 · 10 requests');
  change('Status','All');fireEvent.click(screen.getByText('Next'));expect(screen.getByText('Page 2 · 11 requests')).toBeVisible();fireEvent.click(screen.getByText('Previous'));
  change('Search requests','none');expect(screen.getByText(/No requests match/)).toBeVisible();
});

test('leave write/review/read failures remain visible',async()=>{
  installApi('STUDENT',{'POST /api/leaves/':{httpStatus:400}});
  const view=render(<LeaveForm onSaved={jest.fn()}/>);change('Start date','2026-11-17');change('End date','2026-11-18');change('Reason','Synthetic');submit('Submit leave');expect(await screen.findByRole('alert')).toBeVisible();view.unmount();
  installApi('WARDEN',{'POST /api/leaves/leave-1/decision/':{httpStatus:400}});window.confirm=jest.fn(()=>true);
  const decision=render(<LeaveReviewPanel row={leave} role="WARDEN" onSaved={jest.fn()}/>);change('Decision remarks','Review');submit('Save decision');expect(await screen.findByRole('alert')).toBeVisible();decision.unmount();
  installApi();fetch.mockRejectedValue(Error('Offline'));render(<LeaveWorkspace/>);expect(await screen.findByRole('alert')).toBeVisible();
});

test('leave history fallbacks and final state have no review action',()=>{
  render(<><LeaveHistory/><LeaveHistory transitions={[{id:1,from_status:'Pending',to_status:'Approved',actor_name:'Warden',occurred_at:stamp}]}/><LeaveReviewPanel row={{status:'Approved'}} role="WARDEN"/></>);
  expect(screen.queryByText('Save decision')).not.toBeInTheDocument();expect(screen.getByText(/Warden/)).toBeVisible();
});

test('leave detail without optional names renders safe fallbacks',async()=>{
  installApi('STUDENT',{'/api/leaves/leave-1/':{...leave,student_name:'',warden_name:'',transitions:[]}});render(<LeaveWorkspace detailId="leave-1"/>);expect(await screen.findByText('Student request')).toBeVisible();
});

const session={id:'session-1',title:'Evening attendance',opens_at:stamp,closes_at:stamp,radius_m:100,max_accuracy_m:20};
test.each(['WARDEN','CHIEF_WARDEN','STUDENT'])('%s attendance shows sessions and retained history',async role=>{
  installApi(role,{'/api/attendance/sessions/?page=1':{results:[session]},'/api/attendance/history/?page=1':{results:[{id:1,result:'Accepted',reason_code:'WITHIN_POLICY',student:1,session:1,submitted_at:stamp}]}});
  render(<AttendanceWorkspace/>);expect(await screen.findByText('Evening attendance')).toBeVisible();expect(await screen.findByText(/Accepted/)).toBeVisible();
});

test('attendance form validates dates, posts numeric policy and shows server errors',async()=>{
  const data=installApi('WARDEN');const saved=jest.fn();render(<AttendanceSessionForm onSaved={saved}/>);
  change('Title','Evening');change('Opens','2026-11-17T10:00');change('Closes','2026-11-17T09:00');submit('Create session');expect(await screen.findByRole('alert')).toHaveTextContent(/Closing time/);
  change('Closes','2026-11-17T11:00');change('Centre latitude','12');change('Centre longitude','77');change('Radius (m)','100');change('Maximum accuracy (m)','20');change('Maximum sample age (seconds)','60');
  data['POST /api/attendance/sessions/']={httpStatus:400};submit('Create session');expect(await screen.findByRole('alert')).toBeVisible();
  delete data['POST /api/attendance/sessions/'];submit('Create session');await screen.findByText('Attendance session created.');expect(saved).toHaveBeenCalled();
  expect(JSON.parse(writes('/api/attendance/sessions/')[0][1].body)).toMatchObject({radius_m:100,centre_latitude:12});
});

test('one-time attendance handles absent and denied location, then retries',async()=>{
  installApi();const saved=jest.fn();render(<AttendanceSubmit session={session} onSaved={saved}/>);
  Object.defineProperty(navigator,'geolocation',{configurable:true,value:undefined});fireEvent.click(screen.getByText('Submit one-time location attendance'));expect(await screen.findByRole('alert')).toHaveTextContent(/unavailable/);
  Object.defineProperty(navigator,'geolocation',{configurable:true,value:{getCurrentPosition:jest.fn((ok,fail)=>fail())}});fireEvent.click(screen.getByText('Submit one-time location attendance'));expect(await screen.findByRole('alert')).toHaveTextContent(/denied/);
  navigator.geolocation.getCurrentPosition.mockImplementation(ok=>ok({coords:{latitude:12,longitude:77,accuracy:5},timestamp:Date.now()}));fireEvent.click(screen.getByText('Submit one-time location attendance'));await waitFor(()=>expect(saved).toHaveBeenCalled());
});

test.each(['identity','records'])('attendance displays %s failures',async kind=>{
  installApi();if(kind==='identity')fetch.mockRejectedValue(Error('Offline'));else installApi('STUDENT',{'/api/attendance/sessions/?page=1':Error('Offline')});render(<AttendanceWorkspace/>);expect(await screen.findByRole('alert')).toHaveTextContent('Offline');
});

const deviation={id:1,student:1,rule_title_snapshot:'Quiet hours',weightage_snapshot:'2.50',active:true,remarks:'Synthetic',recorded_at:stamp,recorded_by:2};
test('Warden records/deactivates deviations, retaining failed write feedback',async()=>{
  const data=installApi('WARDEN',{'/api/arin/students/?page=1':{results:[{id:1,name:'Synthetic'}]},'/api/arin/rules/?page=1':{results:[{id:1,title:'Quiet hours',weightage:'2.50'}]},'/api/deviations/?page=1&student=1':{results:[deviation,{...deviation,id:2,active:false,deactivated_at:stamp,deactivated_by:2,deactivation_reason:'Corrected'}]},'/api/deviations/total/?student=1':{active_total:'2.50'}});
  render(<DeviationPanel/>);await screen.findByText(/Active weightage total: Select a student/);await screen.findByRole('option',{name:'Synthetic'});change('Assigned student','1');await screen.findByLabelText('Active rule');await screen.findByRole('option',{name:'Quiet hours · 2.50'});change('Active rule','1');change('Remarks','Observed');
  data['POST /api/deviations/']={httpStatus:400};submit('Record deviation');expect(await screen.findByRole('alert')).toBeVisible();delete data['POST /api/deviations/'];submit('Record deviation');await waitFor(()=>expect(writes('/api/deviations/')).toHaveLength(2));
  change('Deactivation reason','Correction');data['POST /api/deviations/1/deactivate/']={httpStatus:400};submit('Deactivate and retain history');await waitFor(()=>expect(screen.getAllByRole('alert').length).toBeGreaterThan(0));delete data['POST /api/deviations/1/deactivate/'];submit('Deactivate and retain history');await waitFor(()=>expect(writes('/api/deviations/1/deactivate/')).toHaveLength(2));
});

test.each(['identity','choices','totals'])('deviation panel reports %s read failures',async kind=>{
  installApi(kind==='choices'?'WARDEN':'STUDENT',{'/api/arin/students/?page=1':Error('Offline'),'/api/deviations/total/':Error('Offline')});if(kind==='identity')fetch.mockRejectedValue(Error('Offline'));render(<DeviationPanel/>);expect(await screen.findByRole('alert')).toHaveTextContent('Offline');
});
