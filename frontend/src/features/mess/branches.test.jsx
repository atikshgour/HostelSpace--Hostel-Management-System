// US-13/15/16/22 | Staff actions, histories, failed writes and provider UI adapter.
import {act,fireEvent,screen,waitFor,within} from '@testing-library/react';
import MessPanel from './MessPanel';
import FeesPanel from '../fees/FeesPanel';
import ComplaintList from '../complaints/ComplaintList';
import LaundryPanel from '../laundry/LaundryPanel';
import {installApi,portal,change,submit,writes,stamp} from '../../../test-support/fixtures';

jest.mock('next/navigation',()=>{const router={replace:jest.fn(),refresh:jest.fn()};return {useRouter:()=>router,usePathname:()=>global.__testPath || '/dashboard'};});

const option={id:1,name:'Main mess',diet:'Vegetarian',capacity:10,available:2,enrolled:8,active:true,timings:'9–5',description:'Meals',breakfast:'Idli',lunch:'Rice',dinner:'Roti'};
const coupon={id:1,code:'MEAL',active:true,student_name:'Synthetic',valid_from:'2026-11-17',valid_to:'2026-11-18'};
const routes=()=>({'/api/mess/':[{id:1,student_name:'Synthetic',mess_name:'Main mess',option:1,updated_at:stamp}],'/api/mess/coupons/':[coupon,{...coupon,id:2,code:'OLD',active:false}],'/api/mess/options/':[option,{...option,id:2,name:'Full mess',available:0,description:'',breakfast:'',lunch:'',dinner:''},{...option,id:3,name:'One place',available:1},{...option,id:4,name:'Inactive mess',active:false,enrolled:0}],'/api/mess/history/':[{id:1,new_mess:'Main mess',old_mess:'Other',student_name:'Synthetic',occurred_at:stamp},{id:2,new_mess:'Main mess',old_mess:'',occurred_at:stamp}],'/api/choices/users/?role=STUDENT':[{id:1,name:'Synthetic'}]});

