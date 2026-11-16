/* Owner: Anvi Srinivas | US-17,US-01 | Dev sprint 1 | SRS sprint 1 | Reviewer: Arin Singh (pending) */
export class ApiError extends Error {
  constructor(status, payload = {}) {
    super(payload.message || "Request failed. Please retry.");
    this.status = status;
    this.fields = payload.fields || {};
  }
}
export async function api(path, { method = "GET", body } = {}) {
  if (!path.startsWith("/api/"))
    throw new Error("Same-origin API path required.");
  const headers = { Accept: "application/json" };
  if (method !== "GET") {
    const r = await fetch("/api/auth/csrf/", {
      credentials: "same-origin",
      cache: "no-store",
    });
    const data = await r.json();
    if (!r.ok || !data.csrfToken) throw new ApiError(r.status, data);
    headers["X-CSRFToken"] = data.csrfToken;
    headers["Content-Type"] = "application/json";
  }
  const r = await fetch(path, {
    method,
    headers,
    credentials: "same-origin",
    cache: "no-store",
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new ApiError(r.status, data);
  return data;
}
export async function all(path) {
  let next = path,
    rows = [];
  while (next) {
    const data = await api(next);
    if (!Array.isArray(data.results)) return data;
    rows.push(...data.results);
    next = data.next
      ? new URL(
          data.next,
          typeof window === "undefined"
            ? "http://localhost"
            : window.location.origin,
        ).pathname +
        new URL(
          data.next,
          typeof window === "undefined"
            ? "http://localhost"
            : window.location.origin,
        ).search
      : null;
  }
  return rows;
}
