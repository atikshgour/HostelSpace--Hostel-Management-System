"use client";
import { useParams } from "next/navigation";
import Workspace from "@/features/leave/LeaveList";
export default function LeaveDetailPage(){ const { id }=useParams(); return <Workspace detailId={id}/>; }
