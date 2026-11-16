"use client";
/* Arin Singh | US-05/06 | Sprint 3. Complete leave workspace in an existing assigned file. */
import { useEffect, useState } from "react";
import { decideLeave, getIdentity, getLeave, listLeaves, submitLeave } from "./api";

const ui = { page:{maxWidth:960,margin:"0 auto",padding:24}, card:{border:"1px solid #cbd5e1",borderRadius:12,padding:20,margin:"16px 0",background:"#fff"}, row:{display:"flex",gap:12,flexWrap:"wrap",alignItems:"center"}, field:{display:"grid",gap:6,margin:"12px 0",minWidth:220}, input:{minHeight:42,padding:9,border:"1px solid #94a3b8",borderRadius:8,font:"inherit"}, button:{minHeight:42,padding:"8px 14px",border:"1px solid #1d4ed8",borderRadius:8,background:"#fff",color:"#1d4ed8",cursor:"pointer"}, error:{padding:12,borderLeft:"4px solid #b91c1c",background:"#fef2f2"} };

export function ErrorMessage({ error }) { return error ? <div role="alert" style={ui.error}><strong>{error.message}</strong>{Object.entries(error.fields || {}).map(([key,value])=><p key={key}>{key}: {Array.isArray(value)?value.join(" "):String(value)}</p>)}</div> : null; }
function Field({ label, children, ...props }) { return <label style={ui.field}><span>{label}</span>{children || <input style={ui.input} {...props}/>}</label>; }
function Pager({ page, data, setPage }) { return <nav aria-label="Leave pages" style={ui.row}><button style={ui.button} disabled={page===1} onClick={()=>setPage(page-1)}>Previous</button><span>Page {page}</span><button style={ui.button} disabled={!data?.next} onClick={()=>setPage(page+1)}>Next</button></nav>; }

export function LeaveForm({ onSaved }) {
  const [busy,setBusy]=useState(false), [error,setError]=useState(null), [message,setMessage]=useState("");
  async function submit(event) {
    event.preventDefault(); const form=event.currentTarget; const body=Object.fromEntries(new FormData(form));
    setError(null); setMessage("");
    if (body.end_date < body.start_date) { setError(new Error("End date must be on or after start date.")); return; }
    setBusy(true);
    try { await submitLeave(body); form.reset(); setMessage("Leave request submitted with Pending status."); onSaved(); }
    catch (failure) { setError(failure); } finally { setBusy(false); }
  }
  return <section style={ui.card}><h2>Apply for leave</h2><form onSubmit={submit}><div style={ui.row}><Field label="Start date" name="start_date" type="date" required/><Field label="End date" name="end_date" type="date" required/></div><Field label="Reason"><textarea style={{...ui.input,minHeight:96}} name="reason" maxLength={2000} required/></Field><button style={ui.button} disabled={busy}>{busy?"Submitting…":"Submit leave"}</button><ErrorMessage error={error}/><p role="status">{message}</p></form></section>;
}

export function LeaveHistory({ transitions=[] }) { return <ol>{transitions.map(item=><li key={item.id}><strong>{item.from_status || "New"} → {item.to_status}</strong><p>{item.remarks}</p><small>Actor {item.actor} · {new Date(item.occurred_at).toLocaleString()}</small></li>)}</ol>; }

export function LeaveReviewPanel({ row, role, onSaved }) {
  const allowed=(row.status==="Pending" && role==="WARDEN") || (row.status==="Escalated" && role==="CHIEF_WARDEN");
  const [decision,setDecision]=useState("Approved"), [busy,setBusy]=useState(false), [error,setError]=useState(null);
  if (!allowed) return null;
  async function submit(event) { event.preventDefault(); setBusy(true); setError(null); try { await decideLeave(row.id,{decision,remarks:new FormData(event.currentTarget).get("remarks")}); onSaved(); } catch(failure){ setError(failure); } finally { setBusy(false); } }
  return <form onSubmit={submit}><Field label="Decision"><select style={ui.input} value={decision} onChange={event=>setDecision(event.target.value)}><option>Approved</option><option>Rejected</option>{role==="WARDEN"?<option>Escalated</option>:null}</select></Field><Field label="Decision remarks"><textarea style={{...ui.input,minHeight:80}} name="remarks" maxLength={2000} required/></Field><button style={ui.button} disabled={busy}>{busy?"Saving…":"Save decision"}</button><ErrorMessage error={error}/></form>;
}

export default function LeaveWorkspace({ detailId=null }) {
  const [identity,setIdentity]=useState({loading:true}), [page,setPage]=useState(1), [data,setData]=useState({results:[]}), [error,setError]=useState(null), [revision,setRevision]=useState(0);
  useEffect(()=>{ let live=true; getIdentity().then(user=>live&&setIdentity({loading:false,user})).catch(error=>live&&setIdentity({loading:false,error})); return()=>{live=false}; },[]);
  useEffect(()=>{ let live=true; setError(null); (detailId?getLeave(detailId).then(row=>({results:[row]})):listLeaves(page)).then(value=>live&&setData(value)).catch(failure=>live&&setError(failure)); return()=>{live=false}; },[detailId,page,revision]);
  if (identity.loading) return <main style={ui.page}><p role="status">Checking session…</p></main>;
  if (identity.error) return <main style={ui.page}><ErrorMessage error={identity.error}/></main>;
  const role=identity.user?.role, refresh=()=>setRevision(value=>value+1);
  return <main style={ui.page}><h1>Leave requests</h1>{role==="STUDENT"&&!detailId?<LeaveForm onSaved={refresh}/>:null}<ErrorMessage error={error}/>{!data.results?.length?<p>No leave records.</p>:data.results.map(row=><article style={ui.card} key={row.id}><h2>{row.start_date} to {row.end_date} · {row.status}</h2><p>{row.reason}</p><p>Request {row.id} · Student {row.student}</p><LeaveHistory transitions={row.transitions}/><LeaveReviewPanel row={row} role={role} onSaved={refresh}/>{!detailId?<a href={`/leave/${row.id}`}>Open request</a>:null}</article>)}{!detailId?<Pager page={page} data={data} setPage={setPage}/>:null}</main>;
}
