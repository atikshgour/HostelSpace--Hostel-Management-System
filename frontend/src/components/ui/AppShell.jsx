/* Owner: Anvi Srinivas | US-17,US-21 | Dev sprint 1; 4–6 | SRS sprint 1; 6 | Reviewer: Arin Singh (pending) */
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState, useRef } from "react";
import { api, all } from "@/lib/api";
import { menus, roleLabel, navGroup } from "@/lib/roles";
import Button from "./Button";
import FormField from "./FormField";
const Identity = createContext(null);
export const useIdentity = () => useContext(Identity);
export function ErrorMessage({ error }) {
  return error ? (
    <div className="hs-error" role="alert">
      <strong>{error.message}</strong>
      {Object.entries(error.fields || {}).map(([k, v]) => (
        <p key={k}>
          {k}: {Array.isArray(v) ? v.join(" ") : String(v)}
        </p>
      ))}
    </div>
  ) : null;
}
export function useResource(paths) {
  const [data, setData] = useState(null),
    [error, setError] = useState(null),
    [revision, setRevision] = useState(0);
  const key = JSON.stringify(paths);
  useEffect(() => {
    let live = true;
    setError(null);
    Promise.all(JSON.parse(key).map((p) => (p ? all(p) : Promise.resolve([]))))
      .then((x) => live && setData(x))
      .catch((e) => live && setError(e));
    return () => {
      live = false;
    };
  }, [key, revision]);
  return { data, error, refresh: () => setRevision((x) => x + 1) };
}
export function ResourceForm({
  title,
  fields,
  onSave,
  initial = {},
  button = "Save",
  onCancel,
  successMessage = "Changes saved.",
}) {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(null),
    [message, setMessage] = useState("");
  async function submit(e) {
    e.preventDefault();
    let form = e.currentTarget;
    const fd = new FormData(form),
      body = {};
    for (const f of fields) {
      let v = fd.get(f.name);
      if (f.type === "checkbox") v = fd.has(f.name);
      if (v === "" && f.nullable) {
        body[f.name] = null;
        continue;
      }
      if (v === "" && f.optional) continue;
      if (f.type === "number" && v !== "") v = Number(v);
      body[f.name] = v;
    }
    setBusy(true);
    setError(null);
    setMessage("");
    try {
      await onSave(body);
      setMessage(successMessage);
      if (!Object.keys(initial).length) form.reset();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form method="post" onSubmit={submit}>
      <h2>{title}</h2>
      {fields.map((f) => (
        <FormField key={f.name} label={f.label}>
          {f.options ? (
            <select
              name={f.name}
              required={!f.optional}
              defaultValue={initial[f.name] ?? ""}
            >
              <option value="">Select…</option>
              {f.options.map((x) => (
                <option key={x.value ?? x} value={x.value ?? x}>
                  {x.label ?? x}
                </option>
              ))}
            </select>
          ) : f.type === "textarea" ? (
            <textarea
              name={f.name}
              required={!f.optional}
              maxLength={f.maxLength || 3000}
              defaultValue={initial[f.name] ?? ""}
            />
          ) : (
            <input
              className={f.type === "checkbox" ? "check" : ""}
              name={f.name}
              type={f.type || "text"}
              required={!f.optional && f.type !== "checkbox"}
              min={f.min}
              max={f.max}
              maxLength={f.maxLength || 500}
              step={f.step}
              defaultValue={
                f.type === "checkbox" ? undefined : (initial[f.name] ?? "")
              }
              defaultChecked={
                f.type === "checkbox" ? Boolean(initial[f.name]) : undefined
              }
            />
          )}
        </FormField>
      ))}
      <ErrorMessage error={error} />
      {message ? (
        <p role="status" className="hs-success">
          {message}
        </p>
      ) : null}
      <div className="hs-actions">
        <Button variant="primary" disabled={busy}>
          {busy ? "Saving…" : button}
        </Button>
        {onCancel ? (
          <Button type="button" onClick={onCancel}>
            Cancel edit
          </Button>
        ) : null}
      </div>
    </form>
  );
}
export default function AppShell({ children }) {
  const [user, setUser] = useState(null),
    [error, setError] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [mobile, setMobile] = useState(false);
  useEffect(() => {
    const media = window.matchMedia("(max-width: 800px)");
    const update = () => {
      setMobile(media.matches);
      if (!media.matches) setMenuOpen(false);
    };
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  const menuRef = useRef(null),
    triggerRef = useRef(null);
  const path = usePathname(),
    router = useRouter();
  useEffect(() => {
    let live = true;
    api("/api/auth/me/")
      .then((u) => live && setUser(u))
      .catch((e) => {
        if (e.status === 403 || e.status === 401) router.replace("/login");
        else if (live) setError(e);
      });
    return () => {
      live = false;
    };
  }, [router]);
  useEffect(() => {
    setMenuOpen(false);
  }, [path]);
  useEffect(() => {
    if (!menuOpen) return;
    const old = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const root = menuRef.current;
    root?.querySelector("button,a")?.focus();
    function key(e) {
      if (e.key === "Escape") {
        setMenuOpen(false);
        triggerRef.current?.focus();
      }
      if (e.key === "Tab") {
        const controls = [...root.querySelectorAll("a,button")].filter(
          (x) => x.getClientRects().length,
        );
        const first = controls[0],
          last = controls.at(-1);
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    }
    document.addEventListener("keydown", key);
    return () => {
      document.body.style.overflow = old;
      document.removeEventListener("keydown", key);
    };
  }, [menuOpen]);
  async function logout() {
    try {
      await api("/api/auth/logout/", { method: "POST", body: {} });
      router.replace("/login");
      router.refresh();
    } catch (e) {
      setError(e);
    }
  }
  if (!user)
    return (
      <main className="hs-container">
        <p role="status">Checking your session…</p>
        <ErrorMessage error={error} />
      </main>
    );
  return (
    <Identity.Provider value={user}>
      <a className="hs-skip" href="#content">
        Skip to content
      </a>
      {menuOpen ? (
        <button
          className="hs-nav-overlay"
          aria-label="Close navigation"
          onClick={() => {
            setMenuOpen(false);
            triggerRef.current?.focus();
          }}
          tabIndex={-1}
        />
      ) : null}
      <aside
        ref={menuRef}
        id="main-menu"
        inert={mobile && !menuOpen ? true : undefined}
        className={`hs-sidebar ${menuOpen ? "is-open" : ""}`}
      >
        <div className="hs-row">
          <Link className="hs-brand" href="/dashboard">
            <span className="hs-logo">H</span>HostelSpace
          </Link>
          <button
            className="hs-mobile-close hs-button"
            aria-label="Close navigation menu"
            onClick={() => {
              setMenuOpen(false);
              triggerRef.current?.focus();
            }}
          >
            Close
          </button>
        </div>
        <p className="hs-workspace-label">{roleLabel(user.role)} workspace</p>
        <nav className="hs-nav" aria-label="Main navigation">
          {[
            ...new Set((menus[user.role] || []).map((x) => navGroup(x[1]))),
          ].map((group) => (
            <div key={group} className="hs-nav-group">
              <p>{group}</p>
              {(menus[user.role] || [])
                .filter((x) => navGroup(x[1]) === group)
                .map(([name, url]) => (
                  <Link
                    className={path === url ? "current" : ""}
                    aria-current={path === url ? "page" : undefined}
                    href={url}
                    key={url}
                  >
                    <span className="hs-nav-mark" aria-hidden="true">
                      <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.6"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        {url.includes("laundry") ? (
                          <>
                            <rect x="4" y="2" width="16" height="20" rx="2" />
                            <circle cx="12" cy="14" r="5" />
                            <path d="M7 6h1m3 0h6" />
                          </>
                        ) : url.includes("users") ? (
                          <>
                            <circle cx="9" cy="7" r="3" />
                            <path d="M2 21v-2a7 7 0 0 1 14 0v2m1-17a3 3 0 0 1 0 6m2 4a6 6 0 0 1 3 5v2" />
                          </>
                        ) : url.includes("mess") ? (
                          <>
                            <path d="M5 2v7m4-7v7M3 2v5a4 4 0 0 0 8 0V2M7 11v11m12 0V2c-4 3-4 10 0 10" />
                          </>
                        ) : url.includes("leave") ? (
                          <>
                            <path d="M4 20 20 4M8 4h12v12" />
                          </>
                        ) : (
                          <>
                            <rect x="3" y="3" width="18" height="18" rx="2" />
                            <path d="M7 8h10M7 12h10M7 16h6" />
                          </>
                        )}
                      </svg>
                    </span>
                    {name}
                  </Link>
                ))}
            </div>
          ))}
        </nav>
        <div className="hs-sidebar-note">
          One place for everyday hostel life.
        </div>
      </aside>
      <div className="hs-portal">
        <header className="hs-topbar">
          <button
            ref={triggerRef}
            className="hs-menu-trigger hs-button"
            aria-label="Open navigation menu"
            aria-expanded={menuOpen}
            aria-controls="main-menu"
            onClick={() => setMenuOpen(true)}
          >
            ☰ Menu
          </button>
          <span className="hs-muted breadcrumb">
            HostelSpace /{" "}
            {(menus[user.role] || []).find((x) => x[1] === path)?.[0] ||
              "Workspace"}
          </span>
          <div className="hs-actions">
            <span className="hs-avatar">
              {user.name.slice(0, 2).toUpperCase()}
            </span>
            <span>
              {user.name}
              <br />
              <small className="hs-muted">{roleLabel(user.role)}</small>
            </span>
            <Button onClick={logout}>Sign out</Button>
          </div>
        </header>
        <div
          className="hs-content"
          id="content"
          inert={mobile && menuOpen ? true : undefined}
        >
          <ErrorMessage error={error} />
          {children}
        </div>
      </div>
    </Identity.Provider>
  );
}
