"""
Advanced RAG Engine for Basel III Regulatory Reporting
Supports: Hybrid Search, Re-ranking, Multi-query expansion, HyDE
"""

from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Any

# ── LangChain imports ─────────────────────────────────────────────────────────
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

# Safe imports with fallbacks for different langchain versions
try:
    from langchain.retrievers.ensemble import EnsembleRetriever
    _HAS_ENSEMBLE = True
except ImportError:
    _HAS_ENSEMBLE = False

try:
    from langchain.retrievers.multi_query import MultiQueryRetriever
    _HAS_MULTI_QUERY = True
except ImportError:
    _HAS_MULTI_QUERY = False
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import streamlit as st


BASEL3_SYSTEM_PROMPT = """You are an expert Basel III regulatory advisor with deep knowledge of:
- Capital Adequacy Requirements (CET1, AT1, Tier 2 capital)
- Liquidity Coverage Ratio (LCR) and Net Stable Funding Ratio (NSFR)
- Leverage Ratio Framework
- Credit Risk (Standardised and IRB Approaches)
- Market Risk (FRTB - Fundamental Review of the Trading Book)
- Operational Risk (Standardised Approach SA-OR)
- Pillar 2 Supervisory Review and Pillar 3 Disclosure
- BCBS regulatory guidelines and national implementations

Use ONLY the provided regulatory context to answer questions. 
Be precise, cite specific ratios and thresholds, and flag where national 
implementations may differ from BCBS minimums.

If the answer is not in the context, clearly state that and suggest where 
the user might find it (e.g., specific BCBS publications).

Context:
{context}

Question: {question}

Provide a structured, accurate answer with:
1. Direct answer to the question
2. Relevant regulatory thresholds/ratios if applicable
3. Key caveats or implementation notes
4. Reference to source sections where possible
"""


