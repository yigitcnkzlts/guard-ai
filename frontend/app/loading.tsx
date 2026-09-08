import { MetricSkeleton, TableSkeleton } from "@/components/ui/Skeleton";

export default function Loading(){return <div className="mx-auto max-w-[1180px] space-y-7" role="status" aria-label="Loading page"><div className="h-9 w-72 animate-pulse rounded-lg bg-white/10"/><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{Array.from({length:6}).map((_,i)=><MetricSkeleton key={i}/>)}</div><div className="rounded-xl border border-border bg-surface p-5"><TableSkeleton/></div><span className="sr-only">Loading…</span></div>}
