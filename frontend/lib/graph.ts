import type { DocType, LegalEdge, LegalGraph, LegalNode, SearchResponse, Slide } from "../types";

/* ====================== ثوابت العرض ====================== */

export const REL_LABEL: Record<string, string> = {
  referral: "إحالة",
  total_repeal: "إلغاء كلي",
  abolishes: "إلغاء كيان",
  renames: "إعادة تسمية",
  creates_position: "إنشاء منصب",
  establishes: "إنشاء هيئة",
  empowers: "منح اختصاص",
  contains: "يتضمن",
};

export const REL_COLOR: Record<string, string> = {
  referral: "#d29922",
  total_repeal: "#f85149",
  abolishes: "#f0883e",
  renames: "#a371f7",
  creates_position: "#3fb950",
  establishes: "#2ea8a0",
  empowers: "#58a6ff",
  contains: "#30363d",
};

const REL_PRIORITY = ["total_repeal", "abolishes", "renames", "creates_position", "establishes", "empowers", "referral"];

export const DOC_COLOR: Record<DocType, string> = {
  constitution: "#e3b341",
  declaration: "#f0883e",
  law: "#58a6ff",
  decree_law: "#79c0ff",
  presidential_decision: "#a371f7",
  administrative_decision: "#8b949e",
  other: "#6e7681",
};

export const DOC_LABEL: Record<DocType, string> = {
  constitution: "دستور",
  declaration: "إعلان دستوري",
  law: "قانون",
  decree_law: "قرار بقانون",
  presidential_decision: "قرار رئاسي",
  administrative_decision: "قرار إداري",
  other: "أخرى",
};

export const relLabel = (t: string) => REL_LABEL[t] ?? t;

export function docTypeOf(id: string): DocType {
  if (id.startsWith("CONST-TRANS")) return "declaration";
  if (id.startsWith("CONST")) return "constitution";
  if (id.startsWith("LAW-")) return "law";
  if (id.startsWith("DL-")) return "decree_law";
  if (id.startsWith("ADM-PRES")) return "presidential_decision";
  if (id.startsWith("ADM-")) return "administrative_decision";
  return "other";
}

/* ====================== بناء الجراف من رد الـ API ====================== */

// يضيف نصاً بدون تكرار: يتجاهل لو موجود جزء منه، ويشيل القديم لو النص الجديد أشمل
function pushText(list: string[], raw?: string | null) {
  if (!raw) return;
  const t = raw.replace(/(\.{3}|…)\s*$/, "").trim();
  if (!t || list.some((x) => x.includes(t))) return;
  for (let i = list.length - 1; i >= 0; i--) if (t.includes(list[i])) list.splice(i, 1);
  list.push(t);
}

const primaryRel = (types: string[]) => REL_PRIORITY.find((t) => types.includes(t)) ?? types[0];

export function buildLegalGraph(resp?: SearchResponse | null): LegalGraph {
  const nodes = new Map<string, LegalNode>();
  const edges = new Map<string, LegalEdge>();

  const addEdge = (from: string, to: string, type: string, text?: string | null) => {
    const id = `${from}|${type}|${to}`;
    let e = edges.get(id);
    if (!e) { e = { id, from, to, type, refTexts: [] }; edges.set(id, e); }
    pushText(e.refTexts, text);
  };

  const docNode = (docId: string, title?: string): LegalNode => {
    let n = nodes.get(docId);
    if (!n) {
      n = { id: docId, kind: "document", docId, docType: docTypeOf(docId), relTypes: [], refTexts: [] };
      nodes.set(docId, n);
    }
    if (title && !n.title) n.title = title;
    return n;
  };

  const artNode = (docId: string, art: string): LegalNode => {
    const id = `${docId}#${art}`;
    let n = nodes.get(id);
    if (!n) {
      docNode(docId);
      n = { id, kind: "article", docId, art, docType: docTypeOf(docId), relTypes: [], refTexts: [] };
      nodes.set(id, n);
      addEdge(docId, id, "contains");
    }
    return n;
  };

  for (const r of resp?.results ?? []) {
    docNode(r.document.doc_id, r.document.title);
    for (const rel of r.relations ?? []) {
      const src = rel.src_art ? artNode(rel.src_doc, rel.src_art) : docNode(rel.src_doc);
      if (rel.tgt_doc) {
        const tgt = rel.tgt_art ? artNode(rel.tgt_doc, rel.tgt_art) : docNode(rel.tgt_doc);
        addEdge(src.id, tgt.id, rel.rel_type, rel.ref_text);
      } else {
        if (!src.relTypes.includes(rel.rel_type)) src.relTypes.push(rel.rel_type);
        pushText(src.refTexts, rel.ref_text);
      }
    }
  }

  const byType: Record<string, number> = {};
  let relations = 0;
  const bump = (t: string) => { byType[t] = (byType[t] ?? 0) + 1; relations++; };
  nodes.forEach((n) => n.relTypes.forEach(bump));
  edges.forEach((e) => { if (e.type !== "contains") bump(e.type); });

  const nodeList = [...nodes.values()];
  return {
    nodes: nodeList,
    edges: [...edges.values()],
    stats: {
      documents: nodeList.filter((n) => n.kind === "document").length,
      articles: nodeList.filter((n) => n.kind === "article").length,
      relations,
      byType,
    },
  };
}

