<div align="center">

# ⚖️ ELKM — Egyptian Legal Knowledge Model

**The first comprehensive, open-source Arabic legal knowledge graph for Egyptian law**

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-prototype-orange.svg)]()
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1.svg)](https://neo4j.com/)
[![Language](https://img.shields.io/badge/language-Arabic%20%2F%20English-green.svg)]()
[![Docs](https://img.shields.io/badge/docs-mkdocs-1E90FF.svg)](https://heshammalek.github.io/ELKM/)

**[📘 Arabic version available in `README.ar.md`](README.ar.md)**

</div>

---

## 📑 Table of Contents
- [Why ELKM?](#why-elkm)
- [Core Challenges](#core-challenges)
- [The Academic Gap](#the-academic-gap)
- [Why ELKM Is Different](#why-elkm-is-different)
- [Project Scope](#project-scope-where-the-code-ends)
- [Repository Structure](#repository-structure)
- [Corpus Structure](#corpus-structure)
- [Relationship Graph](#relationship-graph)
- [Segmented Identifier System](#segmented-identifier-system)
- [Technical Stack](#technical-stack)
- [Inspired By](#inspired-by)
- [Roadmap](#roadmap)
- [Current Status](#-current-status)
- [Call for Collaboration](#call-for-collaboration)
- [How to Contribute](#-how-to-contribute)
- [Acknowledgments](#-acknowledgments)
- [License](#license)

---

## 🚀 Quick Start

> **Note:** This is a quick reference. For detailed setup, see the [Installation Guide](docs/installation.md).

```bash
# Clone the repository
git clone https://github.com/heshammalek/ELKM-Egyptian-Legal-Knowledge-Model.git
cd ELKM-Egyptian-Legal-Knowledge-Model

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the corpus builder (example)
python scripts/build_corpus.py

For Docker setup, see Docker Guide.

❓ Why ELKM?
Egyptian legal text is hyper‑precision: a single letter can redefine criminal liability. The passive "يُعاقَب" (liability falls on whoever is proven to have caused the harm) is not the same statement as the active "يُعاقِب" (an explicit actor is named) — one character, an entirely different legal consequence. Text alone doesn't represent legal truth, either: truth emerges from the text's interaction with the Constitutional Court (annulment), the Court of Cassation (binding interpretation), and the State Council (fatwa and annulment). Current legal search tools treat all of this as keyword matching.

ELKM solves this by treating Egyptian law not as a text archive, but as a knowledge graph — a relationship network connecting every text to everything that affected it or was affected by it, with full historical tracking of each article's status individually.

🧩 Core Challenges
#	Challenge	Detail
1	No unified relational structure	Egyptian laws interweave through total/partial repeal, amendment, addition, and delegation — with no structured, programmatically queryable source linking them
2	Overlapping document types	Laws, decree‑laws, administrative decisions, legislative fatwas, judicial rulings, parliamentary minutes — each with different force logic, statuses, and issuing authorities, and easy to misclassify (e.g. every decree‑law is titled "Presidential Decision," but not every presidential decision is a decree‑law)
3	Arabic legal‑text complexity	Diacritics, hamza variants, Arabic‑Indic vs. Western numerals, legal tables — and hyper‑precision at the character level, as in the passive/active distinction above
4	The temporal dimension of force	The same article can be in force, then suspended, then amended, then ruled unconstitutional — each state with its own independent start and end date, requiring precise tracking rather than a single snapshot
5	Repeal vs. nullity vs. lapse	Ending a text's effect doesn't always follow the same logic: prospective repeal, retroactive erasure, nullity from a fundamental defect, or automatic lapse (a decree‑law not submitted to parliament within the constitutional deadline) — distinctions most legal archives ignore entirely
6	Massive scale, scattered sources	Thousands of documents spanning decades, from fragmented paper and digital sources, requiring a scalable data architecture instead of unstructured manual processing
7	Colliding issuing authorities	Entirely different administrative decisions can share the same number and year if issued by different authorities (a minister vs. a governor vs. an agency head) — without a structured authority registry, identifier collisions are inevitable
🎓 The Academic Gap
No comprehensive, publicly published Arabic legal ontology currently exists. Existing efforts are limited to digital legal dictionaries (term lists without relationships), incomplete research papers never implemented in software, or Western ontologies (FOLaw, LKIF, UFO‑L) that don't map onto the Egyptian system.

ELKM‑Ontology aims to be the first comprehensive, publicly published Arabic legal ontology — a scholarly contribution in its own right, publishable at venues such as ICAIL (International Conference on AI and Law), JURIX, and LREC. Concretely, ELKM aims to contribute:

The first comprehensive Arabic legal ontology.

A model for representing Arabic legal text as a knowledge graph.

An EBNF grammar for Arabic legal syntax — currently non‑existent anywhere.

A bridge between global standards (Akoma Ntoso, LegalRuleML) and the Arabic legal context.

An Arabic legal Named Entity Recognition (NER) model.

Why Egypt Specifically
The Egyptian legal system is a unique hybrid unlike any single reference model:

Islamic Sharia — a principal source of legislation (Article 2 of the Constitution)

French civil law tradition — underlying the civil and commercial fabric

Judicial precedent — the Court of Cassation plays a broader interpretive role than its French counterpart

State Council fatwa — a purely Egyptian institution with no Western equivalent

The Supreme Constitutional Court — exercising posterior review of legislative constitutionality

Any off‑the‑shelf Western ontology collides with this specificity. The only viable path is a purpose‑built one.

🚀 Why ELKM Is Different (Competitive Context)
Products already exist offering fast full‑text search over Egyptian legislation — most notably Ansvar Systems (Sweden), a globally leading company running the same MCP‑server template across 80+ countries (SQLite + FTS5). The real difference isn't coverage — it's the layer:

Traditional full‑text search tools	ELKM
Structure	Simple text indexing	Ontology + graph + explicit relationships
Depth	Generic classification, no fine‑grained typing	Distinguishes decree‑law from administrative decision, fatwa binding basis (Art. 66), per‑article status over time
Scope	Usually statutes only	13 document types (including rulings, fatwas, minutes, academic doctrine)
Nature	Repeatable technical template across dozens of countries (breadth)	A deep research project dedicated to the Egyptian legal system specifically (depth)
ELKM aims to intellectually and technically surpass this model — not by competing on the same layer, but by building a deeper one (legal reasoning and a relationship graph) for which no real equivalent currently exists for Egyptian law. Tools like Harvey AI and CoCounsel demonstrate the same lesson from the other direction: powerful LLMs still need a structured knowledge base underneath them to reason reliably over law. ELKM aims to be that base — an open Egyptian equivalent of what Westlaw provides commercially, but published.

🧭 Project Scope: Where the Code Ends
The extraction and OCR stage (converting image/PDF to text) runs through external language models following a documented extraction prompt, entirely outside the project's codebase. This is deliberate: ELKM's real value lies in the data architecture, ontology, relationship layer, and graph engine — not in an OCR engine that's replaceable by any newer model. Keeping extraction separate keeps the repo focused, lightweight on dependencies, and clear in scope for any contributor or reviewer.

🗂️ Repository Structure
text
ELKM/
├── api/                    # Query interface (planned)
├── ArabicLegalNLP/         # Standalone NLP library (external tool)
├── corpus/                 # Structured legal data
│   ├── raw/                # scanned/ + text_as_is/
│   ├── normalized/         # txt/ + json/
│   ├── metadata/           # doc_types, subjects, id_codes
│   ├── relations/          # Flat relation store
│   ├── diff/               # Version comparisons
│   └── exports/            # jsonl, markdown, akn, sqlite, parquet, neo4j
├── datasets/               # NER + legal terminology
│   └── ner/
│       ├── schema.json
│       ├── annotated/
│       ├── exports/
│       └── legal-terms/
├── docs/                   # Documentation
├── graph/                  # Neo4j import/build scripts
├── ontology/               # Legal ontology definitions
├── scripts/                # Processing & matching tools
├── tests/                  # Unit tests
├── z-draft/                # Drafts and experiments
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── README.md
└── requirements.txt
🏛️ Corpus Structure (corpus/)
text
corpus/
├── raw/
│   ├── scanned/{category}/       # Original scanned images
│   └── text_as_is/{category}/    # Text as it appears (for display)
├── normalized/
│   ├── txt/{category}/           # Normalized text (for search)
│   └── json/{category}/          # Full structured data
├── metadata/                     # doc_types, subjects, id_codes
├── relations/                    # Flat store, keyed by relation_id
├── diff/{doc_type}/{doc_id}/     # Version comparisons
└── exports/                      # jsonl/, markdown/, akn/, sqlite/, parquet/, neo4j/
Design rationale:

text_as_is = Display Path (verbatim, with diacritics).

normalized/txt = Search Path (simplified, for faster matching).

exports/sqlite = central database with articles_index table for article‑level queries.

exports/neo4j = deferred until the relationship layer is complete.

🔗 Relationship Graph
Every relation is recorded with:

Relation type (e.g., DERIVED_FROM, IMPLEMENTS, ABROGATES, INTERPRETS, ANNULS)

Effective date

Extraction confidence level

Relation status (active, suspended, etc.)

Time‑Travel queries — retrieving the law as it stood on a specific historical date — are a first‑class capability.

Dependency Map — "which laws cite Article 53 of the constitution?" — is built by applying the NER model (ARTICLE_REF label) across the entire corpus.

🆔 Segmented Identifier System
Every document gets a unique, human‑readable, automatically generable identifier:

text
LAW-10-2000                     Law No. 10 of 2000
DECREE-LAW-20-2001              Decree-Law No. 20 of 2001
ADMIN-DECISION-PRES-30-2025     Presidential Decision No. 30 of 2025
ADMIN-DECISION-MIN-AGRIC-5-2024 Minister of Agriculture Decision No. 5 of 2024
JUDG-CONST-15-20                Supreme Constitutional Court, Case 15 / Judicial Year 20
JUDG-NAQD-CIVIL-30-40           Court of Cassation, Civil Chamber, Appeal 30 / Judicial Year 40
metadata/id_codes.json is the single source of truth for authority and court codes, preventing identifier collisions.

🛠️ Technical Stack
Component	Technology	Role
Language	Python 3.12+	Core implementation
Graph database	Neo4j 5.x	Multi‑hop relationship storage and queries (Cypher)
Vector search	pgvector → Qdrant	Semantic/vector search over legal text
Text search & indexing	SQLite + Elasticsearch	Document/article index, full‑text search
Arabic NLP	CAMeL Tools 1.5+	Morphological analysis, POS tagging, NER
Grammar parsing	Lark (EBNF parser)	Arabic legal‑drafting patterns (conditionals, cross‑references, definitions)
Ontology	OWLReady2, exported as OWL/Turtle	Document types, subjects, authority codes
Backend (planned)	FastAPI	Public API, data snapshots, institutional integration
Containers & CI	Docker + Compose, GitHub Actions, Pytest	Reproducible environment, automated testing
Documentation	MkDocs Material	Published project documentation
LLM integration	Anthropic/OpenAI SDKs	Reasoning layer on top of the graph
Export standards	Akoma Ntoso (AKN) + LegalRuleML	International legal‑document and rule‑representation standards
Extraction (outside code)	LLM‑powered extraction via a documented prompt	Converts image/PDF to text_as_is
💡 Inspired By
Harvard LIL — Caselaw Access Project and its document assembly line approach

Stanford CODEX — the "computable law" concept

Akoma Ntoso — UN's international XML standard for legal documents

LegalRuleML — standard for logically representing legal rules

LKIF Core Ontology — academic reference (not adopted directly)

Hohfeld's Fundamental Legal Conceptions — theoretical framework for legal relationship modeling

McCarty's LLD — framework for representing legal norms

Harvey AI, CoCounsel (Casetext) — lesson: powerful LLMs need a structured knowledge base to reason reliably over law

🗺️ Roadmap
Corpus & Core Architecture

☑ Build the core ontology (document types, subject sectors)
☑ Design the corpus architecture (raw / normalized / metadata / relations / diff / exports)
☑ Temporal article‑status tracking system (status_history)
☑ Segmented identifier system
□ Complete extraction of the core body of laws in force
□ Build out the full relationship layer and link it to Neo4j
□ Unified export script (read JSON → route to jsonl/sqlite/parquet/markdown/akn by doc_type)
□ EBNF grammar for Arabic legal drafting patterns (Lark), and a regex‑based MVP entity extractor
Enrichment & Analysis

□ Enrichment pass: classify each article by subject via subjects.json
□ Dependency Map via NER ARTICLE_REF extraction
□ Time‑Travel query support
Arabic Legal NER

□ Finalize schema.json label definitions
□ Build NER_EXTRACTOR and ANNOTATION_HELPER
□ Annotate a training set (train/dev/test) and export in HuggingFace and CoNLL formats
□ Research paper on the Arabic Legal NER dataset
Infrastructure

□ MCP server on top of ELKM
□ Docker containers
□ GitHub repository setup and linking
After Corpus Completion

□ Full ontology and methodology documentation, published as OWL/Turtle
□ Public query interface (API / semantic search)
□ ArabicLegalNLP — standalone Python library
□ LexChain Egypt — commercial product layer (ELKM + LLM + UI + search tools)
📊 Current Status
Project Phase: Prototype — Seeking Support

ELKM is currently in active prototype development. The core architecture, ontology, and data pipeline are designed and partially implemented. We are actively seeking academic, technical, and funding partners to accelerate development.

Component	Status
Core Ontology Design	✅ Complete (v1.0)
Corpus Architecture	✅ Complete
Segmented Identifier System	✅ Complete
Document Classification (types/sectors)	✅ Complete
Extraction Pipeline (OCR → raw text)	⏳ In Progress (external)
Normalization & JSON Conversion	🟡 In Progress (40%)
NER Dataset & Annotation	🟡 In Progress (10% annotated)
Neo4j Import Scripts	⏳ Planned
Relationship Layer	⏳ Planned
Public API	⏳ Planned
Docker Containerization	⏳ Planned
🤝 Call for Collaboration
ELKM is an open research effort, and it's stronger with the right partners:

Academic sponsorship — a university or research center to adopt ELKM as an official research project: academic supervision, publication opportunities (ICAIL, JURIX, LREC), and graduate students to help build the corpus.

Funding — a seed grant to cover dedicated research time, server costs, and conference publication fees.

Technical partnership — help building the OCR pipeline for scanned legal texts, and UI development for the future LexChain Egypt product layer.

Legal review — an Egyptian legal expert (judge, lawyer, or law professor) to review the ontology's accuracy in representing the Egyptian legal system and the correctness of the relationships and interpretations in the knowledge model.

If any of this fits what you do, opening an issue or reaching out is welcome.

👥 How to Contribute
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add some amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

See CONTRIBUTING.md for detailed guidelines.

🙏 Acknowledgments
Harvard LIL for the Caselaw Access Project inspiration

Akoma Ntoso for the legal document standard

CAMeL Lab for Arabic NLP tools

All contributors and reviewers who helped shape this project

📄 License
Code: MIT License

Data: CC BY 4.0

Fully open to the legal and technical community — contributions and reviews welcome.

<div align="center">
"Egyptian law, mapped from enactment to the latest amendment."

</div> ```