DEMO_CORPUS = [
    Document(
        page_content="""Basel III Capital Requirements - Common Equity Tier 1 (CET1)

The Basel III framework requires banks to maintain minimum capital ratios. The minimum 
Common Equity Tier 1 (CET1) capital ratio is 4.5% of Risk-Weighted Assets (RWA).

In addition to the minimum CET1 requirement, banks must maintain:
- Capital Conservation Buffer: 2.5% of RWA (composed of CET1 capital)
- Countercyclical Capital Buffer: 0% to 2.5% of RWA (jurisdiction-specific)
- G-SIB Surcharge: 1% to 3.5% additional CET1 for Global Systemically Important Banks

Total minimum CET1 including conservation buffer: 7.0% of RWA

The total capital requirement (Tier 1 + Tier 2) minimum is 8.0% of RWA.
Tier 1 minimum: 6.0% of RWA (of which CET1 must be at least 4.5%)
Additional Tier 1 (AT1): up to 1.5% of RWA

Capital instruments eligible for CET1 include: ordinary shares, share premium, 
retained earnings, accumulated other comprehensive income (AOCI), and other disclosed reserves.

Regulatory deductions from CET1 include: goodwill, intangible assets, deferred tax assets, 
significant investments in financial institutions, and shortfalls in provisions.""",
        metadata={"source": "BCBS Basel III Framework", "section": "Capital Requirements", "page": 1}
    ),
    Document(
        page_content="""Liquidity Coverage Ratio (LCR) - Basel III Liquidity Standards

The Liquidity Coverage Ratio (LCR) requires banks to hold sufficient High-Quality Liquid 
Assets (HQLA) to cover net cash outflows over a 30-day stress period.

Formula: LCR = Stock of HQLA / Total Net Cash Outflows over 30 days ≥ 100%

HQLA Classification:
Level 1 Assets (no haircut):
- Coins and banknotes
- Central bank reserves
- Marketable securities from sovereigns/central banks with 0% risk weight
- No cap on Level 1 assets

Level 2A Assets (15% haircut, max 40% of HQLA):
- Sovereign/central bank securities with 20% risk weight
- Non-financial corporate bonds rated AA- or higher
- Covered bonds rated AA- or higher

Level 2B Assets (25-50% haircut, max 15% of HQLA):
- RMBS rated AA or higher (25% haircut)
- Non-financial corporate bonds rated A+ to BBB- (50% haircut)
- Equity securities not issued by financial institutions (50% haircut)

Cash Outflow Rates (stressed scenario):
- Retail deposits (stable): 3% run-off rate
- Retail deposits (less stable): 10% run-off rate  
- Unsecured wholesale funding: 25-100% run-off rate
- Secured funding: 0-25% run-off rate depending on collateral quality

Phased implementation: LCR minimum was 60% in 2015, rising 10% per year to 100% by 2019.""",
        metadata={"source": "BCBS Basel III: LCR and Liquidity Risk Monitoring Tools", "section": "LCR", "page": 1}
    ),
    Document(
        page_content="""Net Stable Funding Ratio (NSFR) - Structural Liquidity Requirement

The Net Stable Funding Ratio (NSFR) requires banks to maintain a stable funding profile 
in relation to their assets and off-balance sheet activities.

Formula: NSFR = Available Stable Funding (ASF) / Required Stable Funding (RSF) ≥ 100%

Available Stable Funding (ASF) Factors:
- Tier 1 and Tier 2 capital instruments: 100% ASF factor
- Preferred stock and liabilities > 1 year maturity: 100% ASF factor
- Stable retail deposits and term deposits < 1 year: 95% ASF factor
- Less stable retail deposits < 1 year: 90% ASF factor
- Wholesale funding < 6 months from non-financial corporates: 50% ASF factor
- All other liabilities and equity not included above: 0% ASF factor

Required Stable Funding (RSF) Factors:
- Unencumbered Level 1 HQLA: 5% RSF factor
- Unencumbered Level 2A assets: 15% RSF factor  
- Unencumbered Level 2B assets: 50% RSF factor
- Unencumbered performing loans (residential mortgages, risk weight ≤ 35%): 65% RSF factor
- Other unencumbered performing loans: 85% RSF factor
- All other assets: 100% RSF factor

The NSFR became a minimum standard from 1 January 2018 under BCBS final rules.
National regulators may apply stricter requirements.""",
        metadata={"source": "BCBS Basel III: NSFR", "section": "NSFR", "page": 1}
    ),
    Document(
        page_content="""Basel III Leverage Ratio Framework

The Leverage Ratio provides a non-risk-based backstop measure to supplement risk-based 
capital requirements.

Formula: Leverage Ratio = Tier 1 Capital / Exposure Measure ≥ 3%

The Exposure Measure includes:
1. On-balance sheet exposures (at accounting value, net of specific provisions)
2. Derivative exposures (using SA-CCR or current exposure method)
3. Securities Financing Transaction (SFT) exposures
4. Off-balance sheet items (credit conversion factors applied)

G-SIB Buffer:
Global Systemically Important Banks (G-SIBs) must maintain a leverage ratio buffer 
equal to 50% of their risk-based G-SIB surcharge.
For a G-SIB with a 2% surcharge: minimum leverage ratio = 3% + 1% = 4%

Basel III leverage ratio minimum of 3% became effective January 2018.
The Basel III reforms (Basel IV) finalized in December 2017 require:
- Minimum leverage ratio: 3% of Tier 1 capital
- G-SIB surcharge buffer applied from January 2022
- Output floor: 72.5% of standardised RWA (phased in from 2025 to 2030)

Key differences from risk-based capital:
- Does not depend on internal models or risk weights
- Provides a floor to prevent excessive leverage
- Particularly constraining for low-risk business models (e.g., repo, mortgage lending)""",
        metadata={"source": "BCBS Leverage Ratio Framework", "section": "Leverage Ratio", "page": 1}
    ),
    Document(
        page_content="""Credit Risk - Standardised Approach (SA) under Basel III

The Standardised Approach (SA) assigns risk weights to credit exposures based on 
external credit ratings and asset class.

Sovereign Exposures:
- AAA to AA-: 0% risk weight
- A+ to A-: 20% risk weight
- BBB+ to BBB-: 50% risk weight
- BB+ to BB-: 100% risk weight
- B+ to B-: 100% risk weight (150% from B-)
- Below B-: 150% risk weight
- Unrated: 100% risk weight

Bank Exposures (External Credit Risk Assessment Approach - ECRA):
- AAA to AA-: 20% risk weight
- A+ to A-: 30% risk weight
- BBB+ to BBB-: 50% risk weight
- BB+ to B-: 100% risk weight
- Below B-: 150% risk weight

Corporate Exposures:
- AAA to AA-: 20% risk weight
- A+ to A-: 50% risk weight
- BBB+ to BBB-: 75% risk weight
- BB+ to BB-: 100% risk weight
- Below BB-: 150% risk weight
- Unrated: 100% risk weight

Residential Real Estate:
- Loan-to-Value ≤ 50%: 20% risk weight
- LTV 50-60%: 25% risk weight
- LTV 60-80%: 30% risk weight
- LTV 80-90%: 40% risk weight
- LTV 90-100%: 50% risk weight
- LTV > 100%: 70% risk weight

SME exposures qualifying for retail treatment: 75% risk weight
Defaulted exposures (unsecured): 150% risk weight""",
        metadata={"source": "BCBS CRE: Credit Risk - Standardised Approach", "section": "Credit Risk SA", "page": 1}
    ),
    Document(
        page_content="""Market Risk - Fundamental Review of the Trading Book (FRTB)

The FRTB (Basel III market risk framework, finalised 2019) replaced the 1996 Market 
Risk Amendment and introduces major structural changes.

Revised Internal Models Approach (IMA):
- Expected Shortfall (ES) at 97.5% confidence replaces VaR at 99% confidence
- Stressed calibration period (minimum 1 year, must include period of stress)
- Non-modellable risk factors (NMRFs) subject to stress scenario capital add-on
- P&L attribution test: IMA approval requires passing daily back-testing at desk level
- Liquidity horizons: 10, 20, 40, 60, 120 days depending on risk factor category

Revised Standardised Approach (SA):
- Sensitivity-based method (SBM): Delta, Vega, Curvature charges
- Default Risk Charge (DRC): captures jump-to-default risk
- Residual Risk Add-On (RRAO): for exotic instruments

Sensitivities-Based Method Risk Charges:
General Interest Rate Risk (GIRR): 
  - Shock scenarios applied to yield curve tenors
  - Correlation between tenors: intra-bucket correlation ρ = e^(-α|Ti-Tj|/min(Ti,Tj))
  
Foreign Exchange Risk:
  - 15% delta risk weight for most FX pairs
  - 7.5% for currencies in pegged arrangements
  
Equity Risk:
  - Large cap: 55% delta risk weight
  - Small cap: 70% delta risk weight
  - Sector correlations: 14-39%

Implementation: FRTB SA/IMA required from 1 January 2025 (extended from Jan 2022).
Banks must report SA capital requirements regardless of IMA approval status.""",
        metadata={"source": "BCBS MAR: Market Risk", "section": "FRTB", "page": 1}
    ),
    Document(
        page_content="""Operational Risk - New Standardised Approach (SA-OR)

Basel III's revised operational risk framework (finalised December 2017) replaces 
all previous approaches (BIA, TSA, AMA) with a single non-model-based method.

Business Indicator (BI) Components:
1. Interest, Leases and Dividends Component (ILDC)
   = |Net Interest Income| + |Net Lease Income| + Dividend Income
   
2. Services Component (SC)
   = Max(Fee Income, Fee Expense) + Max(Other Operating Income, Other Operating Expense)
   
3. Financial Component (FC)
   = |Net P&L Trading Book| + |Net P&L Banking Book|

Business Indicator (BI) = ILDC + SC + FC

BI Ranges and Marginal Coefficients (αi):
- BI Bucket 1 (≤ €1bn): α = 12%
- BI Bucket 2 (€1bn – €30bn): α = 15%  
- BI Bucket 3 (> €30bn): α = 18%

Business Indicator Component (BIC):
- BIC = Σ αi × BI marginal amount in each bucket

Internal Loss Multiplier (ILM):
- ILM = ln(exp(1) - 1 + (Loss Component / BIC)^0.8)
- Loss Component = 15 × average annual operational risk losses over 10 years
- National supervisors may set ILM = 1 (i.e., not use historical loss data)

Operational Risk Capital (ORC):
- ORC = BIC × ILM (or BIC if ILM not applied)

Implementation date: 1 January 2023 (extended due to COVID-19 from Jan 2022)
Replaces: Basic Indicator Approach, Standardised/Alternative Standardised, Advanced Measurement Approach""",
        metadata={"source": "BCBS OPE: Operational Risk", "section": "Operational Risk SA-OR", "page": 1}
    ),
    Document(
        page_content="""Pillar 2 and Pillar 3 - Supervisory Review and Market Discipline

PILLAR 2 - Supervisory Review Process (SRP)

The Supervisory Review Process has four key principles:

Principle 1: Banks should have a process for assessing overall capital adequacy 
relative to their risk profile (ICAAP - Internal Capital Adequacy Assessment Process)

Principle 2: Supervisors should review banks' internal assessments and take 
supervisory action where appropriate (SREP - Supervisory Review and Evaluation Process)

Principle 3: Supervisors should expect banks to operate above the minimum regulatory 
capital ratios. Pillar 2 add-ons may include:
- Pillar 2 Requirement (P2R): mandatory binding additional capital
- Pillar 2 Guidance (P2G): non-binding supervisory expectation
- Stress-testing based capital buffers

Principle 4: Supervisors should intervene early to prevent capital falling below 
minimum levels supporting the risk characteristics of the bank.

Key Pillar 2 Risks Assessed:
- Concentration risk (single-name, sector, geographic)
- Interest Rate Risk in the Banking Book (IRRBB)
- Liquidity and funding risk beyond LCR/NSFR
- Pension obligation risk
- Residual risk (incomplete risk mitigation)
- Business model risk and strategic risk

PILLAR 3 - Market Discipline and Disclosure Requirements

Disclosure Frequency Requirements:
- Annual: Full Pillar 3 report (quantitative and qualitative)
- Semi-annual: Key metrics, RWA, capital composition
- Quarterly: Key metrics table, Capital adequacy, Leverage ratio

Key Disclosure Templates include:
- KM1: Key metrics summary
- OV1: Overview of RWA by risk type
- CC1: Composition of regulatory capital
- CR1-CR10: Credit risk exposures and RWA
- MR1-MR4: Market risk under SA and IMA
- LIQ1-LIQ2: LCR and NSFR quantitative disclosures""",
        metadata={"source": "BCBS Pillar 2/3 Framework", "section": "Pillar 2 & 3", "page": 1}
    ),
]


