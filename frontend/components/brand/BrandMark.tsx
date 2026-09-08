import { ShieldCheck } from "lucide-react";
export function BrandMark({ compact = false }: { compact?: boolean }) {
  return <div className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-accent text-[#071412] shadow-[0_0_28px_rgba(114,200,187,.18)]"><ShieldCheck className="h-5 w-5" strokeWidth={2.4}/></span>{!compact?<span className="text-lg font-semibold tracking-[-0.03em]">GUARD<span className="text-accent"> AI</span></span>:null}</div>;
}
