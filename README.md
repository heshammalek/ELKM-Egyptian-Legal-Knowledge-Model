# ELKM — Egyptian Legal Knowledge Model

<div align="center">

**An open-source, article-level temporal knowledge graph for Egyptian law**

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Data: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1.svg)](https://neo4j.com/)
[![Status](https://img.shields.io/badge/status-active%20development-orange.svg)]()
[![CI](https://img.shields.io/github/actions/workflow/status/heshammalek/ELKM-Egyptian-Legal-Knowledge-Model/ci.yml?branch=main)](https://github.com/heshammalek/ELKM-Egyptian-Legal-Knowledge-Model/actions)

> [!WARNING]
> **Active Development — Living Ontology**
>
> This project is an **ontology in the making** — not a finished product. This README provides a general overview of the project. It may not reflect the latest additions or refinements. The authoritative reference is the metadata files themselves; this document is intended as a conceptual guide.
> 
**[نسخة عربية ستكون متاحة في `docs/README.ar.md` (قيد الإعداد)](docs/README.ar.md)**

</div>

---

## 📑 Table of Contents

- [Why ELKM?](#why-elkm)
- [Quick Start](#-quick-start-tldr)
- [Core Challenges](#core-challenges)
- [The Academic Gap](#the-academic-gap)
- [Why ELKM Is Different](#why-elkm-is-different-competitive-context)
- [Project Scope](#project-scope-where-the-code-ends)
- [Repository Structure](#repository-structure)
- [Corpus Structure](#corpus-structure-corpus)
- [Relationship Graph](#relationship-graph)
- [RDF Export (Linked Data)](#rdf-export-linked-data)
- [Segmented Identifier System](#segmented-identifier-system)
- [Technical Stack](#technical-stack)
- [Intellectual References](#intellectual-references)
- [Current Status](#-current-status)
- [Roadmap](#roadmap)
- [How to Contribute](#-how-to-contribute)
- [Call for Collaboration](#call-for-collaboration)
- [Acknowledgments](#-acknowledgments)
- [License](#license)

---

## Why ELKM?

The first Arabic attempt to build a knowledge graph and ontology for the legal domain — a pioneering scientific, technical, and economic project.

### Scientific Value

The first comprehensive, open-source Arabic legal ontology. No equivalent currently exists. Existing efforts are limited to term lists without relationships, or theoretical papers never implemented in software. ELKM builds a **knowledge base** — not a text archive. The difference: an archive answers *what*; a knowledge base answers *why*.

### Technical Value

A **knowledge graph** connecting every legal text to everything that affected it or was affected by it, with full temporal tracking per article. This enables queries that are **impossible** in any text search engine or relational database:

- **Time-Travel**: Retrieve the text of an article as it stood on a specific historical date.
- **Multi-hop Impact**: Trace the final effect on Article X after a chain of amendments, rulings, and administrative decisions.
- **Dependency Map**: Find every text that cites a specific constitutional article.
- **Principle Tracking**: Trace how a legal principle evolved across decades of legislation.
- **Legislative Cycles**: Detect principles ruled unconstitutional and later re-enacted in new laws.

### Economic Value

Once interfaces are built, ELKM serves multiple roles: individuals, professionals, research institutions, and authorities. The model: **ELKM open-source** (knowledge layer) → **LexChain Egypt** (commercial product layer).

### Why Now — Data Is the Differentiator

When LLMs (GPT, Claude, Gemini) and infrastructure (Neo4j, AWS, Qdrant) converge, **the only remaining differentiator is data quality and structure**.

VentureBeat Pulse (June–July 2026, 101 companies):

- **57%** of companies reported "confident but wrong" AI agent answers due to missing or inconsistent context
- Rose to **68%** in July
- Companies with **governed context layers** reported *higher* error rates (78% vs 20%) — not because their systems are worse, but because they **see** errors that were previously invisible

**The problem is not the model — it is the data.** ELKM is the layer for Egyptian law.

### Why Egypt

A unique hybrid: Islamic Sharia, French civil tradition, judicial precedent, State Council fatwa, and the Supreme Constitutional Court. No off-the-shelf Western ontology fits. The only path is purpose-built.

### Global Momentum

Legal tech investment in 2025 exceeded **$5.99 billion**, up 22% year-over-year, with 14 rounds above $100M. Harvey AI raised $818M (valuation $8B). Clio raised $850M and acquired vLex for $1B. ELKM builds this layer for Egyptian law — **before anyone else does**.

### The Egyptian Gap

Egypt's Supreme Committee for Legislative Reform and National AI Council have made progress. The Egyptian Legal Portal holds 290,000+ laws and 100,000+ judgments. But it remains an **archive**, not a **knowledge layer**. ELKM fills this gap.

---

## 🚀 Quick Start (TL;DR)

```bash
# Clone the repo
git clone https://github.com/heshammalek/ELKM-Egyptian-Legal-Knowledge-Model.git
cd ELKM-Egyptian-Legal-Knowledge-Model

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> The unified export/build script is still under active development (see [Current Status](#-current-status)) — exact commands and paths will stabilize as `scripts/` is finalized.

---

## Core Challenges

| # | Challenge | Detail |
|---|-----------|--------|
| 1 | **No unified relational structure** | Egyptian laws interweave through total/partial repeal, amendment, addition, and delegation — with no structured, programmatically queryable source linking them |
| 2 | **Overlapping document types** | Laws, decree-laws, administrative decisions, legislative fatwas, judicial rulings, parliamentary minutes — each with different force logic, statuses, and issuing authorities, and easy to misclassify (e.g. every decree-law is titled "Presidential Decision," but not every presidential decision is a decree-law) |
| 3 | **Arabic legal-text complexity** | Diacritics, hamza variants, Arabic-Indic vs. Western numerals, legal tables — and hyper-precision at the character level, as in the passive/active distinction above |
| 4 | **The temporal dimension of force** | The same article can be in force, then suspended, then amended, then ruled unconstitutional — each state with its own independent start and end date, requiring precise tracking rather than a single snapshot |
| 5 | **Repeal vs. nullity vs. lapse** | Ending a text's effect doesn't always follow the same logic: prospective repeal, retroactive erasure, nullity from a fundamental defect, or automatic lapse (a decree-law not submitted to parliament within the constitutional deadline) — distinctions most legal archives ignore entirely |
| 6 | **Massive scale, scattered sources** | Thousands of documents spanning decades, from fragmented paper and digital sources, requiring a scalable data architecture instead of unstructured manual processing |
| 7 | **Colliding issuing authorities** | Entirely different administrative decisions can share the same number and year if issued by different authorities (a minister vs. a governor vs. an agency head) — without a structured authority registry, identifier collisions are inevitable |

---

## The Academic Gap

No comprehensive, publicly published Arabic legal ontology currently exists. Existing efforts are limited to digital legal dictionaries (term lists without relationships), incomplete research papers never implemented in software, or Western ontologies (FOLaw, LKIF, UFO-L) that don't map onto the Egyptian system.

**ELKM-Ontology** aims to be the first comprehensive, publicly published Arabic legal ontology — a scholarly contribution in its own right, publishable at venues such as **ICAIL** (International Conference on AI and Law), **JURIX**, and **LREC**. Concretely, ELKM aims to contribute:

1. The first comprehensive Arabic legal ontology.
2. A model for representing Arabic legal text as a knowledge graph.
3. A bridge between global standards and the Arabic legal context.
4. An Arabic legal Named Entity Recognition (NER) model.

### Why Egypt Specifically

The Egyptian legal system is a unique hybrid unlike any single reference model:

- **Islamic Sharia** — a principal source of legislation (Article 2 of the Constitution)
- **French civil law tradition** — underlying the civil and commercial fabric
- **Judicial precedent** — the Court of Cassation plays a broader interpretive role than its French counterpart
- **State Council fatwa** — a purely Egyptian institution with no Western equivalent
- **The Supreme Constitutional Court** — exercising posterior review of legislative constitutionality

Any off-the-shelf Western ontology collides with this specificity. The only viable path is a purpose-built one.

---

## Why ELKM Is Different (Competitive Context)

Products already exist in two shapes over Egyptian legislation: **Ansvar Systems** (Sweden), a globally leading company running the same MCP-server template across 46 jurisdictions (330,000+ national laws) for fast full-text search; and **Dike**, a commercial MENA API offering hybrid retrieval with citation-graph traversal. Both are strong retrieval layers. The real difference isn't coverage — it's the **layer**:

| | Ansvar (MCP) | Dike (API) | ELKM |
|---|---|---|---|
| **Nature** | Full-text search tool | Commercial retrieval + reasoning API | Open knowledge graph + ontology |
| **Structure** | Simple text indexing (FTS5 + BM25) | Hybrid dense + lexical index | Ontology + graph + explicit relationships |
| **Document type taxonomy** | Not documented — generic classification | Not documented publicly | Explicit `doc_types.json` with per-type force logic |
| **Relation type taxonomy** | Citation aggregation only | 5 types: cites / amends / repeals / implements / interprets | **26 named types** across 3 categories (DOC-DOC, DOC-ENT, DOC-POS), with constitutional basis per type |
| **Relation granularity** | Document-level | Document-level (per published docs) | **Article-level source** + target can be `article`, `entity`, `position`, or `whole_document` |
| **Relation metadata** | Not documented | Effective date (per published docs) | Structured `source`/`target` (doc_id, article_number, section, scope, entity_id, position_id) + `type_id` + `constitutional_basis` + `effective_date` + `confidence` + `reference_text` |
| **Status tracking** | Law-level | Per-document status; article-level history not described publicly | Article-level `status_history` with start/end dates |
| **Time-travel** | Not documented | Not documented | Computed at query time from effective_date — no static status field |
| **Citation integrity** | Not documented | Model citations checked against retrieved set | `doc_id` + source anchoring (planned in MCP layer) |
| **Provenance** | Not documented | Source ID + gazette date | source, extraction run, review status per record (being added) |
| **Openness** | Public repo (license not verified) | Closed API, key required | MIT code, CC BY 4.0 data, RDF export |

ELKM operates on a different layer — not by competing on text search, but by building a deeper one: a versioned, article-level, openly licensed model of how Egyptian legal texts affect each other over time. Dike provides a commercial retrieval and reasoning API with citation-graph traversal; ELKM complements this by offering an open knowledge layer underneath.


## Project Scope: Where the Code Ends

The **extraction and OCR** stage (converting image/PDF to text) runs through external language models following a documented extraction prompt, **entirely outside the project's codebase**. This is deliberate: ELKM's real value lies in the data architecture, ontology, relationship layer, and graph engine — not in an OCR engine that's replaceable by any newer model. Keeping extraction separate keeps the repo focused, lightweight on dependencies, and clear in scope for any contributor or reviewer.

```mermaid
flowchart TB
    subgraph external ["Outside the project — a documented process, not code"]
        ocr["Extraction + OCR<br/>via external language models<br/>per a documented prompt"]
    end

    subgraph project ["Inside the project — code and architecture"]
        direction TB

        norm["Normalization<br/>text_as_is → normalized_txt"]

        subgraph ontology ["Ontology Layer"]
            direction LR
            ont1["doc_types.json"]
            ont2["doc_codes.json"]
            ont3["subjects.json"]
            ont4["relation_types.json"]
            ont5["authority_types.json"]
        end

        subgraph structured ["Structured Data"]
            direction LR
            st1["normalized/json/{doc_id}.json<br/>(articles + instance_references)"]
            st2["relations/by_document/{instance_id}.json"]
        end

        subgraph exports ["Exports"]
            direction LR
            exp1["jsonl/"]
            exp2["markdown/"]
            exp3["sqlite/corpus.db"]
            exp4["parquet/"]
            exp5["neo4j/ (primary)"]
            exp6["rdf/"]
        end
    end

    ocr -.raw text.-> norm
    norm --> ontology
    ontology --> structured
    structured --> exports

    style ocr fill:#2a2a2a,stroke:#888,color:#ccc,stroke-dasharray: 5 5
    style norm fill:#1a2332,stroke:#4a90d9,color:#fff
    style ont1 fill:#1a2332,stroke:#4a90d9,color:#fff
    style ont2 fill:#1a2332,stroke:#4a90d9,color:#fff
    style ont3 fill:#1a2332,stroke:#4a90d9,color:#fff
    style ont4 fill:#1a2332,stroke:#4a90d9,color:#fff
    style ont5 fill:#1a2332,stroke:#4a90d9,color:#fff
    style st1 fill:#1a2332,stroke:#f5a623,color:#fff
    style st2 fill:#1a2332,stroke:#f5a623,color:#fff
    style exp1 fill:#1a2332,stroke:#7ed321,color:#fff
    style exp2 fill:#1a2332,stroke:#7ed321,color:#fff
    style exp3 fill:#1a2332,stroke:#7ed321,color:#fff
    style exp4 fill:#1a2332,stroke:#7ed321,color:#fff
    style exp5 fill:#1a2332,stroke:#7ed321,color:#fff
    style exp6 fill:#1a2332,stroke:#7ed321,color:#fff
```

---

## Repository Structure

```mermaid
flowchart TB
    subgraph root ["ELKM/"]
        corpus["corpus/<br/>Structured legal data"]
        ontology["ontology/<br/>Legal ontology definitions<br/>(elkm_core.ttl · elkm_core.owl<br/>elkm.ttl · shapes.ttl · context.jsonld)"]
        graphdir["graph/<br/>Neo4j import/build scripts<br/>(Python + Cypher)"]
        datasets["datasets/<br/>NER + legal terminology"]
        scripts["scripts/<br/>Processing, matching &<br/>RDF export/validation tools"]
        api["api/<br/>FastAPI application<br/>(serves /openapi.json and /studio)"]
        web["web/<br/>Static assets<br/>(studio/index.html)<br/>mounted into api/ via StaticFiles"]
        docs["docs/<br/>Documentation (README.ar.md)"]
        tests["tests/<br/>Test scripts"]
        arabicnlp["ArabicLegalNLP/<br/>Sibling Python library"]
    end

    web -.mounted into.-> api

    style corpus fill:#1a2332,stroke:#4a90d9,color:#fff
    style ontology fill:#1a2332,stroke:#4a90d9,color:#fff
    style graphdir fill:#1a2332,stroke:#7ed321,color:#fff
    style datasets fill:#1a2332,stroke:#9013fe,color:#fff
    style scripts fill:#1a2332,stroke:#888,color:#ccc
    style api fill:#1a2332,stroke:#4a90d9,color:#fff
    style web fill:#1a2332,stroke:#f5a623,color:#fff
    style docs fill:#1a2332,stroke:#888,color:#ccc
    style tests fill:#1a2332,stroke:#888,color:#ccc
    style arabicnlp fill:#1a2332,stroke:#9013fe,color:#fff
```

### `datasets/ner/` — Detailed Layout

```
datasets/ner/
├── readme.md
├── schema.json              Label definitions: LAW_REF, ARTICLE_REF, COURT,
│                             AUTHORITY, DATE_HIJRI_GREGORIAN, PENALTY,
│                             MONETARY_AMOUNT, LEGAL_PERSON
├── annotated/
│   ├── train.conll           80%
│   ├── dev.conll             10%
│   └── test.conll            10%
├── exports/
│   ├── ner.jsonl              HuggingFace format
│   └── ner.conll
└── legal-terms/               Legal terminology glossary for annotation
                                consistency (e.g. relative vs. absolute
                                nullity, civil vs. criminal effect of an
                                unconstitutionality ruling, imprisonment
                                vs. detention vs. hard labor) — a
                                disambiguation reference for annotators,
                                not general documentation, to prevent
                                inconsistent labeling across the dataset
```

The `NER_EXTRACTOR` and `ANNOTATION_HELPER` scripts read directly from `corpus/normalized/{type}/json` — never re-reading raw scans, to avoid duplicated work. Until a trained model exists, the MVP fallback is a set of regex rules grounded in a documented Arabic legal-drafting grammar (conditional sentences, cross-references, definitions, enumerations, issuing-authority attribution).

**ArabicLegalNLP** — a standalone sibling Python library for Arabic legal NLP (legal thesaurus, morphological analysis, agent/patient extraction, NER), called by ELKM as an external tool rather than built into it. It exists to defend Arabic linguistic specificity in the legal domain, developed as its own project on its own timeline.

---

## Corpus Structure (`corpus/`)

```mermaid
flowchart TB
    subgraph corpus ["corpus/"]
        direction TB

        subgraph raw ["raw/"]
            direction LR
            scanned["scanned/<br/>{category}/<br/>Original scanned images"]
            tai["text_as_is/<br/>{category}/<br/>Text as it appears<br/>(diacritics + hamza)<br/>for user display"]
        end

        subgraph normalized ["normalized/"]
            direction LR
            ntxt["txt/{category}/<br/>Normalized text<br/>for search speed"]
            njson["json/{category}/<br/>Full structured data"]
        end

        metadata["metadata/<br/>doc_types · doc_codes · subjects<br/>relation_types · authority_types<br/>documents_index"]
        relations["relations/by_document/<br/>{instance_id}.json"]

        subgraph exports ["exports/"]
            direction LR
            jsonl["jsonl/<br/>one file per document"]
            md["markdown/<br/>one file per document"]
            sqlite["sqlite/<br/>corpus.db<br/>(single central DB)"]
            parquet["parquet/<br/>one file per doc_type"]
            neodb["neo4j/<br/>nodes/ + relationships/"]
            rdf["rdf/<br/>{doc_type}.ttl · relations.ttl<br/>void.ttl"]
        end
    end

    raw --> normalized
    normalized --> exports
    metadata -.classification.-> normalized
    normalized -.feeds.-> relations
    relations -.links.-> exports

    style scanned fill:#1a2332,stroke:#4a90d9,color:#fff
    style tai fill:#1a2332,stroke:#4a90d9,color:#fff
    style ntxt fill:#1a2332,stroke:#4a90d9,color:#fff
    style njson fill:#1a2332,stroke:#4a90d9,color:#fff
    style metadata fill:#1a2332,stroke:#f5a623,color:#fff
    style relations fill:#1a2332,stroke:#f5a623,color:#fff
    style jsonl fill:#1a2332,stroke:#7ed321,color:#fff
    style md fill:#1a2332,stroke:#7ed321,color:#fff
    style sqlite fill:#1a2332,stroke:#7ed321,color:#fff
    style parquet fill:#1a2332,stroke:#7ed321,color:#fff
    style neodb fill:#1a2332,stroke:#7ed321,color:#fff
    style rdf fill:#1a2332,stroke:#7ed321,color:#fff
```

**Design rationale:**

- **`raw/scanned/{category}/`** and **`raw/text_as_is/{category}/`**: a unified category split that repeats identically inside `normalized/` — knowing a document's path in one folder tells you its path everywhere else instantly.
- **`text_as_is`** is a verbatim copy (the *Display Path*) for direct user display; **`normalized`** is a simplified copy (the *Search Path*) for **faster search and matching**, not display.
- **`metadata`**: near-static classification data — document types, authority codes, subject sectors, relation types, authority types, and the document index.
- **`relations/by_document/`**: every relation is stored as a separate JSON file keyed by its `instance_id`, and referenced directly from within the article it connects via `instance_references`.
- **`exports/`**: a fully derived layer with storage granularity that differs by format — **jsonl/markdown** one file per document, **sqlite** a single central database (`INSERT OR REPLACE` keyed by `doc_id` to prevent duplication), **parquet** one file per `doc_type` (a columnar format unsuited to thousands of small files), and **neo4j** as the primary output, with `nodes/` and `relationships/` for import.

### Article Index = the SQLite Export, Not a Separate File

With thousands of documents and hundreds of thousands of articles, a single `documents_index.json` becomes too heavy for article-level queries. The fix: an `articles_index` table inside the same SQLite export serves both purposes:

```sql
CREATE TABLE articles_index (
  doc_id TEXT, article_number INTEGER, doc_type TEXT,
  subjects TEXT, -- JSON array as text
  text_normalized TEXT
);
```

This is the direct foundation for queries like *"which articles reference Article 53 of the constitution"* as a single query, and it's the same foundation the future Dependency Map will be built on.

---

## Relationship Graph

```mermaid
graph LR
    L1["LAW-58-1937<br/>Penal Code"]
    L2["LAW-174-2025<br/>Amendment"]
    J1["JUDG-SCC-15-20<br/>Constitutionality Ruling"]
    L3["LAW-200-2024<br/>Reinstatement"]

    L2 -->|partial_repeal| L1
    J1 -->|unconstitutionality_ruling| L1
    L3 -->|reinstatement| L1

    style L1 fill:#1a2332,stroke:#4a90d9,color:#fff
    style L2 fill:#1a2332,stroke:#4a90d9,color:#fff
    style J1 fill:#1a2332,stroke:#d0021b,color:#fff
    style L3 fill:#1a2332,stroke:#9013fe,color:#fff
```

Every relation is recorded with full temporal and legal precision: relation type, effective date, extraction confidence level, and reference text. A relation's status at any given date is computed at query time from its effective_date — not stored as a static value. This is what makes time-travel queries possible: the same relation is "active" or "not yet in force" depending on when you ask.

Named relation types anchor the graph's semantics, mirroring the authorities that create legal truth:

| Relation | Meaning |
|---|---|
| `total_repeal` | Complete repeal of a law by a later law |
| `partial_repeal` | Repeal of a specific article or provision |
| `amendment` | Modification of an existing legal text |
| `addition` | Addition of new articles to an existing law |
| `unconstitutionality_ruling` | Supreme Constitutional Court ruling of unconstitutionality |
| `reinstatement` | Reinstatement of a repealed or suspended legal text |
| `preemptive_repeal` | Blanket repeal of any text conflicting with a new law (target unresolved until matched) |
| `referral` | Cross-reference from one text to another |
| `establishes` | Creation of a new entity or institution |

**Time-Travel queries** — retrieving the law exactly as it stood on a specific historical date — are a first-class capability the graph is designed to support, not an afterthought.

**Dependency Map** — *"which laws cite Article 53 of the constitution?"* — isn't a separate component, but a direct result of applying the NER model (specifically the `ARTICLE_REF` label) across the entire corpus to extract every explicit reference to one article inside another document's text, then building the graph from it.

---
## RDF Export (Linked Data)

The graph runs in Neo4j and is published as RDF so it can be linked, validated and cited by other projects. This turns ELKM from a private graph database into a piece of the global Linked Data web: each document, each article, and each relation becomes a dereferenceable URI that external tools can query, cross-reference, and reason over.

```
corpus/exports/rdf/
├── {doc_type}.ttl     one file per doc_type
├── relations.ttl      each relation is its own node (keyed by relation_id)
└── void.ttl           dataset description (license, version, counts)

ontology/
├── elkm.ttl           classes and properties (OWL/Turtle)
├── shapes.ttl         SHACL validation shapes
└── context.jsonld     JSON-LD context

scripts/
├── export_rdf.py      corpus/normalized/json -> Turtle
└── validate_rdf.py    SHACL report (human review gate before publishing)
```

**Modeling choices:**

- **URIs:** `<base>/id/{doc_id}`, `<base>/id/{doc_id}/art/{n}`, `<base>/rel/{relation_id}` — every document, article, and relation is individually addressable.
- **FRBR/ELI alignment:** `doc_id` = Work; each `version_from`/`version_to` = Expression (ELI/FRBR); `text_as_is` / `normalized` / `akn` = Manifestations. This separates the abstract law from its temporal versions and its textual representations.
- Relations are nodes, not bare edges: each relation carries its own type, effective date, extraction confidence, and reference text — so a repeal can itself be dated, questioned, or superseded. Judgment-specific metadata (e.g. retroactive effect) is carried only on relations whose source is a judgment, not as a universal field.
- **Reused standards:** ELI (legislation metadata), SKOS (subjects), PROV-O (source, extraction run, reviewer), Dublin Core (descriptive metadata). ELKM does not reinvent vocabulary where a W3C standard already exists.

**Base URI decision:** Use `w3id.org/elkm` as the canonical base. Submit a request to the W3ID repository to register it. Until registration is approved, use the `github.io` URL as a temporary base. This matters because every published URI must remain stable forever — changing the base later would break every external citation.

**Validation gate:** `validate_rdf.py` runs the SHACL shapes in `ontology/shapes.ttl` against the exported Turtle and produces a human-readable report. Publishing is blocked until the report is reviewed and approved. This is the quality gate before any RDF snapshot is released — the same role a human reviewer plays for the corpus itself.
---

## Segmented Identifier System

Every document gets a unique, human-readable, automatically generable identifier:

```
LAW-10-2000                     Law No. 10 of 2000
DL-20-2001                      Decree-Law No. 20 of 2001
ADM-PRES-30-2025                Presidential Decision No. 30 of 2025
ADM-MIN-AGRIC-5-2024            Minister of Agriculture Decision No. 5 of 2024
JUDG-SCC-15-20                  Supreme Constitutional Court, Case 15 / Judicial Year 20
JUDG-CASS-CIV-30-40             Court of Cassation, Civil Chamber, Appeal 30 / Judicial Year 40
```

`metadata/doc_codes.json` is a living, non-exhaustive registry of authorities and courts, holding **the identifier construction pattern itself** alongside it (segment order, which courts require a chamber code) — kept in one file as a single source of truth used by both the extraction prompt and any validation script, rather than separate documentation that risks drifting out of sync. The practical necessity of the registry: entirely different administrative decisions can share the same number and year if issued by different authorities (a minister vs. a governor), so distinguishing by authority is mandatory to avoid identifier collisions.

---

## Technical Stack

| Component | Technology | Role |
|---|---|---|
| Language | **Python 3.12+** | Core implementation language |
| Graph database | **Neo4j 5.x** | Stores and queries multi-hop relationships between texts, via Cypher |
| Vector search | **Qdrant** | Semantic/vector search over legal text (folder reserved; not yet exported) |
| Text search & indexing | **SQLite (central) + Elasticsearch** | Queryable document/article index, plus fast full-text search on normalized text |
| RDF export | **rdflib** | Serialize graph data to Turtle/RDF |
| RDF validation | **pySHACL** | Validate exported RDF against SHACL shapes |
| Ontology | **OWLReady2**, exported as OWL/Turtle (W3C-compatible) | doc_types.json / doc_codes.json / subjects.json / relation_types.json / authority_types.json define the applied classification (13 document types, 6 subject sectors) |
| Backend (planned) | **FastAPI** | Public API, data snapshots, or institutional integration |
| Containers & CI | **Docker + Compose, GitHub Actions, Pytest** | Reproducible environment, automated testing |
| LLM integration | **Anthropic/OpenAI SDKs directly** | Reasoning layer on top of the graph |

---

## Intellectual References

ELKM draws on academic, technical, and conceptual references — none adopted wholesale, each informing a specific design decision.

**Academic & Conceptual**

- **Harvard LIL** — document assembly line approach
- **Stanford CODEX** — "computable law" concept
- **Hohfeld** — legal relationship taxonomy
- **McCarty's LLD** — formal representation of legal norms
- **LKIF Core Ontology** — legal ontology approach (not its structure; incompatible with the Egyptian system)

**Standards & Frameworks**

- **Akoma Ntoso** — hierarchical document structure (concept, not standard)
- **LegalRuleML** — logical rule representation (concept, not format)
- **FOLaw** — legal ontology as a layer separate from text

**Technical Models**

- **Ansvar Systems** — full-text search is not enough; a deeper layer is needed
- **Harvey AI, CoCounsel** — LLMs need a structured knowledge base underneath

**Arabic Legal Ontologies (Prior Work)**

- **CrimAr (2017)** — Arabic legal ontology is possible, but narrow
- **Zaidi (2006)** — Arabic legal search needs semantic expansion

**Egyptian Legal Archives**

- **Manshurat (AUC)** — digital archives are a foundation, not an endpoint

---

## 📊 Current Status

> Indicative status — checkboxes will be updated as work progresses.

| Component | Planned | In Progress | Complete |
|---|---|---|---|
| Core Ontology | ⬜ | ⬜ | ⬜ |
| Corpus Architecture | ⬜ | ⬜ | ⬜ |
| Segmented Identifier System | ⬜ | ⬜ | ⬜ |
| Neo4j Import Script | ⬜ | ⬜ | ⬜ |
| Unified Export Script | ⬜ | ⬜ | ⬜ |
| RDF Export | ⬜ | ⬜ | ⬜ |
| Studio Page | ⬜ | ⬜ | ⬜ |
| NER Dataset | ⬜ | ⬜ | ⬜ |
| Public API | ⬜ | ⬜ | ⬜ |
| Arabic Documentation | ⬜ | ⬜ | ⬜ |

---

## Roadmap

**Corpus & Core Architecture**
- [ ] Build the core ontology (document types, subject sectors)
- [ ] Design the corpus architecture (raw / normalized / metadata / relations / exports)
- [ ] Segmented identifier system
- [ ] Complete extraction of the core body of laws in force
- [ ] Build out the full relationship layer and link it to Neo4j
- [ ] Unified export script (read JSON → automatically route to jsonl/markdown/sqlite/parquet/neo4j by `doc_type`)
- [ ] EBNF grammar for Arabic legal drafting patterns, and a regex-based MVP entity extractor grounded in it

**Enrichment & Analysis**
- [ ] Enrichment pass: classify each article by subject via `subjects.json`
- [ ] Dependency Map via NER `ARTICLE_REF` extraction
- [ ] Time-Travel query support (retrieve the law as it stood on a given date)

**Arabic Legal NER**
- [ ] Finalize the `schema.json` label definitions
- [ ] Build `NER_EXTRACTOR` and `ANNOTATION_HELPER`
- [ ] Annotate a training set (train/dev/test) and export in HuggingFace and CoNLL formats
- [ ] Research paper on the Arabic Legal NER dataset

**Infrastructure**
- [ ] MCP server on top of ELKM
- [ ] Docker containers
- [ ] GitHub repository setup and linking
- [ ] CI pipeline

**After Corpus Completion**
- [ ] Full ontology and methodology documentation, published as OWL/Turtle
- [ ] Public query interface (API / semantic search)
- [ ] **ArabicLegalNLP** — standalone Python library
- [ ] **LexChain Egypt** — commercial product layer

**RDF & Interoperability**
- [ ] Export RDF (Turtle) with SHACL validation report
- [ ] Register `w3id.org/elkm` base URI
- [ ] Publish `void.ttl` dataset description

**Developer Experience**
- [ ] Studio page at `/studio` (reads `/openapi.json`)
- [ ] Benchmark against Ansvar and Dike on identical queries
---

## 🤝 How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See `CONTRIBUTING.md` for detailed guidelines.

---

## Call for Collaboration

ELKM is building the **knowledge layer for Egyptian law** — the infrastructure that every legal AI application in Egypt will depend on. This is not just a research project; it is the foundation for a new generation of legal technology.

We are seeking partners who share this vision:

### For Academic Institutions

**What you get:**
- A pioneering research project publishable at **ICAIL**, **JURIX**, and **LREC**
- Graduate research opportunities in Arabic legal NLP and knowledge graphs
- The first published Arabic legal ontology — a scholarly contribution

**What you give:**
- Academic supervision of the ontology and methodology
- Publication support and peer review
- Graduate students to help build the corpus.
- 
- ### 💰 Funding
A seed grant would allow ELKM to move from prototype to a fully functional, published resource. Funding would cover:
- **Dedicated research time** for the project lead and research assistants.
- **Server and infrastructure costs** for Neo4j, PostgreSQL/Qdrant, and Elasticsearch.
- **Conference publication fees** (ICAIL, JURIX, LREC).
- **Annotation costs** for the Arabic Legal NER dataset.
- **Legal review fees** for expert validation of the ontology.
- **Establishment of a research entity** dedicated to the project.
- **Office setup and logistics** for the research team.

- ### For Technical and Legal Experts
As the project scales, we will need specialized expertise in areas such as:
- **Arabic NLP**
- **LLM Engineering**
- **Security**
- **Legal review** — judges, lawyers, and law professors to validate the ontology and the correctness of the relationships

If any of this fits what you do, opening an issue or reaching out is welcome.

---

## 🙏 Acknowledgments

- **Harvard LIL** for the Caselaw Access Project inspiration
- **CAMeL Lab** for Arabic NLP tools
- All contributors and reviewers who helped shape this project

---

## License

- **Code**: [MIT License](https://opensource.org/licenses/MIT)
- **Data**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

Fully open to the legal and technical community — contributions and reviews welcome.

---

<div align="center">

**"Egyptian law, mapped from enactment to the latest amendment."**

</div>
