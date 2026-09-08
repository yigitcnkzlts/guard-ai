"use client";
import { Download } from "lucide-react";
export function PrintButton(){return <button onClick={()=>window.print()} className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm"><Download className="h-4 w-4"/>Export PDF</button>}