class Basel3RAGEngine:
    """Advanced RAG engine with hybrid search, multi-query expansion and re-ranking."""

    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        os.environ["OPENAI_API_KEY"] = openai_api_key

        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

        self.vectorstore: FAISS | None = None
        self.bm25_retriever: BM25Retriever | None = None
        self.docs: list[Document] = []

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " "],
        )

    # ── Ingestion ─────────────────────────────────────────────────────────────

    def load_demo_corpus(self) -> int:
        """Load built-in Basel III demo documents."""
        chunks = self.text_splitter.split_documents(DEMO_CORPUS)
        self._build_indexes(chunks)
        return len(chunks)

    def load_documents(self, file_paths: list[str], merge_with_existing: bool = False) -> int:
        """Load and index user-uploaded documents.
        
        Args:
            file_paths: List of file paths to load.
            merge_with_existing: If True, merges with already-loaded docs (e.g. demo corpus).
                                  If False (default), replaces the index with only these docs.
        """
        raw_docs: list[Document] = []
        for path in file_paths:
            ext = Path(path).suffix.lower()
            try:
                if ext == ".pdf":
                    raw_docs.extend(PyPDFLoader(path).load())
                elif ext == ".docx":
                    raw_docs.extend(Docx2txtLoader(path).load())
                elif ext == ".txt":
                    loaded = False
                    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
                        try:
                            raw_docs.extend(TextLoader(path, encoding=enc).load())
                            loaded = True
                            break
                        except (UnicodeDecodeError, Exception):
                            continue
                    if not loaded:
                        # Binary fallback: decode with latin-1 (covers all 256 bytes)
                        try:
                            text = Path(path).read_bytes().decode("latin-1", errors="replace")
                            raw_docs.append(Document(page_content=text, metadata={"source": path}))
                            loaded = True
                        except Exception:
                            pass
                    if not loaded:
                        st.warning(f"Could not decode {path} with any known encoding.")
                else:
                    st.warning(f"Unsupported file type: {ext}")
            except Exception as e:
                st.warning(f"Could not load {path}: {e}")

        if not raw_docs:
            return 0

        chunks = self.text_splitter.split_documents(raw_docs)

        if merge_with_existing and self.docs:
            # Merge with existing docs (e.g. demo corpus + PDF together)
            all_chunks = self.docs + chunks
        else:
            # Isolated — only the uploaded files, no demo corpus bleed-through
            all_chunks = chunks

        self._build_indexes(all_chunks)
        return len(chunks)

    def _build_indexes(self, chunks: list[Document]):
        """Build FAISS vector index and BM25 keyword index."""
        self.docs = chunks
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        self.bm25_retriever = BM25Retriever.from_documents(chunks)
        self.bm25_retriever.k = 5

    # ── Query ─────────────────────────────────────────────────────────────────

    def query(
        self,
        question: str,
        retrieval_mode: str = "hybrid",
        top_k: int = 5,
    ) -> dict[str, Any]:
        if not self.vectorstore:
            raise RuntimeError("Knowledge base not loaded.")

        # 1. Retrieve documents
        docs = self._retrieve(question, retrieval_mode, top_k)

        # 2. Re-rank by relevance scoring + compute overlap scores
        docs, scores = self._rerank_with_scores(question, docs)
        docs = docs[:top_k]
        scores = scores[:top_k]

        # 3. Confidence score — average keyword overlap of top-K chunks (0.0–1.0)
        avg_score = sum(scores) / len(scores) if scores else 0.0
        if avg_score >= 0.35:
            confidence = "HIGH"
        elif avg_score >= 0.15:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        # 4. Build context — inject low-confidence warning if needed
        context = self._build_context(docs)
        if confidence == "LOW":
            context = (
                "⚠️ WARNING: The retrieved chunks have LOW relevance to this question. "
                "The topic may not be present in the loaded documents. "
                "Answer only from what is explicitly stated below, or state that the "
                "information is not available.\n\n" + context
            )

        # 5. Generate answer
        prompt = PromptTemplate.from_template(BASEL3_SYSTEM_PROMPT)
        chain = (
            {"context": lambda _: context, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        answer = chain.invoke(question)

        # 6. Format sources
        sources = self._format_sources(docs)

        # Build per-chunk breakdown for Context Analyzer
        chunk_breakdown = []
        for i, (doc, score) in enumerate(zip(docs, scores), 1):
            chunk_breakdown.append({
                "index":   i,
                "source":  doc.metadata.get("source", "Unknown"),
                "section": doc.metadata.get("section", ""),
                "page":    doc.metadata.get("page", ""),
                "chars":   len(doc.page_content),
                "score":   round(score, 3),
                "text":    doc.page_content,
            })

        # Estimate tokens (rough: 1 token ≈ 4 chars)
        full_prompt = BASEL3_SYSTEM_PROMPT.replace("{context}", context).replace("{question}", question)
        estimated_tokens = len(full_prompt) // 4

        return {
            "answer": answer,
            "sources": sources,
            "metadata": {
                "retrieval_mode": retrieval_mode,
                "chunks_retrieved": len(docs),
                "top_k": top_k,
                "confidence": confidence,
                "avg_score": round(avg_score, 3),
            },
            "context_data": {
                "question":        question,
                "context_str":     context,
                "full_prompt":     full_prompt,
                "chunk_breakdown": chunk_breakdown,
                "estimated_tokens": estimated_tokens,
                "confidence":      confidence,
                "avg_score":       round(avg_score, 3),
            },
        }

    def _retrieve(
        self, question: str, mode: str, top_k: int
    ) -> list[Document]:
        dense_retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": top_k, "fetch_k": top_k * 3, "lambda_mult": 0.7},
        )

        if mode == "dense":
            return dense_retriever.invoke(question)

        if mode == "sparse":
            self.bm25_retriever.k = top_k
            return self.bm25_retriever.invoke(question)

        if mode == "hybrid":
            if _HAS_ENSEMBLE:
                ensemble = EnsembleRetriever(
                    retrievers=[dense_retriever, self.bm25_retriever],
                    weights=[0.6, 0.4],
                )
                return ensemble.invoke(question)
            else:
                # Manual fusion fallback — no EnsembleRetriever needed
                dense_docs = dense_retriever.invoke(question)
                self.bm25_retriever.k = top_k
                bm25_docs = self.bm25_retriever.invoke(question)
                seen, merged = set(), []
                for doc in dense_docs + bm25_docs:
                    key = doc.page_content[:100]
                    if key not in seen:
                        seen.add(key)
                        merged.append(doc)
                return merged[:top_k]

        if mode == "multi_query":
            if _HAS_MULTI_QUERY:
                mq_retriever = MultiQueryRetriever.from_llm(
                    retriever=dense_retriever, llm=self.llm
                )
                return mq_retriever.invoke(question)
            else:
                return dense_retriever.invoke(question)

        return dense_retriever.invoke(question)

    def _rerank(self, question: str, docs: list[Document]) -> list[Document]:
        """Simple keyword-overlap re-ranking (avoids extra API calls)."""
        docs, _ = self._rerank_with_scores(question, docs)
        return docs

    def _rerank_with_scores(
        self, question: str, docs: list[Document]
    ) -> tuple[list[Document], list[float]]:
        """Re-rank docs by keyword overlap and return scores alongside docs."""
        q_terms = set(re.findall(r"\w+", question.lower()))
        scored = []
        for doc in docs:
            d_terms = set(re.findall(r"\w+", doc.page_content.lower()))
            overlap = len(q_terms & d_terms) / max(len(q_terms), 1)
            scored.append((overlap, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        docs_out   = [doc   for _, doc   in scored]
        scores_out = [score for score, _ in scored]
        return docs_out, scores_out

    @staticmethod
    def _build_context(docs: list[Document]) -> str:
        parts = []
        for i, doc in enumerate(docs, 1):
            src = doc.metadata.get("source", "Unknown")
            sec = doc.metadata.get("section", "")
            header = f"[{i}] {src}" + (f" — {sec}" if sec else "")
            parts.append(f"{header}\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def _format_sources(docs: list[Document]) -> list[dict]:
        seen: set[str] = set()
        sources = []
        for doc in docs:
            src = doc.metadata.get("source", "Unknown Source")
            if src not in seen:
                seen.add(src)
                sources.append({
                    "source": src,
                    "section": doc.metadata.get("section", ""),
                    "page": doc.metadata.get("page", ""),
                    "snippet": doc.page_content[:200] + "…",
                })
        return sources
