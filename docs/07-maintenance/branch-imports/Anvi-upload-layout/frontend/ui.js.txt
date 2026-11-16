// Shared UI components (US-21). Use these for all forms and states.

export function Alert({ type = "error", children }) {
  if (!children) return null;
  return (
    <div role={type === "error" ? "alert" : "status"} className={`hs-alert hs-alert-${type}`}>
      {children}
    </div>
  );
}

export function FormField({ label, id, error, type = "text", value, onChange, ...rest }) {
  return (
    <div>
      <label htmlFor={id} className="hs-label">{label}</label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        className="hs-input"
        aria-invalid={error ? "true" : "false"}
        aria-describedby={error ? `${id}-error` : undefined}
        {...rest}
      />
      {error && <p id={`${id}-error`} className="hs-field-error">{error}</p>}
    </div>
  );
}

export function Button({ loading, loadingText = "Please wait...", variant = "primary", children, ...rest }) {
  const cls = variant === "secondary" ? "hs-btn hs-btn-secondary" : "hs-btn";
  return (
    <button className={cls} disabled={loading || rest.disabled} {...rest}>
      {loading ? loadingText : children}
    </button>
  );
}

export function Loading({ text = "Loading..." }) {
  return (
    <div role="status" className="flex items-center gap-2 p-4">
      <span className="hs-spinner" aria-hidden="true" />
      <span>{text}</span>
    </div>
  );
}

export function EmptyState({ title, message, action }) {
  return (
    <div className="hs-card text-center py-8">
      <p className="font-semibold">{title}</p>
      {message && <p className="mt-1" style={{ color: "var(--hs-muted)" }}>{message}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function StatusBadge({ status, tone = "warn" }) {
  return <span className={`hs-badge hs-badge-${tone}`}>{status}</span>;
}
