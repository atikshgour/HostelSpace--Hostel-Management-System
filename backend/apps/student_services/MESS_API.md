# FR-08 / US-15 mess contract
Owner: Atiksh Gour; reviewer: Anvi Srinivas (pending).

Students read only their current allocation/coupons/history. Mess Staff maintain
allocations and coupons; Director has read-only oversight. Wardens cannot access
this module. All requests require active sessions; writes require CSRF.
`GET /api/mess/`, `GET /api/mess/coupons/` (student date/active filter),
`GET/POST /api/mess/options/`, `PATCH /api/mess/options/{id}/`,
`POST /api/mess/select/` with `{student,option}` (Mess Staff only),
`POST /api/mess/coupons/`, `PATCH /api/mess/coupons/{id}/`,
`GET /api/mess/history/`. Coupon ranges, capacity and active-student checks are
server-enforced. Allocation changes append immutable actor/time/history events.
