import Link from 'next/link';
// Owner: Atiksh | US-20 foundation | Sprint 1
export default function Home() {
  return <main className="hs-container"><section className="hs-card">
    <h1>HostelSpace</h1>
    <p>Student services are available. Additional team modules are being integrated.</p>
    <Link href="/login">Sign in to student services</Link>
  </section></main>;
}
