// Owner: Atiksh Gour | US-13-16/20 | Integration landing page
import Link from 'next/link';
export default function Dashboard() {
  return <main><h1>HostelSpace</h1><p>Student services</p>
    <Link href="/complaints">Complaints</Link>{' '}
    <Link href="/mess">Mess</Link>{' '}
    <Link href="/fees">Fees</Link></main>;
}
