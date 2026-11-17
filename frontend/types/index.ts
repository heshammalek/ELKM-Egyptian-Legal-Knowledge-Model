// types/index.ts

export interface Document {
  doc_id: string;
  title: string;
}

export interface Relation {
  direction: 'Source' | 'Target';
  src_doc: string;
  src_art: string;
  rel_type: string;
  tgt_doc: string | null;
  tgt_art: string | null;
  ref_text?: string;
}

export interface SearchResult {
  document: Document;
  relations: Relation[];
}

export interface SearchResponse {
  results: SearchResult[];
  message: string;
  source: string;
  answer: string;
  cypher: string | null;
}

// ---- طبقة البيانات ----
export type DocType =
  | "constitution" | "declaration" | "law" | "decree_law"
  | "presidential_decision" | "administrative_decision" | "other";

export interface LegalNode {
  id: string;
  kind: "document" | "article";
  docId: string;
  art?: string;
  title?: string;
  docType: DocType;
  relTypes: string[];
  refTexts: string[];
}

export interface LegalEdge {
  id: string;
  from: string;
  to: string;
  type: string;
  refTexts: string[];
}

export interface LegalGraph {
  nodes: LegalNode[];
  edges: LegalEdge[];
  stats: { documents: number; articles: number; relations: number; byType: Record<string, number> };
}

// ---- الشات والعرض ----
export interface ChatMessage {
  role: "user" | "ai";
  text: string;
  raw?: SearchResponse;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
}

export interface Slide {
  id: string;
  title: string;
  body: string;     // markdown
  mermaid: string;  // "" لو مفيش علاقات مرتبطة
}
