"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  MagnifyingGlassPlusIcon,
  MagnifyingGlassMinusIcon,
  ViewfinderCircleIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import { DOC_COLOR, DOC_LABEL, REL_COLOR, relLabel, toNvl } from "../lib/graph";
import type { LegalGraph } from "../types";

interface Props {
  graph: LegalGraph;
  isFullScreen: boolean;
}

const btn = "p-1.5 text-gray-400 hover:text-white hover:bg-[#2a2a2a] rounded transition";

export default function GraphView({ graph, isFullScreen }: Props) {
  const nvlRef = useRef<any>(null);
  const [Nvl, setNvl] = useState<any>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const { nodes, rels } = useMemo(() => toNvl(graph), [graph]);

  // تحميل NVL على العميل فقط (بيستخدم window/canvas)، ومن غير next/dynamic عشان الـ ref يشتغل مضمون
  useEffect(() => {
    import("@neo4j-nvl/react").then((m) => setNvl(() => m.InteractiveNvlWrapper));
  }, []);

  const fit = () => nvlRef.current?.fit(graph.nodes.map((n) => n.id));

  const zoomBy = (factor: number) => {
    const v = nvlRef.current;
    if (!v) return;
    v.setZoom(Math.min(5, Math.max(0.05, v.getScale() * factor)));
  };

  // الـ layout بيستقر بعد ثواني، فنعمل fit بعد التحميل وبعد تغيير الحجم
  useEffect(() => {
    if (!Nvl || !graph.nodes.length) return;
    const timers = [800, 2000].map((ms) => setTimeout(fit, ms));
    return () => timers.forEach(clearTimeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [Nvl, graph, isFullScreen]);

  const sel = graph.nodes.find((n) => n.id === selectedId);
  const docTitle = sel ? sel.title ?? graph.nodes.find((n) => n.id === sel.docId)?.title : undefined;
  const docTypes = [...new Set(graph.nodes.filter((n) => n.kind === "document").map((n) => n.docType))];
  const relTypes = Object.keys(graph.stats.byType);
  const graphKey = `${isFullScreen}-${graph.nodes.length}-${graph.edges.length}-${graph.nodes[0]?.id ?? ""}`;

  return (
    <div id="print-graph" className="absolute inset-0 bg-[#111]">
      {graph.nodes.length === 0 ? (
        <div className="h-full flex items-center justify-center text-gray-600 text-sm">اطرح سؤالاً لعرض الجراف.</div>
      ) : (
        <>
          <div className="absolute inset-0">
            {Nvl && (
              <Nvl
                key={graphKey}
                ref={nvlRef}
                nodes={nodes}
                rels={rels}
                style={{ width: "100%", height: "100%" }}
                mouseEventCallbacks={{
                  onPan: true,
                  onZoomAndPan: true,
                  onDrag: true,
                  onNodeClick: (n: any) => setSelectedId(n.id),
                  onCanvasClick: () => setSelectedId(null),
                }}
                nvlCallbacks={{ onLayoutDone: fit }}
                nvlOptions={{
                  initialZoom: 1,
                  minZoom: 0.05,
                  maxZoom: 5,
                  renderer: "canvas",
                  allowDynamicMinZoom: true,
                  layout: "forceDirected",
                }}
              />
            )}
          </div>

          <div data-no-print className="absolute top-4 right-4 z-10 flex flex-col gap-1 bg-[#1a1a1a] p-1 rounded-lg border border-[#2a2a2a] shadow-lg">
            <button onClick={() => zoomBy(1.3)} className={btn} title="تكبير"><MagnifyingGlassPlusIcon className="w-4 h-4" /></button>
            <button onClick={() => zoomBy(1 / 1.3)} className={btn} title="تصغير"><MagnifyingGlassMinusIcon className="w-4 h-4" /></button>
            <button onClick={fit} className={btn} title="ملاءمة الشاشة"><ViewfinderCircleIcon className="w-4 h-4" /></button>
          </div>

          <div data-no-print dir="rtl" className="absolute bottom-4 right-4 z-10 max-w-[60%] rounded-lg border border-[#2a2a2a] bg-[#1a1a1a]/90 px-3 py-2 text-[11px] text-gray-400">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
              {docTypes.map((t) => (
                <span key={t} className="flex items-center gap-1">
                  <i className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: DOC_COLOR[t] }} />
                  {DOC_LABEL[t]}
                </span>
              ))}
            </div>
            <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
              {relTypes.map((t) => (
                <span key={t} className="flex items-center gap-1">
                  <i className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: REL_COLOR[t] ?? "#8b949e" }} />
                  {relLabel(t)} ({graph.stats.byType[t]})
                </span>
              ))}
            </div>
            <div className="mt-1 text-gray-600">اسحب للتحريك · العجلة للتكبير · اضغط على عقدة للتفاصيل</div>
          </div>

          {sel && (
            <div data-no-print dir="rtl" className="absolute bottom-4 left-4 z-10 max-h-[60%] w-80 overflow-y-auto rounded-xl border border-[#2a2a2a] bg-[#1a1a1a]/95 p-4 text-sm shadow-lg">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="font-bold text-white">{sel.kind === "document" ? sel.docId : `المادة ${sel.art}`}</div>
                  <div className="text-xs text-gray-400">
                    {sel.kind === "article" && `${sel.docId} · `}
                    {DOC_LABEL[sel.docType]}
                  </div>
                </div>
                <button onClick={() => setSelectedId(null)} className={btn}><XMarkIcon className="w-4 h-4" /></button>
              </div>
              {docTitle && <p className="mt-2 leading-7 text-gray-300">{docTitle}</p>}
              {sel.relTypes.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {sel.relTypes.map((t) => (
                    <span key={t} className="rounded px-2 py-0.5 text-xs text-black" style={{ background: REL_COLOR[t] ?? "#8b949e" }}>
                      {relLabel(t)}
                    </span>
                  ))}
                </div>
              )}
              {sel.refTexts.map((t, i) => (
                <blockquote key={i} className="mt-3 border-r-2 border-blue-500/60 pr-3 leading-7 text-gray-300">{t}</blockquote>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
