"use client";
export default function Error({ reset }) {
  return (
    <section className="hs-card">
      <h1>Unable to open this page</h1>
      <p>Please retry. If the issue persists, check the backend connection.</p>
      <button className="hs-button" onClick={reset}>
        Try again
      </button>
    </section>
  );
}
