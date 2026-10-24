import { Skeleton } from "@/components/ui/skeleton";

export default function SocLoading() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-48 bg-zinc-800" />
        <Skeleton className="h-8 w-32 bg-zinc-800" />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Skeleton className="h-32 rounded-xl bg-zinc-800" />
        <Skeleton className="h-32 rounded-xl bg-zinc-800" />
        <Skeleton className="h-32 rounded-xl bg-zinc-800" />
      </div>
      <Skeleton className="h-[400px] w-full rounded-xl bg-zinc-800" />
    </div>
  );
}
