/* Arin Singh | US-05/06 | Sprint 3. */
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
export const listLeaves = (page = 1) => request(`/api/leaves/?page=${page}`);
export const getLeave = (id) => request(`/api/leaves/${encodeURIComponent(id)}/`);
export const submitLeave = (body) => request("/api/leaves/", { method: "POST", body });
export const decideLeave = (id, body) => request(`/api/leaves/${encodeURIComponent(id)}/decision/`, { method: "POST", body });
