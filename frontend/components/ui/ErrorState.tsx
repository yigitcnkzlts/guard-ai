import { ShieldAlert } from "lucide-react";

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex items-start gap-3 rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3">
      <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-rose-300" />
      <div>
        <p className="text-sm font-medium text-rose-200">Live service is temporarily unavailable.</p>
        <p className="mt-1 text-xs text-rose-200/80">{message}</p>
        {onRetry ? <button type="button" onClick={onRetry} className="mt-3 rounded-md border border-rose-300/30 px-3 py-1.5 text-xs font-semibold text-rose-100">Try again</button> : null}
      </div>
    </div>
  );
}
