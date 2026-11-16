/* Owner: Anvi Srinivas | US-17,US-21 | Dev sprint 1; 4–6 | SRS sprint 1; 6 | Reviewer: Arin Singh (pending) */
export default function PageHeader({ title, description, children }) {
  return (
    <header className="hs-header hs-row">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {children}
    </header>
  );
}
