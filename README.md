# Legal RAG System — EU Law Question Answering

> An intelligent legal assistant powered by Retrieval-Augmented Generation (RAG), built on official EUR-Lex documents and running entirely on local infrastructure.

---

## Overview

This project implements a **domain-specific RAG pipeline** specialized in European Union law. Given a natural language question, the system retrieves the most semantically relevant legal articles from a curated knowledge base of official EU legislation and generates a precise, source-cited answer using a local language model.

The system is designed with a core principle in mind: **every answer must be grounded in a verifiable legal source**. No hallucinations, no guesswork — only answers anchored in official EUR-Lex documents.

---

## Demo

```
User    : What are my rights if a company refuses to delete my data?

Answer  : Under EU law, you have the right to lodge a complaint with a
          supervisory authority and seek an effective judicial remedy
          against a controller or processor.

Source  : Article 77 & 79 (Right to lodge a complaint), GDPR — EUR-Lex
```

---

## Why This Project Matters

Legal information is notoriously difficult to navigate. EU regulations run into hundreds of pages of dense legal language. This system makes EU law **accessible to anyone** — no legal background required.

This project is a full end-to-end implementation of the same core architecture, built from scratch.

---

## Architecture

The system is split into two phases:

### Phase 1 — Indexing (run once)

```
EUR-Lex PDFs → Article-level chunking → Semantic embeddings → ChromaDB (persistent)
```

1. Official EU legislation is downloaded as PDFs from EUR-Lex
2. Each document is parsed and split article by article using regex on the legal structure
3. Each article is encoded into a 384-dimensional semantic vector using `all-MiniLM-L6-v2`
4. All vectors are stored in ChromaDB with metadata (article number, title, source document)

### Phase 2 — Inference (at every question)

```
User question → Embedding → ChromaDB cosine search → Top 3 articles → Phi-3 → Answer + source
```

1. The user's question is encoded into the same semantic space
2. ChromaDB performs cosine similarity search to find the 3 most relevant articles
3. The question and retrieved articles are sent to Phi-3 via Ollama
4. Phi-3 generates a grounded answer with the exact article citation

---

## Knowledge Base

All documents are sourced directly from **EUR-Lex**, the official EU law database:

| Document | CELEX ID | Coverage |
|---|---|---|
| General Data Protection Regulation (GDPR) | 32016R0679 | Data privacy, user rights, controller obligations |
| AI Act | 32024R1689 | AI system classification, obligations, prohibited uses |
| Digital Services Act (DSA) | 32022R2065 | Platform liability, illegal content, user rights online |
| Consumer Rights Directive | 32011L0083 | Right of withdrawal, guarantees, refunds |
| Working Time Directive | 32003L0088 | Working hours, rest periods, annual leave |

---

## Tech Stack

| Component | Technology | Role |
|---|---|---|
| PDF extraction | PyMuPDF (`fitz`) | Parse official EUR-Lex PDFs article by article |
| Chunking | Regex on legal structure | Split by article with number and title as metadata |
| Embedding model | `all-MiniLM-L6-v2` | Encode text into 384-dim semantic vectors |
| Vector database | ChromaDB (persistent) | Store and search vectors with cosine similarity |
| Language model | Phi-3 via Ollama | Generate grounded answers locally — no API, no cost |
| Interface | Gradio | Interactive web UI at localhost:7860 |

---

## Project Structure

```
rag_legal_2/
├── app.py                  
├── rag/
│   ├── __init__.py        
│   ├── ingestion.py        
│   ├── retrieval.py       
│   └── generation.py      
├── legal_rag_db/          
├── requirements.txt
└── README.md
```

Each file has a single responsibility:
- **Change the data source** → edit `ingestion.py` only
- **Change the search logic** → edit `retrieval.py` only
- **Change the LLM** → edit `generation.py` only
- **Change the interface** → edit `app.py` only

---

## Key Design Decisions

