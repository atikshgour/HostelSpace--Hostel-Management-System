/* Owner: Anvi Srinivas | US-17,US-21 | Dev sprint 1; 4–6 | SRS sprint 1; 6 | Reviewer: Arin Singh (pending) */
import { dateTime } from "@/lib/format";
export default function HistoryTimeline({ items = [] }) {
  return (
    <ol className="hs-timeline">
      {items.map((x) => (
        <li key={x.id}>
          <strong>
            {x.from_status || "New"} → {x.to_status}
          </strong>
          <p>{x.remarks}</p>
          <small className="hs-muted">
            Actor {x.actor} · {dateTime(x.occurred_at)}
          </small>
        </li>
      ))}
    </ol>
  );
}
