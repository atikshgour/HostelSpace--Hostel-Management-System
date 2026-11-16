// Owner: Atiksh Gour | US-16 | Sprint 5 | Reviewer: Anvi Srinivas
import Link from 'next/link';
export default function FeeResultPage() {
  return <main className="hs-container"><h1>Payment result</h1>
    <p>Open your fees to view the server verified status.</p><Link href="/fees">View fees</Link></main>;
}
