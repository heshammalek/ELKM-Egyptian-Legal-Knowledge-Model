"use client";

import {
  ArrowsPointingInIcon,
  ArrowsPointingOutIcon,
  Bars3Icon,
  DocumentTextIcon,
  MapIcon,
  PresentationChartBarIcon,
  PrinterIcon,
  ShareIcon,
} from "@heroicons/react/24/outline";

export type TabId = "graph" | "text" | "diagram";

interface Props {
  active: TabId;
  onTab: (t: TabId) => void;
  onPrint: () => void;
  onShare: () => void;
  isFullScreen: boolean;
  onToggleFullScreen: () => void;
  sidebarClosed: boolean;
  onOpenSidebar: () => void;
}

const iconBtn = "p-1.5 text-gray-400 hover:text-white hover:bg-[#1a1a1a] rounded transition";

export default function ResultTabs(p: Props) {
  const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: "graph", label: "Graph", icon: <MapIcon className="w-4 h-4" /> },
    { id: "text", label: "Text", icon: <DocumentTextIcon className="w-4 h-4" /> },
    { id: "diagram", label: "Presentation", icon: <PresentationChartBarIcon className="w-4 h-4" /> },
  ];

  return (
    <div className="flex items-center justify-between px-4 py-2 bg-[#0d0d0d] shrink-0 border-b border-gray-800">
      <div className="flex items-center gap-2">
        {p.sidebarClosed && !p.isFullScreen && (
          <button onClick={p.onOpenSidebar} className={iconBtn}><Bars3Icon className="w-5 h-5" /></button>
        )}
        <div className="flex items-center gap-1">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => p.onTab(t.id)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-all ${
                p.active === t.id ? "bg-[#2a2a2a] text-white" : "text-gray-500 hover:text-gray-300 hover:bg-[#1a1a1a]"
              }`}
            >
              {t.icon}
              <span className="hidden sm:inline">{t.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-1">
        <button onClick={p.onPrint} className={iconBtn} title="طباعة منطقة العرض"><PrinterIcon className="w-5 h-5" /></button>
        <button onClick={p.onShare} className={iconBtn} title="مشاركة"><ShareIcon className="w-5 h-5" /></button>
        <div className="w-px h-5 bg-gray-700 mx-1" />
        <button onClick={p.onToggleFullScreen} className={iconBtn} title={p.isFullScreen ? "خروج (Esc)" : "ملء الشاشة"}>
          {p.isFullScreen ? <ArrowsPointingInIcon className="w-5 h-5" /> : <ArrowsPointingOutIcon className="w-5 h-5" />}
        </button>
      </div>
    </div>
  );
}

/* ====================== الطباعة: منطقة العرض فقط ====================== */

// يدمج كل طبقات الـ canvas (الجراف) في صورة واحدة
function snapshotCanvases(el: HTMLElement): string | null {
  const cs = Array.from(el.querySelectorAll("canvas"));
  if (!cs.length) return null;
  const w = Math.max(...cs.map((c) => c.width));
  const h = Math.max(...cs.map((c) => c.height));
  if (!w || !h) return null;
  const out = document.createElement("canvas");
  out.width = w;
  out.height = h;
  const ctx = out.getContext("2d");
  if (!ctx) return null;
  ctx.fillStyle = "#111";
  ctx.fillRect(0, 0, w, h);
  cs.forEach((c) => {
    try { ctx.drawImage(c, 0, 0); } catch {}
  });
  try { return out.toDataURL("image/png"); } catch { return null; }
}

export async function printElement(el: HTMLElement | null, opts: { landscape?: boolean; title?: string } = {}) {
  if (!el) return;
  const shot = snapshotCanvases(el);
  const clone = el.cloneNode(true) as HTMLElement;
  clone.querySelectorAll("[data-no-print]").forEach((n) => n.remove());
  clone.querySelectorAll("canvas").forEach((c, i) => {
    if (i === 0 && shot) {
      const img = document.createElement("img");
      img.src = shot;
      img.style.cssText = "width:100%;height:auto;display:block";
      c.replaceWith(img);
    } else c.remove();
  });

  const links = Array.from(document.querySelectorAll<HTMLLinkElement>('link[rel="stylesheet"]'))
    .map((l) => `<link rel="stylesheet" href="${l.href}">`)
    .join("");
  const styles = Array.from(document.querySelectorAll("style")).map((s) => s.outerHTML).join("");
  const title = (opts.title ?? "LexChain Egypt").replace(/[<>&]/g, "");

  const iframe = document.createElement("iframe");
  iframe.style.cssText = "position:fixed;right:0;bottom:0;width:0;height:0;border:0;visibility:hidden";
  document.body.appendChild(iframe);
  const doc = iframe.contentDocument;
  const win = iframe.contentWindow;
  if (!doc || !win) return iframe.remove();

  doc.open();
  doc.write(`<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><title>${title}</title>${links}${styles}
<style>
  @page { size: A4 ${opts.landscape ? "landscape" : "portrait"}; margin: 12mm; }
  html, body { background:#fff !important; height:auto !important; overflow:visible !important; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .print-root, .print-root > * { position:static !important; inset:auto !important; height:auto !important; }
  .print-root * { overflow:visible !important; max-height:none !important; }
  .print-root *:not(svg):not(svg *):not(img) { background-color:transparent !important; color:#111 !important; border-color:#bbb !important; }
  [data-slide] { display:grid !important; grid-template-columns:1fr 1fr !important; height:auto !important; min-height:175mm; break-after:page; page-break-after:always; border:1px solid #ccc; }
  [data-slide]:last-child { break-after:auto; page-break-after:auto; }
  tr { break-inside:avoid; }
</style></head><body><div class="print-root">${clone.outerHTML}</div></body></html>`);
  doc.close();

  // نستنى تحميل ملفات الـ CSS قبل الطباعة
  await new Promise<void>((resolve) => {
    const pending = Array.from(doc.querySelectorAll('link[rel="stylesheet"]'));
    let left = pending.length;
    if (!left) return resolve();
    const done = () => { if (--left <= 0) resolve(); };
    pending.forEach((l) => {
      l.addEventListener("load", done);
      l.addEventListener("error", done);
    });
    setTimeout(resolve, 4000);
  });
  await new Promise((r) => setTimeout(r, 300));

  win.addEventListener("afterprint", () => iframe.remove());
  setTimeout(() => iframe.remove(), 120000);
  win.focus();
  win.print();
}
