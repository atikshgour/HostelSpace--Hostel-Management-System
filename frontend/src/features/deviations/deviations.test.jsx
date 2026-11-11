import { render, screen } from "@testing-library/react";
import DeviationPanel from "./DeviationPanel";

function response(body, status = 200) { return { ok: status < 400, status, json: async () => body }; }
test("student receives read-only history and server-calculated active total", async () => {
  global.fetch = jest.fn(async url => {
    if (url === "/api/auth/me/") return response({ id: "s1", role: "STUDENT" });
    if (String(url).startsWith("/api/deviations/total/")) return response({ student: "s1", active_total: "2.50" });
    if (String(url).startsWith("/api/deviations/")) return response({ next: null, results: [{ id: "d1", student: "s1", rule_title_snapshot: "Late return", weightage_snapshot: "2.50", remarks: "Observed", recorded_by: "w1", recorded_at: "2026-09-28T10:00:00Z", active: true }] });
    return response({}, 404);
  });
  render(<DeviationPanel />);
  expect(await screen.findByText(/Active weightage total: 2.50/)).toBeInTheDocument();
  expect(screen.getByText(/Late return · 2.50/)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /Record deviation/ })).not.toBeInTheDocument();
});
