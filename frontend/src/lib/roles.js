/* Owner: Anvi Srinivas | US-17,US-01 | Dev sprint 1 | SRS sprint 1 | Reviewer: Arin Singh (pending) */
export const roleLabel = (role = "") =>
  role === "DIRECTOR"
    ? "Admin"
    : role
        .toLowerCase()
        .replaceAll("_", " ")
        .replace(/\b\w/g, (c) => c.toUpperCase());
export const menus = {
  STUDENT: [
    ["Dashboard", "/dashboard"],
    ["My profile", "/profile"],
    ["Announcements & info", "/information"],
    ["Study room", "/study-room"],
    ["Laundry", "/laundry"],
    ["Leave requests", "/leave"],
    ["Attendance", "/attendance"],
    ["Deviation history", "/deviations"],
    ["Complaints", "/complaints"],
    ["Mess & coupons", "/mess"],
    ["Fees & payments", "/fees"],
  ],
  WARDEN: [
    ["Dashboard", "/dashboard"],
    ["Leave review", "/leave/review"],
    ["Attendance sessions", "/attendance/manage"],
    ["Deviation records", "/deviations/manage"],
    ["People & accounts", "/director/users"],
    ["Laundry overview", "/laundry/manage"],
    ["Announcements & rules", "/information/manage"],
    ["Study room", "/study-room/manage"],
  ],
  CHIEF_WARDEN: [
    ["Dashboard", "/dashboard"],
    ["Escalated leave", "/leave/review"],
    ["Attendance", "/attendance"],
    ["Deviation records", "/deviations/manage"],
  ],
  DIRECTOR: [
    ["Dashboard", "/dashboard"],
    ["Reports", "/director"],
    ["Users & assignments", "/director/users"],
    ["Settings", "/director/settings"],
    ["Content management", "/information/manage"],
    ["Study room", "/study-room/manage"],
    ["Complaints", "/complaints/manage"],
    ["Fees", "/fees"],
  ],
  LAUNDRY_STAFF: [
    ["Dashboard", "/dashboard"],
    ["Laundry records", "/laundry/handover"],
    ["Group schedule", "/laundry/manage"],
  ],
  MAINTENANCE_STAFF: [
    ["Dashboard", "/dashboard"],
    ["Assigned complaints", "/complaints/manage"],
  ],
  MESS_STAFF: [
    ["Dashboard", "/dashboard"],
    ["Mess & coupons", "/mess/manage"],
  ],
  CONTENT_STAFF: [
    ["Dashboard", "/dashboard"],
    ["Content management", "/information/manage"],
    ["Study room", "/study-room/manage"],
  ],
};

export function navGroup(url) {
  if (url === "/dashboard") return "Overview";
  if (["/profile", "/director/users", "/director/settings"].includes(url))
    return "People & account";
  if (
    url.includes("leave") ||
    url.includes("attendance") ||
    url.includes("deviations") ||
    url.includes("complaints")
  )
    return "Requests & records";
  if (url.startsWith("/director")) return "Administration";
  return "Hostel services";
}
