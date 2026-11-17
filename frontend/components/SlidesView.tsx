"use client";

import { useEffect, useState } from "react";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import { ArabicMarkdown } from "./TextView";
import type { Slide } from "../types";

interface Props {
  slides: Slide[];
  index: number;
  onIndex: (i: number) => void;
}

export default function SlidesView({ slides, index, onIndex }: Props) {
  const [svgs, setSvgs] = useState<Record<string, string>>({});
  const [done, setDone] = useState(false);

  // نرسم كل الشرائح مرة واحدة (مطلوب للطباعة الكاملة)، ومermaid بيتحمّل عند الحاجة بس
  useEffect(() => {
    let cancelled = false;
    setDone(false);
    (async () => {
      const { default: mermaid } = await import("mermaid");
      mermaid.initialize({ startOnLoad: false, theme: "default", flowchart: { htmlLabels: true, curve: "basis" } });
      const out: Record<string, string> = {};
      for (const s of slides) {
        if (!s.mermaid) continue;
        try {
          if (!(await mermaid.parse(s.mermaid, { suppressErrors: true }))) continue;
          const { svg } = await mermaid.render(`m-${s.id}-${Date.now()}`, s.mermaid);
          out[s.id] = svg;
        } catch (e) {
          console.error("mermaid", s.id, e);
        }
      }
      if (!cancelled) {
        setSvgs(out);
        setDone(true);
      }
    })();
    return () => { cancelled = true; };
  }, [slides]);

  // RTL: السهم الأيسر = التالي (ونتجاهل الكتابة في مربع الإدخال)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && (t.tagName === "TEXTAREA" || t.tagName === "INPUT")) return;
      if (e.key === "ArrowLeft") onIndex(Math.min(slides.length - 1, index + 1));
      if (e.key === "ArrowRight") onIndex(Math.max(0, index - 1));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [index, slides.length, onIndex]);

  if (!slides.length)
    return (
      <div className="absolute inset-0 flex items-center justify-center text-gray-600 text-sm">
        اطرح سؤالاً لإنشاء العرض التقديمي.
      </div>
    );

  return (
    <div className="absolute inset-0 flex flex-col p-4 gap-3" dir="rtl">
      <div id="print-slides" className="flex-1 min-h-0 relative">
        {slides.map((s, i) => (
          <section
            key={s.id}
            data-slide
            className={`${i === index ? "grid" : "hidden"} h-full grid-cols-1 md:grid-cols-2 gap-4 rounded-2xl border border-gray-800 bg-[#111] p-5`}
          >
            <div className="min-h-0 overflow-y-auto pl-2">
              <h2 dir="auto" className="text-xl font-bold text-white mb-3 pb-2 border-b border-gray-700 text-start">{s.title}</h2>
              <ArabicMarkdown>{s.body}</ArabicMarkdown>
            </div>
            <div className="min-h-0 rounded-xl bg-white flex items-center justify-center overflow-auto p-3 [&_svg]:max-w-full [&_svg]:h-auto [&_svg]:max-h-full">
              {svgs[s.id] ? (
                <div dangerouslySetInnerHTML={{ __html: svgs[s.id] }} />
              ) : (
                <span className="text-gray-400 text-sm">
                  {!s.mermaid ? "لا توجد علاقات مرتبطة بهذه الشريحة" : done ? "تعذّر رسم المخطط" : "جارٍ الرسم..."}
                </span>
              )}
            </div>
          </section>
        ))}
      </div>

      <div data-no-print className="flex items-center justify-center gap-4 shrink-0">
        <button
          onClick={() => onIndex(Math.max(0, index - 1))}
          disabled={index === 0}
          className="p-2 rounded-full bg-[#1a1a1a] border border-gray-700 disabled:opacity-30 hover:bg-[#2a2a2a]"
        >
          <ChevronRightIcon className="w-5 h-5" />
        </button>
        <div className="flex gap-1.5">
          {slides.map((s, i) => (
            <button
              key={s.id}
              onClick={() => onIndex(i)}
              title={s.title}
              className={`h-2 rounded-full transition-all ${i === index ? "w-6 bg-blue-400" : "w-2 bg-gray-600 hover:bg-gray-400"}`}
            />
          ))}
        </div>
        <span className="text-xs text-gray-500 tabular-nums">{index + 1} / {slides.length}</span>
        <button
          onClick={() => onIndex(Math.min(slides.length - 1, index + 1))}
          disabled={index === slides.length - 1}
          className="p-2 rounded-full bg-[#1a1a1a] border border-gray-700 disabled:opacity-30 hover:bg-[#2a2a2a]"
        >
          <ChevronLeftIcon className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
