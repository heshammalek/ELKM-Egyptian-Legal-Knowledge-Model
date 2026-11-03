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
