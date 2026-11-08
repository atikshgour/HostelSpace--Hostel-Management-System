// Owner: Atiksh Gour | US-14 | Sprint 4 | Reviewer: Anvi Srinivas
import { all, api } from '@/lib/api';

export const listComplaints = (page = 1) => api(`/api/complaints/?page=${page}`);
export const listMaintenanceStaff = () => all('/api/choices/users/?role=MAINTENANCE_STAFF');
export const assignComplaint = (id, body) => api(`/api/complaints/${id}/assign/`, {
  method: 'POST', body: { assigned_to: body.assigned_to },
});
export const advanceComplaint = (id, body) => api(`/api/complaints/${id}/progress/`, {
  method: 'POST', body: { status: body.status, remarks: body.remarks },
});
