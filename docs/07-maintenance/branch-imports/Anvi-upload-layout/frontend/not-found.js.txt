import { EmptyState } from "@/components/ui";

export default function NotFound() {
  return (
    <main className="p-8 max-w-lg">
      <EmptyState title="Page not found" message="The page you are looking for does not exist."
        action={<a href="/dashboard" className="underline">Go to dashboard</a>} />
    </main>
  );
}
