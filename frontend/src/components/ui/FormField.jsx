/* Owner: Anvi Srinivas | US-17,US-21 | Dev sprint 1; 4–6 | SRS sprint 1; 6 | Reviewer: Arin Singh (pending) */
export default function FormField({ label, error, children, ...props }) {
  return (
    <label className="hs-field">
      <span>{label}</span>
      {children || <input {...props} />}{" "}
      {error ? <span role="alert">{error}</span> : null}
    </label>
  );
}
