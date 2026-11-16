/* Owner: Anvi Srinivas | US-17,US-21 | Dev sprint 1; 4–6 | SRS sprint 1; 6 | Reviewer: Arin Singh (pending) */
export default function Button({ children, variant = "", ...props }) {
  return (
    <button className={`hs-button ${variant}`} {...props}>
      {children}
    </button>
  );
}
