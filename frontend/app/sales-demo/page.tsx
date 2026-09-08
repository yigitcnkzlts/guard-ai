"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, CheckCircle2, CircleDollarSign, ShieldCheck, Sparkles } from "lucide-react";
import { useLocale } from "@/components/layout/LocaleProvider";

const stories = {
  tr: [
    { title: "Riskli işlem oluşur", detail: "Finans ajanı 48.500 ₺ tutarında iade başlatır.", result: "İşlem müşterinin sistemine ulaşmadan yakalanır." },
    { title: "Politika milisaniyeler içinde çalışır", detail: "10.000 ₺ üzerindeki iadeler için yönetici onayı kuralı eşleşir.", result: "GUARD işlemi durdurur ve gerekçeyi kaydeder." },
    { title: "Yetkili kişi karar verir", detail: "Finans yöneticisi bağlamı, riski ve geçmişi tek ekranda görür.", result: "Onay veya ret kararı kimlik ve zaman bilgisiyle saklanır." },
    { title: "Denetim kanıtı hazırdır", detail: "Ajan, politika, istek ve insan kararı tek zincirde raporlanır.", result: "Denetim hazırlığı günlerden dakikalara iner." },
  ],
  en: [
    { title: "A risky action starts", detail: "A finance agent initiates a ₺48,500 refund.", result: "The action is intercepted before reaching the customer system." },
    { title: "Policy evaluates in milliseconds", detail: "The manager-approval rule for refunds over ₺10,000 matches.", result: "GUARD pauses the action and records the reason." },
    { title: "An authorized person decides", detail: "A finance manager sees context, risk and history in one view.", result: "Approval or denial is stored with identity and time." },
    { title: "Audit evidence is ready", detail: "Agent, policy, request and human decision form one evidence chain.", result: "Audit preparation drops from days to minutes." },
  ],
};

export default function SalesDemoPage() {
  const { locale } = useLocale();
  const [step, setStep] = useState(0);
  const copy = stories[locale];
  const current = copy[step];
  const tr = locale === "tr";
  return <div className="mx-auto max-w-5xl space-y-7">
    <header className="flex flex-wrap items-end justify-between gap-4"><div><p className="mb-2 flex items-center gap-2 text-sm font-medium text-accent"><Sparkles className="h-4 w-4"/>{tr?"5 dakikalık müşteri sunumu":"5-minute customer presentation"}</p><h1 className="text-3xl font-semibold">{tr?"Satış Demosu":"Sales Demo"}</h1><p className="mt-2 max-w-2xl text-muted">{tr?"GUARD AI'ın finansal bir riski nasıl durdurduğunu adım adım gösterin.":"Show how GUARD AI stops a financial risk, step by step."}</p></div><span className="rounded-full border border-border px-3 py-1.5 text-sm text-muted">{step+1} / {copy.length}</span></header>
    <div className="grid gap-5 lg:grid-cols-[1.1fr_.9fr]">
      <section className="rounded-2xl border border-border bg-surface p-6 sm:p-8" aria-live="polite"><div className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl bg-accent/10 text-accent"><ShieldCheck/></span><div><p className="text-xs font-semibold uppercase tracking-wider text-muted">{tr?"Müşteri problemi":"Customer problem"}</p><h2 className="mt-1 text-xl font-semibold">{current.title}</h2></div></div><p className="mt-8 text-lg leading-relaxed">{current.detail}</p><div className="mt-8 rounded-xl border border-emerald-400/20 bg-emerald-400/[.06] p-4"><p className="text-xs font-semibold uppercase tracking-wider text-emerald-300">{tr?"İş sonucu":"Business outcome"}</p><p className="mt-2 text-sm text-emerald-100">{current.result}</p></div><div className="mt-8 flex gap-3"><button onClick={()=>setStep(step===copy.length-1?0:step+1)} className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-[#071412]">{step===copy.length-1?(tr?"Baştan başlat":"Restart"):(tr?"Sonraki adım":"Next step")}<ArrowRight className="h-4 w-4"/></button><Link href="/approvals" className="rounded-lg border border-border px-4 py-2.5 text-sm">{tr?"Onay merkezini aç":"Open approvals"}</Link></div></section>
      <aside className="rounded-2xl border border-border bg-background p-6"><p className="text-sm font-semibold">{tr?"Sunum konuşma notları":"Presenter notes"}</p><ol className="mt-5 space-y-4">{copy.map((item,i)=><li key={item.title} className={`flex gap-3 text-sm ${i===step?"text-foreground":"text-muted"}`}><CheckCircle2 className={`mt-0.5 h-4 w-4 shrink-0 ${i<=step?"text-accent":"text-muted"}`}/><button className="text-left" onClick={()=>setStep(i)}>{item.title}</button></li>)}</ol><div className="mt-7 border-t border-border pt-5"><CircleDollarSign className="h-5 w-5 text-accent"/><p className="mt-3 text-sm font-medium">{tr?"Değer mesajı":"Value message"}</p><p className="mt-1 text-sm text-muted">{tr?"Daha az yetkisiz işlem, daha hızlı denetim ve kontrollü AI ölçeklendirmesi.":"Fewer unauthorized actions, faster audits and controlled AI scaling."}</p></div></aside>
    </div>
  </div>;
}
