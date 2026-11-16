/* Owner: Anvi Srinivas | US-17,US-01 | Dev sprint 1 | SRS sprint 1 | Reviewer: Arin Singh (pending) */
export const dateTime = (value) =>
  value ? new Date(value).toLocaleString("en-IN") : "—";
export const money = (value, currency = "INR") =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency }).format(
    Number(value),
  );