test('mess staff create/edit menu, assign student and issue/toggle coupons',async()=>{
  const data=installApi('MESS_STAFF',routes());portal(<MessPanel/>);await screen.findByText('Full mess');
  change('Search enrolments','none');change('Search enrolments','Synthetic');
  fireEvent.click(screen.getByText('Deactivate'));await waitFor(()=>expect(writes('/api/mess/coupons/1/')).toHaveLength(1));
  data['PATCH /api/mess/coupons/2/']={httpStatus:400};fireEvent.click(screen.getByText('Activate'));expect(await screen.findByRole('alert')).toBeVisible();
  fireEvent.click(screen.getByText('+ Add mess option'));change('Mess name','New mess');change('Meal type','Mixed');submit('Save changes');
  await screen.findByText('Mess details updated.');expect(writes('/api/mess/options/')).toHaveLength(1);
  fireEvent.click(screen.getAllByText('Edit menu & capacity')[0]);submit('Save changes');await waitFor(()=>expect(writes('/api/mess/options/1/')).toHaveLength(1));
  await waitFor(()=>expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  fireEvent.click(screen.getByText('Select for student'));change('Student','1');change('Mess option','1');submit('Save changes');
  await waitFor(()=>expect(writes('/api/mess/select/')).toHaveLength(1));await waitFor(()=>expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  fireEvent.click(screen.getByText('+ Issue coupon'));change('Student','1');change('Coupon code','NEW');change('Valid from','2026-11-17');change('Valid until','2026-11-18');submit('Save changes');
  await waitFor(()=>expect(writes('/api/mess/coupons/')).toHaveLength(1));await waitFor(()=>expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  fireEvent.click(screen.getByText('+ Add mess option'));fireEvent.click(screen.getByLabelText('Close dialog'));
});

test.each(['STUDENT','DIRECTOR'])('populated %s mess view preserves read-only scope',async role=>{
  installApi(role,routes());portal(<MessPanel/>);await screen.findByText('Full mess');
  expect(screen.queryByText('+ Add mess option')).not.toBeInTheDocument();
  expect(screen.getByText('Inactive mess')).toBeVisible();
});

test.each(['MESS_STAFF','STUDENT'])('empty %s mess shows useful states',async role=>{
  installApi(role);portal(<MessPanel/>);expect(await screen.findByText(/No mess options have/)).toBeVisible();
});

const fee={id:1,title:'Term fee',amount:'100.00',currency:'INR',status:'Unpaid',due_date:'2026-11-20'};
const attempt={id:'attempt-1',fee:1,provider:'simulation',amount:'100.00',currency:'INR',status:'Pending',created_at:stamp};
test('Director creates a due and reads mixed payment modes',async()=>{
  installApi('DIRECTOR',{'/api/fees/':[fee,{...fee,id:2,title:'Second fee',student_name:'Named',status:'Paid'}],'/api/payments/attempts/':[attempt,{...attempt,id:'attempt-2',provider:'razorpay'}],'/api/choices/users/':[{id:1,name:'Synthetic'}]});portal(<FeesPanel/>);await screen.findByText('Term fee');
  change('Student','1');change('Fee title','New due');change('Amount','20');change('Currency','INR');change('Due date','2026-11-20');submit('Save');await screen.findByText('Changes saved.');expect(writes('/api/fees/')).toHaveLength(1);
});

test.each(['Success','Failed','Cancelled'])('local fee simulation records %s',async outcome=>{
  installApi('STUDENT',{'/api/fees/':[fee,{...fee,id:2,status:'Paid'}],'/api/payments/attempts/':[attempt],'POST /api/payments/initiate/':attempt});portal(<FeesPanel/>);
  fireEvent.click(await screen.findByText('Open test checkout'));fireEvent.click(await screen.findByText(`Simulate ${outcome.toLowerCase()}`));
  expect(await screen.findByText(`Local simulation: ${outcome}. No real payment was made.`)).toBeVisible();
});

test('fee simulation and initiation failures stay visible',async()=>{
  const data=installApi('STUDENT',{'/api/fees/':[fee],'POST /api/payments/initiate/':{httpStatus:400}});portal(<FeesPanel/>);
  fireEvent.click(await screen.findByText('Open test checkout'));expect(await screen.findByRole('alert')).toBeVisible();
  data['POST /api/payments/initiate/']=attempt;data['POST /api/payments/simulate/']={httpStatus:400};
  fireEvent.click(screen.getByText('Open test checkout'));fireEvent.click(await screen.findByText('Simulate success'));expect(await screen.findByRole('alert')).toBeVisible();
});

test('sandbox adapter verifies, reports failure and handles dismissal without live I/O',async()=>{
  let options;
  window.Razorpay=jest.fn(function(value){options=value;this.open=jest.fn();});
  const data=installApi('STUDENT',{'/api/fees/':[fee],'POST /api/payments/initiate/':{...attempt,provider:'razorpay',order_id:'order_test',checkout_key:'rzp_test_synthetic'}});portal(<FeesPanel/>);
  fireEvent.click(await screen.findByText('Open test checkout'));await waitFor(()=>expect(options).toBeDefined());
  await act(()=>options.handler({razorpay_payment_id:'pay_test',razorpay_signature:'synthetic'}));
  expect(screen.getByText(/Sandbox payment verified/)).toBeVisible();
  data['POST /api/payments/verify/']={httpStatus:400};await act(()=>options.handler({}));expect(screen.getByRole('alert')).toBeVisible();
  act(()=>options.modal.ondismiss());expect(screen.getByText(/Checkout closed/)).toBeVisible();delete window.Razorpay;
});

test('checkout script failure is recoverable and loading success opens adapter',async()=>{
  installApi('STUDENT',{'/api/fees/':[fee],'POST /api/payments/initiate/':{...attempt,provider:'razorpay'}});portal(<FeesPanel/>);
  fireEvent.click(await screen.findByText('Open test checkout'));
  await waitFor(()=>expect(document.querySelector('script[src*="checkout.razorpay"]')).not.toBeNull());
  const script=document.querySelector('script[src*="checkout.razorpay"]');fireEvent.error(script);
  expect(await screen.findByRole('alert')).toHaveTextContent(/Unable to load/);script.remove();
  fireEvent.click(screen.getByText('Open test checkout'));await waitFor(()=>expect(document.querySelector('script[src*="checkout.razorpay"]')).not.toBeNull());
  window.Razorpay=jest.fn(function(){this.open=jest.fn();});fireEvent.load(document.querySelector('script[src*="checkout.razorpay"]'));
  await waitFor(()=>expect(window.Razorpay).toHaveBeenCalled());document.querySelector('script[src*="checkout.razorpay"]').remove();delete window.Razorpay;
});

const complaint={id:1,category:'Other',description:'Broken light',student_name:'Synthetic',room_snapshot:'A 101',status:'Open',assigned_to:2,assigned_name:'Repair team',created_at:stamp,transitions:[{id:1,actor:1,to_status:'Open',occurred_at:stamp}]};
test('Director assigns and progresses a complaint',async()=>{
  installApi('DIRECTOR',{'/api/complaints/':[complaint],'/api/choices/users/?role=MAINTENANCE_STAFF':[{id:2,name:'Repair team'}]});portal(<ComplaintList detailId="1"/>);
  await screen.findByLabelText('Maintenance staff');change('Maintenance staff','2');
  fireEvent.submit(screen.getByLabelText('Maintenance staff').closest('form'));
  await waitFor(()=>expect(writes('/api/complaints/1/assign/')).toHaveLength(1));
  change('Next status','In Progress');change('Progress remarks','Repairing');
  fireEvent.submit(screen.getByLabelText('Progress remarks').closest('form'));
  await waitFor(()=>expect(writes('/api/complaints/1/progress/')).toHaveLength(1));
});

test.each([['DIRECTOR','Open'],['MAINTENANCE_STAFF','In Progress'],['DIRECTOR','Resolved'],['STUDENT','Open']])('%s complaint detail in %s state',async(role,status)=>{
  installApi(role,{'/api/complaints/':[{...complaint,status,assigned_to:status==='Open'?null:2,assigned_name:status==='Open'?'':'Repair team'}],'/api/choices/users/?role=MAINTENANCE_STAFF':[{id:2,name:'Repair team'}]});portal(<ComplaintList detailId="1"/>);
  await screen.findByText('Broken light');
  if(role==='DIRECTOR'&&status==='Open'){change('Maintenance staff','2');submit('Save');await waitFor(()=>expect(writes('/api/complaints/1/assign/')).toHaveLength(1));}
  if(role==='MAINTENANCE_STAFF'){change('Next status','Resolved');change('Progress remarks','Done');submit('Save');await waitFor(()=>expect(writes('/api/complaints/1/progress/')).toHaveLength(1));}
});

test('student complaint form, list filters and empty search',async()=>{
  installApi('STUDENT',{'/api/complaints/':[complaint,{...complaint,id:2,status:'Resolved',assigned_name:''}]});portal(<ComplaintList/>);await screen.findByText('Broken light');
  change('Status','All');change('Status','Resolved');change('Search complaints','none');expect(screen.getByText('No complaints found.')).toBeVisible();change('Search complaints','');change('Status','Open');
  fireEvent.click(screen.getByText('+ New complaint'));change('Category','Other');change('Description','Synthetic new');submit('Submit complaint');expect(await screen.findByText(/Complaint submitted/)).toBeVisible();
  fireEvent.click(screen.getByText('+ New complaint'));fireEvent.click(screen.getByLabelText('Close dialog'));
});

const plan={student:1,student_name:'Synthetic',srn:'TEST-1',room:'101',group_number:1,weekday:'Monday',next_dropoff_date:'2026-11-23',next_return_date:'2026-11-26'};
const batches=[{id:1,student_name:'Synthetic',item_count:2,item_details:'Shirts',status:'Received',group_number:1,expected_return_date:'2026-11-20',received_at:stamp}, {id:2,student_name:'Synthetic',item_count:1,item_details:'Towel',status:'Ready',received_at:stamp}, {id:3,student_name:'Synthetic',item_count:1,item_details:'Old',status:'Collected',collected_at:stamp}];
const laundryRoutes=()=>({'/api/laundry/allocations/':[plan],'/api/laundry/records/':batches,'/api/choices/users/':[{id:1,name:'Synthetic'},{id:2,name:'Other'}],'/api/laundry/policy/':{turnaround_days:4}});
test('Laundry Staff saves future policy and receives a batch',async()=>{
  installApi('LAUNDRY_STAFF',laundryRoutes(),'/laundry/handover');portal(<LaundryPanel/>);await waitFor(()=>expect(screen.getByText('Change return time')).toBeEnabled());fireEvent.click(screen.getByText('Change return time'));change('Return after (days)','5');submit('Save');expect(await screen.findByText(/Default return time updated/)).toBeVisible();
  fireEvent.click(screen.getByText('+ Receive clothes'));change('Student','1');change('Item details','Shirts');change('Number of items','2');submit('Record handover');expect(await screen.findByText(/Handover recorded/)).toBeVisible();
  expect(writes('/api/laundry/records/')).toHaveLength(1);
  fireEvent.click(screen.getByText('+ Receive clothes'));fireEvent.click(screen.getByLabelText('Close dialog'));fireEvent.click(screen.getByText('Change return time'));fireEvent.click(screen.getByLabelText('Close dialog'));
});

test('laundry transitions confirm collection, cancel safely and expose failure',async()=>{
  const data=installApi('LAUNDRY_STAFF',laundryRoutes(),'/laundry/handover');portal(<LaundryPanel/>);fireEvent.click(await screen.findByText('Mark ready'));await screen.findByText(/Batch is ready/);
  window.confirm=jest.fn(()=>false);fireEvent.click(screen.getByText('Confirm collection'));expect(writes('/api/laundry/records/2/collect/')).toHaveLength(0);
  window.confirm.mockReturnValue(true);fireEvent.click(screen.getByText('Confirm collection'));await screen.findByText(/Collection confirmed/);
  data['POST /api/laundry/records/1/ready/']={httpStatus:400};fireEvent.click(screen.getByText('Mark ready'));expect(await screen.findByRole('alert')).toBeVisible();
  change('Batch status','Collected');change('Batch status','All');change('Search batches','none');expect(screen.getByText(/No batches match/)).toBeVisible();
});

test.each(['STUDENT','DIRECTOR'])('%s laundry record view handles all statuses',async role=>{
  installApi(role,laundryRoutes());portal(<LaundryPanel/>);await screen.findByText('Shirts',{exact:false});change('Batch status','All');expect(screen.getByText('Old',{exact:false})).toBeVisible();
});

test('laundry timetable filters populated schedules',async()=>{
  installApi('LAUNDRY_STAFF',laundryRoutes(),'/laundry/manage');portal(<LaundryPanel/>);await screen.findByText('TEST-1 · Room 101');change('Search schedule','none');expect(screen.queryByText('TEST-1 · Room 101')).not.toBeInTheDocument();
});
