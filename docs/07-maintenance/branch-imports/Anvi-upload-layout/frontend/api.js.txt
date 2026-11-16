// Owner: Anvi Srinivas | Story: US-01 | Sprint: 1
function getCookie(name) {
  const m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return m ? decodeURIComponent(m[2]) : "";
}

export async function api(path, { method = "GET", body } = {}) {
  if (method !== "GET") await fetch("/api/auth/csrf/", { credentials: "include" });
  const res = await fetch(path, {
    method,
    credentials: "include",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw { status: res.status, ...data };
  return data;
}
