/* Owner: Anvi Srinivas | US-17,US-21 | Dev sprint 1; 4–6 | SRS sprint 1; 6 | Reviewer: Arin Singh (pending) */
"use client";
import Button from "./Button";
export default function ConfirmDialog({
  title,
  children,
  onConfirm,
  onCancel,
}) {
  return (
    <div className="hs-modal">
      <section
        className="hs-card"
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <h2>{title}</h2>
        {children}
        <div className="hs-actions">
          <Button variant="primary" onClick={onConfirm}>
            Confirm
          </Button>
          <Button onClick={onCancel}>Cancel</Button>
        </div>
      </section>
    </div>
  );
}