**Why RAG instead of a standalone LLM?**
A standalone LLM answers from memory and can hallucinate — especially on specific legal details like article numbers or exact obligations. RAG forces the model to read the actual legal text before answering, making every response verifiable.

**Why ChromaDB instead of FAISS?**
FAISS stores the index in RAM and requires rebuilding on every session. ChromaDB persists to disk and uses cosine similarity, which is better suited for semantic text search than Euclidean distance.

**Why Phi-3 instead of an extractive model like RoBERTa?**
Extractive models like `roberta-base-squad2` can only find an exact text span — they fail on paraphrased or complex questions. Phi-3 is a generative model that understands the question semantically and formulates a coherent answer even when the wording differs from the source text. Running it locally via Ollama also ensures no data leaves the machine — critical for a system handling legal information.

**Why EUR-Lex instead of Wikipedia?**
Wikipedia summarizes and paraphrases legal texts. EUR-Lex publishes the official, legally valid versions. For a legal assistant, citing "Article 5, GDPR — EUR-Lex" is authoritative; citing Wikipedia is not.

**Why article-level chunking instead of fixed token windows?**
EU legal texts are naturally structured by articles, each covering a specific, self-contained legal concept. Article-level chunking preserves this semantic coherence — a fixed token window would often split an article mid-sentence, losing context and making retrieval less precise.

---

## Limitations & Future Work

**Current limitations:**
- Knowledge base covers 5 documents (~150 articles) — does not represent the full body of EU law
- Phi-3 is a small model (2.2GB) — complex multi-article reasoning may be imprecise
- No cross-article linking — some answers require reading multiple related articles together

**Planned improvements:**
- Add a reranking step (cross-encoder) to improve passage selection quality before generation
- Expand the knowledge base to cover more EUR-Lex documents and directives
- Implement cross-article reference resolution for questions spanning multiple legal texts
- Add multilingual support (French, Arabic) using a multilingual embedding model

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/rag-juridique.git
cd rag-juridique

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Ollama and pull Phi-3
# Download Ollama from https://ollama.com
ollama pull phi3

# 4. Download EUR-Lex source documents
# Place the following PDFs in the project root directory:
# CELEX_32016R0679_EN_TXT.pdf  (GDPR)
# CELEX_32024R1689_EN_TXT.pdf  (AI Act)
# CELEX_32022R2065_EN_TXT.pdf  (Digital Services Act)
# CELEX_32011L0083_EN_TXT.pdf  (Consumer Rights Directive)
# CELEX_32003L0088_EN_TXT.pdf  (Working Time Directive)
# Download from: https://eur-lex.europa.eu

# 5. Build the knowledge base (run once)
python -c "from rag.ingestion import construire_base; construire_base()"

# 6. Launch the interface
python app.py
```

Then open `http://localhost:7860` in your browser.

---

## Usage

Example questions to try:
- *"What does GDPR protect?"*
- *"How many hours can an employee work per week in the EU?"*
- *"What are the obligations of online platforms under the DSA?"*
- *"What is prohibited under the EU AI Act?"*
- *"Can I return a product I bought online?"*
- *"What are my rights if a company refuses to delete my data?"*

---

## Requirements

```
pymupdf
sentence-transformers
chromadb
transformers
torch
datasets
numpy
wikipedia-api
beautifulsoup4
requests
SPARQLWrapper
gradio
ollama
```

---

## About

Built as part of an AI module project. The goal was to go beyond a generic chatbot and build a **domain-specific, source-grounded, fully local** RAG system on a real-world use case with genuine practical value.

The full pipeline — from PDF ingestion to legal answer generation with source citation — was designed, implemented, and debugged end-to-end, including resolving non-trivial challenges such as EUR-Lex anti-scraping measures, vector database imbalance across documents, article-level chunking from complex PDF structures, and extractive vs. generative model trade-offs.

---

*Built with PyMuPDF · ChromaDB · Sentence Transformers · Phi-3 · Ollama · Gradio*