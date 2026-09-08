"use client";
import { ShieldAlert } from "lucide-react";
import Link from "next/link";

export default function ErrorPage({reset}:{error:Error&{digest?:string};reset:()=>void}){return <div className="mx-auto grid min-h-[55vh] max-w-xl place-items-center text-center"><div><span className="mx-auto grid h-12 w-12 place-items-center rounded-xl bg-rose-400/10 text-rose-300"><ShieldAlert/></span><h1 className="mt-5 text-2xl font-semibold">This page could not be loaded</h1><p className="mt-2 text-sm text-muted">Your data is safe. Retry the page or return to the overview.</p><div className="mt-6 flex justify-center gap-3"><button onClick={reset} className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-[#071412]">Try again</button><Link href="/" className="rounded-lg border border-border px-4 py-2 text-sm">Overview</Link></div></div></div>}
