"use client";
import { Alert, Button } from "@/components/ui";

export default function Error({ reset }) {
  return (
    <main className="p-8 max-w-lg space-y-4">
      <Alert type="error">Something went wrong. Please try again.</Alert>
      <Button onClick={reset}>Try again</Button>
    </main>
  );
}
