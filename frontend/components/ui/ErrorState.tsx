import { ShieldAlert } from "lucide-react";

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3">
      <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-rose-300" />
      <div>
        <p className="text-sm font-medium text-rose-200">GUARD backend is currently unavailable.</p>
        <p className="mt-1 text-xs text-rose-200/80">{message}</p>
      </div>
    </div>
  );
}
