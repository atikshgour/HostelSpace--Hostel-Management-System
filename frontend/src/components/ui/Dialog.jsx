"use client";
import { useEffect, useRef, useId } from "react";
import Button from "./Button";
export default function Dialog({ title, onClose, children, className = "" }) {
  const ref = useRef(null),
    id = useId();
  useEffect(() => {
    const d = ref.current;
    d.showModal();
    const before = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = before;
      d.close();
    };
  }, []);
  return (
    <dialog
      className={`hs-dialog ${className}`}
      ref={ref}
      aria-labelledby={id}
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
      onClick={(e) => {
        if (e.target === ref.current) onClose();
      }}
    >
      <div className="hs-dialog-head">
        <h2 id={id}>{title}</h2>
        <Button type="button" aria-label="Close dialog" onClick={onClose}>
          Close
        </Button>
      </div>
      {children}
    </dialog>
  );
}
