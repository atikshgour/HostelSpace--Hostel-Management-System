/* Arin Singh | US-07 | Sprint 4. */
export class ApiError extends Error {
  constructor(status, payload = {}) {
    super(payload.message || "Request failed.");
    this.name = "ApiError";
    this.status = status;
    this.fields = payload.fields || {};
  }
}

export async function request(path, { method = "GET", body } = {}) {
  if (!path.startsWith("/api/") || path.startsWith("//")) throw new Error("Only same-origin API paths are allowed.");
  const headers = { Accept: "application/json" };
  if (method !== "GET") {
    const bootstrap = await fetch("/api/auth/csrf/", { credentials: "same-origin", cache: "no-store" });
    const tokenPayload = await bootstrap.json().catch(() => ({}));
    if (!bootstrap.ok || !tokenPayload.csrfToken) throw new ApiError(bootstrap.status, { message: "Unable to initialize a secure request." });
    headers["X-CSRFToken"] = tokenPayload.csrfToken;
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(path, {
    method, headers, credentials: "same-origin", cache: "no-store",
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new ApiError(response.status, payload);
  return payload;
}

export const getIdentity = () => request("/api/auth/me/");
export const listSessions = (page = 1) => request(`/api/attendance/sessions/?page=${page}`);
export const createSession = (body) => request("/api/attendance/sessions/", { method: "POST", body });
export const submitAttendance = (body) => request("/api/attendance/submit/", { method: "POST", body });
export const listAttendance = (page = 1) => request(`/api/attendance/history/?page=${page}`);
