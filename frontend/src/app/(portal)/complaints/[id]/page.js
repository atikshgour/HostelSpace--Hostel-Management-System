/* Owner: Atiksh Gour | US-13,US-14 | Dev sprint 2 | SRS sprint 4 | Reviewer: Anvi Srinivas (pending) */
"use client";
import { useParams } from "next/navigation";
import Screen from "@/features/complaints/ComplaintList";
export default function Page() {
  const { id } = useParams();
  return <Screen detailId={id} />;
}