const articleColor = (n: LegalNode) =>
  n.relTypes.length ? REL_COLOR[primaryRel(n.relTypes)] ?? "#6e7681" : "#6e7681";

// صيغة NVL 2.0.0: color / size / captionAlign (مش style)
export function toNvl(g: LegalGraph) {
  const nodes = g.nodes.map((n) => ({
    id: n.id,
    caption: n.kind === "document" ? n.docId : `م ${n.art}`,
    color: n.kind === "document" ? DOC_COLOR[n.docType] : articleColor(n),
    size: n.kind === "document" ? 40 : 22,
    captionAlign: "bottom" as const,
  }));
  const rels = g.edges.map((e) => ({
    id: e.id,
    from: e.from,
    to: e.to,
    caption: e.type === "contains" ? undefined : relLabel(e.type),
    color: REL_COLOR[e.type] ?? "#8b949e",
    width: e.type === "contains" ? 1 : 2,
  }));
  return { nodes, rels };
}

/* ====================== الشرائح (Mermaid لكل شريحة) ====================== */

const clean = (s: string) =>
  s.replace(/^#{1,6}\s*/, "").replace(/[*_`]/g, "").replace(/[:：]\s*$/, "").trim();
const escRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const yearOf = (docId: string) => docId.match(/(?:19|20)\d{2}/)?.[0];
const mid = (id: string) => "n" + id.replace(/[^a-zA-Z0-9]/g, "_");
const q = (s: string) => `"${s.replace(/"/g, "'")}"`;

function classDefs(): string[] {
  const out = Object.entries(REL_COLOR)
    .filter(([k]) => k !== "contains")
    .map(([k, c]) => `  classDef c_${k} fill:${c}33,stroke:${c},color:#111;`);
  out.push("  classDef c_none fill:#e5e7eb,stroke:#9ca3af,color:#111;");
  Object.entries(DOC_COLOR).forEach(([k, c]) => out.push(`  classDef d_${k} fill:${c}44,stroke:${c},color:#111,stroke-width:2px;`));
  return out;
}

// رسم مجموعة عقد: كل وثيقة subgraph، ومواد كل وثيقة جواها، والحواف بين الوثائق بين العقد المختارة
function mermaidFor(g: LegalGraph, ids: Set<string>): string {
  if (!ids.size) return "";
  const byId = new Map(g.nodes.map((n) => [n.id, n]));
  const groups = new Map<string, LegalNode[]>();
  ids.forEach((id) => {
    const n = byId.get(id);
    if (n) groups.set(n.docId, [...(groups.get(n.docId) ?? []), n]);
  });
  const lines = ["flowchart LR"];
  let i = 0;
  groups.forEach((list, docId) => {
    lines.push(`  subgraph g${i++}[${q(docId)}]`, "    direction TB");
    list.forEach((n) => {
      if (n.kind === "document") {
        lines.push(`    ${mid(n.id)}[${q(n.docId)}]:::d_${n.docType}`);
      } else {
        const t = n.relTypes.length ? primaryRel(n.relTypes) : "none";
        const sub = n.relTypes.length ? `<br/>${relLabel(t)}` : "";
        lines.push(`    ${mid(n.id)}[${q(`م ${n.art}${sub}`)}]:::c_${t}`);
      }
    });
    lines.push("  end");
  });
  g.edges.forEach((e) => {
    if (e.type !== "contains" && ids.has(e.from) && ids.has(e.to))
      lines.push(`  ${mid(e.from)} -->|${q(relLabel(e.type))}| ${mid(e.to)}`);
  });
  return [...lines, ...classDefs()].join("\n");
}

// نظرة عامة: كل وثيقة عقدة، والحواف مجمّعة (نوع العلاقة × العدد)
function overviewMermaid(g: LegalGraph, maxDocs = 14): string {
  const docs = g.nodes.filter((n) => n.kind === "document").slice(0, maxDocs);
  if (!docs.length) return "";
  const keep = new Set(docs.map((d) => d.id));
  const lines = ["flowchart LR"];
  docs.forEach((d) => {
    const arts = g.nodes.filter((n) => n.kind === "article" && n.docId === d.id);
    const sem = arts.reduce((s, a) => s + a.relTypes.length, 0);
    const info = sem ? `<br/>${arts.length} مادة · ${sem} علاقة` : "";
    lines.push(`  ${mid(d.id)}[${q(d.docId + info)}]:::d_${d.docType}`);
  });
  const agg = new Map<string, { from: string; to: string; type: string; n: number }>();
  g.edges.forEach((e) => {
    if (e.type === "contains") return;
    const from = e.from.split("#")[0];
    const to = e.to.split("#")[0];
    if (!keep.has(from) || !keep.has(to)) return;
    const k = `${from}|${e.type}|${to}`;
    const a = agg.get(k) ?? { from, to, type: e.type, n: 0 };
    a.n++;
    agg.set(k, a);
  });
  agg.forEach((a) =>
    lines.push(`  ${mid(a.from)} -->|${q(relLabel(a.type) + (a.n > 1 ? ` ×${a.n}` : ""))}| ${mid(a.to)}`)
  );
  return [...lines, ...classDefs()].join("\n");
}

// المواد اللي نص الشريحة بيذكرها (رقم المادة + نوع علاقتها + سنة وثيقتها) — تخمين، والبديل الدقيق Slide Plan من الباكند
function matchArticles(text: string, g: LegalGraph, max = 12): LegalNode[] {
  const scored: { n: LegalNode; s: number }[] = [];
  for (const n of g.nodes) {
    if (n.kind !== "article" || !n.art || !n.relTypes.length) continue;
    if (!new RegExp(`(?<!\\d)${escRe(n.art)}(?!\\d)`).test(text)) continue;
    let s = 1;
    if (n.relTypes.some((t) => text.includes(t) || text.includes(relLabel(t)))) s += 2;
    const y = yearOf(n.docId);
    if (y && text.includes(y)) s += 1;
    scored.push({ n, s });
  }
  return scored.sort((a, b) => b.s - a.s).slice(0, max).map((x) => x.n);
}

function slideMermaid(chunk: string, g: LegalGraph): string {
  const ids = new Set<string>();
  matchArticles(chunk, g).forEach((n) => ids.add(n.id));
  // أنواع العلاقات المذكورة صراحةً (الحواف بين الوثائق)
  const mentioned = new Set(
    Object.keys(g.stats.byType).filter((t) => chunk.includes(t) || chunk.includes(relLabel(t)))
  );
  let added = 0;
  for (const e of g.edges) {
    if (e.type === "contains" || !mentioned.has(e.type) || added >= 8) continue;
    ids.add(e.from);
    ids.add(e.to);
    added++;
  }
  return mermaidFor(g, ids);
}

export function buildSlides(answer: string, question: string, g: LegalGraph): Slide[] {
  if (!answer.trim()) return [];
  let parts = answer
    .split(/\n\s*(?:-{3,}|\*{3,})\s*\n|\n(?=#{1,3}\s)/)
    .map((s) => s.trim())
    .filter(Boolean);

  if (parts.length < 2) {
    const paras = answer.split(/\n{2,}/).map((s) => s.trim()).filter(Boolean);
    parts = [];
    for (let i = 0; i < paras.length; i += 2) parts.push(paras.slice(i, i + 2).join("\n\n"));
  }

  return parts.slice(0, 12).map((chunk, i) => {
    const [first, ...rest] = chunk.split("\n");
    const t = clean(first);
    const isTitle = i > 0 && t.length > 0 && t.length <= 90 && !first.trim().startsWith("|");
    const title = i === 0 ? question || "نظرة عامة" : isTitle ? t : `القسم ${i}`;
    const body = i === 0 || !isTitle ? chunk : rest.join("\n").trim() || chunk;
    const mermaid = i === 0 ? overviewMermaid(g) : slideMermaid(chunk, g);
    return { id: `s${i}`, title, body, mermaid };
  });
}
