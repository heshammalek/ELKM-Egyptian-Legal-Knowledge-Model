"use client";

import { useEffect, useRef } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import type { ChatMessage } from "../types";

const components: Components = {
  h1: ({ children }) => <h1 dir="auto" className="text-xl font-bold mt-5 mb-2 text-white text-start">{children}</h1>,
  h2: ({ children }) => <h2 dir="auto" className="text-lg font-bold mt-5 mb-2 text-white text-start">{children}</h2>,
  h3: ({ children }) => <h3 dir="auto" className="text-base font-semibold mt-4 mb-2 text-white text-start">{children}</h3>,
  p: ({ children }) => <p dir="auto" className="my-2 leading-8 text-start">{children}</p>,
  strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
  ul: ({ children }) => <ul className="list-disc pr-6 my-2 space-y-1">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pr-6 my-2 space-y-1">{children}</ol>,
  li: ({ children }) => <li dir="auto" className="leading-8 text-start">{children}</li>,
  hr: () => <hr className="my-5 border-gray-700" />,
  blockquote: ({ children }) => (
    <blockquote className="my-3 border-r-4 border-blue-500/60 bg-white/5 pr-4 py-1 rounded-sm">{children}</blockquote>
  ),
  code: ({ children }) => (
    <code dir="ltr" className="px-1.5 py-0.5 rounded bg-black/40 text-amber-300 text-[13px] font-mono">{children}</code>
  ),
  table: ({ children }) => (
    <div className="my-4 overflow-x-auto rounded-lg border border-gray-700">
      <table dir="rtl" className="w-full text-sm border-collapse">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-[#262626]">{children}</thead>,
  th: ({ children }) => (
    <th dir="auto" className="px-3 py-2 font-semibold text-start whitespace-nowrap border-b border-gray-600">{children}</th>
  ),
  td: ({ children }) => (
    <td dir="auto" className="px-3 py-2 align-top text-start border-t border-gray-800">{children}</td>
  ),
  tr: ({ children }) => <tr className="even:bg-white/[0.03]">{children}</tr>,
};

// مستخدم هنا وفي SlidesView
export function ArabicMarkdown({ children }: { children: string }) {
  return (
    <div dir="rtl" className="text-start text-[15px] text-gray-200">
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} components={components}>
        {children}
      </ReactMarkdown>
    </div>
  );
}

interface Props {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  active: boolean;
}

export default function TextView({ messages, loading, error, active }: Props) {
  const lastUserRef = useRef<HTMLDivElement>(null);
  const lastUserIdx = messages.map((m) => m.role).lastIndexOf("user");

  // نروح لبداية آخر سؤال (مش لآخر الإجابة، عشان الإجابات الطويلة والجداول)
  useEffect(() => {
    if (active) lastUserRef.current?.scrollIntoView({ block: "start" });
  }, [messages, loading, active]);

  return (
    <div className={`absolute inset-0 overflow-y-auto px-4 py-6 justify-center ${active ? "flex" : "hidden"}`}>
      <div id="print-text" className="w-full max-w-3xl space-y-6 pb-10" dir="rtl">
        {messages.length === 0 && !loading && (
          <div className="flex justify-center items-center h-[50vh] text-gray-600 flex-col">
            <div className="text-5xl mb-4 opacity-20">⚖️</div>
            <p className="text-sm">كيف يمكنني مساعدتك في استفسارك القانوني اليوم؟</p>
          </div>
        )}

        {messages.map((msg, idx) =>
          msg.role === "user" ? (
            <div key={idx} ref={idx === lastUserIdx ? lastUserRef : undefined} className="flex justify-start">
              <div dir="auto" className="max-w-[80%] p-4 rounded-2xl text-sm bg-[#2a2a2a] border border-[#333] text-white rounded-tr-sm text-start">
                {msg.text}
              </div>
            </div>
          ) : (
            <div key={idx} className="w-full p-5 rounded-2xl bg-[#1a1a1a] border border-[#2a2a2a] rounded-tr-sm">
              <ArabicMarkdown>{msg.text}</ArabicMarkdown>
              {msg.raw && (msg.raw.source || msg.raw.cypher) && (
                <details data-no-print dir="rtl" className="mt-4 text-xs text-gray-500">
                  <summary className="cursor-pointer select-none">كيف وصلنا لهذه النتيجة</summary>
                  <div dir="ltr" className="mt-2 space-y-1 text-left">
                    {msg.raw.source && <p>source: {msg.raw.source}</p>}
                    {msg.raw.message && <p>{msg.raw.message}</p>}
                    {msg.raw.cypher && (
                      <pre className="overflow-x-auto rounded bg-black/40 p-2 text-[11px] text-amber-300">{msg.raw.cypher}</pre>
                    )}
                  </div>
                </details>
              )}
            </div>
          )
        )}

        {loading && <div className="text-center text-blue-400 text-sm animate-pulse">جارٍ التحليل...</div>}
        {error && <div className="text-center text-red-500 text-sm">{error}</div>}
      </div>
    </div>
  );
}
