/* Owner: Anvi Srinivas | US-17,US-21 | Dev sprint 1; 4–6 | SRS sprint 1; 6 | Reviewer: Arin Singh (pending) */
export default function EmptyState({ children = "No records yet." }) {
  return <p className="hs-empty">{children}</p>;
}
