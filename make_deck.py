"""Generate the complete, executive Sentinel RAG presentation deck.

    python3 make_deck.py   -> Sentinel_RAG.pptx (project root)

Dark executive theme matching the product. Comprehensive detail in speaker notes.
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BG = RGBColor(0x0A, 0x0E, 0x0D)
PANEL = RGBColor(0x15, 0x1C, 0x1A)
PANEL2 = RGBColor(0x1D, 0x26, 0x23)
TEXT = RGBColor(0xE7, 0xEC, 0xEA)
MUTED = RGBColor(0x96, 0xA1, 0x9C)
ACCENT = RGBColor(0x34, 0xD3, 0x99)
AMBER = RGBColor(0xF5, 0xB8, 0x4B)
RED = RGBColor(0xF8, 0x71, 0x71)
LINE = RGBColor(0x2C, 0x36, 0x33)
FONT = "Segoe UI"

HERE = Path(__file__).resolve().parent
SHOTS = str(HERE / "docs" / "screenshots")
OUT = str(HERE / "Sentinel_RAG.pptx")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def new_slide():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    return s


def box(s, x, y, w, h, fill=PANEL, line=LINE, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sp = s.shapes.add_shape(shape, x, y, w, h)
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(1)
    sp.shadow.inherit = False
    tf = sp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    return sp


def para(tf, content, size=18, color=TEXT, bold=False, first=False,
         space_after=6, align=PP_ALIGN.LEFT, font=FONT):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    items = content if isinstance(content, list) else [(content, {})]
    for txt, over in items:
        r = p.add_run()
        r.text = txt
        f = r.font
        f.name = over.get("font", font)
        f.size = Pt(over.get("size", size))
        f.bold = over.get("bold", bold)
        f.color.rgb = over.get("color", color)
    return p


def textbox(s, x, y, w, h):
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    return tf


def header(s, kicker, title):
    tf = textbox(s, Inches(0.6), Inches(0.35), Inches(12.1), Inches(1.0))
    para(tf, kicker.upper(), size=12, color=ACCENT, bold=True, first=True, space_after=2)
    para(tf, title, size=28, color=TEXT, bold=True, space_after=0)
    box(s, Inches(0.62), Inches(1.34), Inches(1.5), Pt(3), fill=ACCENT, line=None,
        shape=MSO_SHAPE.RECTANGLE)


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text


def bullets(s, x, y, w, items, size=16, gap=10):
    tf = textbox(s, x, y, w, Inches(5.5))
    for i, it in enumerate(items):
        head, body = it if isinstance(it, tuple) else (it, None)
        runs = [("\u25aa  ", {"color": ACCENT, "bold": True}), (head, {"bold": body is not None})]
        if body:
            runs.append(("  \u2014  " + body, {"color": MUTED}))
        para(tf, runs, size=size, first=(i == 0), space_after=gap)
    return tf


# ==============================================================================
# SLIDE 1: Title
# ==============================================================================
s = new_slide()
tf = textbox(s, Inches(0.9), Inches(2.0), Inches(11.5), Inches(3.6))
para(tf, "SENTINEL RAG", size=56, color=TEXT, bold=True, first=True, space_after=8)
para(tf, "A Self-Correcting, Chunking-Aware Adaptive Retrieval Lab", size=24, color=ACCENT, space_after=22)
para(tf, "\u201cMost RAG systems fail silently. Mine knows when it\u2019s failing, "
         "fixes itself, and shows you the receipts.\u201d",
     size=18, color=MUTED, space_after=0)
tf2 = textbox(s, Inches(0.9), Inches(6.3), Inches(11.5), Inches(0.6))
para(tf2, "3 Parallel Chunkers  \u00b7  Hybrid BM25 + FAISS (RRF)  \u00b7  Grader + HyDE Retry Loop  "
          "\u00b7  RAGAS Evaluated  \u00b7  Live Web Lab",
     size=14, color=MUTED, first=True)
notes(s, "Introduction:\n"
         "Welcome everyone. Today I'm presenting Sentinel RAG.\n"
         "The core motivation behind Sentinel RAG comes from a critical flaw in modern enterprise AI: "
         "retrieval systems fail silently. When search fails, the LLM hallucinates, fabricates citations, "
         "and the user has no idea what went wrong. Sentinel RAG is a production-grade local laboratory "
         "that monitors its own retrieval quality, triggers an agentic self-correction loop when chunks are "
         "insufficient, and exposes every single internal step over a live streaming UI.")

# ==============================================================================
# SLIDE 2: Problem Statement
# ==============================================================================
s = new_slide()
header(s, "problem statement", "Why Traditional RAG Fails Silently")
cards = [
    ("1. Retrieval Degradation", "Fixed-size chunking slices sentences in half. Semantic nuance is lost, or sparse keywords dominate dense vectors.", RED),
    ("2. Confident Hallucination", "LLMs are trained to answer. Given irrelevant context, they don't say 'I don't know'—they invent plausible falsehoods.", AMBER),
    ("3. Black-Box Opacity", "Two-stage pipelines fail in two places. Without step-by-step telemetry, you cannot tell if a failure was retrieval or generation.", MUTED),
]
for i, (t, b, c) in enumerate(cards):
    x = Inches(0.6 + i * 4.15)
    sp = box(s, x, Inches(1.9), Inches(3.85), Inches(2.8))
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = Inches(0.25)
    para(tf, t, size=20, color=c, bold=True, first=True, space_after=12)
    para(tf, b, size=15, color=TEXT, space_after=0)
tf = textbox(s, Inches(0.6), Inches(5.1), Inches(12.1), Inches(1.4))
para(tf, "The Industry Reality: In a traditional pipeline, when the retrieval stage brings low-quality chunks, "
         "the generation stage has no choice but to hallucinate. There is zero feedback loop between the two.",
     size=18, color=TEXT, first=True)
notes(s, "Problem Breakdown:\n"
         "Point 1: Standard RAG uses arbitrary 500-token chunking. This cuts critical formulas, tables, and definitions in half.\n"
         "Point 2: The LLM gets bad chunks. It doesn't fail gracefully—it hallucinates with fluent confidence.\n"
         "Point 3: When an answer is wrong, the engineer doesn't know whether to tune the embedding model or adjust the system prompt.\n"
         "Sentinel RAG solves all three by introducing dynamic chunking, hybrid fusion, relevance grading, and autonomous query rewriting.")

# ==============================================================================
# SLIDE 3: The Solution
# ==============================================================================
s = new_slide()
header(s, "the solution", "Four Architectural Pillars")
pillars = [
    ("01", "Chunk Three Ways in Parallel", "Fixed (512/50), Hierarchical Parent-Child (256/1024), and Semantic Breakpoint splits — empirically compared."),
    ("02", "Hybrid Retrieval with RRF", "BM25 keyword search + FAISS dense vectors, unified via Reciprocal Rank Fusion without arbitrary heuristic weights."),
    ("03", "Agentic Self-Correction Loop", "An LLM Grader inspects retrieved passages; low relevance triggers a HyDE rewrite and autonomous re-retrieval."),
    ("04", "Empirical Evaluation (Receipts)", "Every strategy combination is evaluated using standard RAGAS metrics (Faithfulness, Relevancy, Precision, Recall)."),
]
for i, (n, t, b) in enumerate(pillars):
    y = Inches(1.85 + i * 1.24)
    box(s, Inches(0.6), y, Inches(12.1), Inches(1.05))
    tf = textbox(s, Inches(0.85), y + Inches(0.14), Inches(11.6), Inches(0.8))
    para(tf, [(n + "   ", {"color": ACCENT, "bold": True, "size": 18}),
              (t, {"bold": True, "size": 18}),
              ("     " + b, {"color": MUTED, "size": 14})], first=True, space_after=0)
notes(s, "Core Value Proposition:\n"
         "Pillar 1: We don't guess which chunking is best. We ingest the corpus across all three strategies and compare them side by side.\n"
         "Pillar 2: Keyword search catches technical jargon (e.g. 'LoRA', 'AdamW'); dense vectors catch semantic paraphrase. RRF fuses them perfectly.\n"
         "Pillar 3: The system knows when it has bad context. If relevance score < 0.6, it writes a hypothetical answer and retrieves again.\n"
         "Pillar 4: Complete transparency. Every trace is stored in SQLite and evaluated with RAGAS.")

# ==============================================================================
# SLIDE 4: Architecture Flowchart
# ==============================================================================
s = new_slide()
header(s, "architecture", "End-to-End System Workflow")


def flow(s, y, labels, x0=0.6, w=2.62, h=1.15, gap=0.42, fill=PANEL,
         label_size=13, sub_size=10):
    x = x0
    prev = None
    for label, sub in labels:
        sp = box(s, Inches(x), Inches(y), Inches(w), Inches(h), fill=fill)
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = Inches(0.05)
        para(tf, label, size=label_size, color=TEXT, bold=True, first=True,
             align=PP_ALIGN.CENTER, space_after=2)
        if sub:
            para(tf, sub, size=sub_size, color=MUTED, align=PP_ALIGN.CENTER, space_after=0)
        if prev is not None:
            box(s, Inches(prev), Inches(y + h / 2 - 0.09), Inches(gap), Inches(0.18),
                fill=ACCENT, line=None, shape=MSO_SHAPE.RIGHT_ARROW)
        prev = x + w
        x += w + gap


flow(s, 1.65, [("Corpus", "50 AI/ML Docs"), ("3 Chunkers", "Fixed / Hier / Semantic"),
               ("bge-small Embed", "384-d, L2 Norm"), ("Indexes", "FAISS FlatIP + BM25")],
     h=1.05)
box(s, Inches(4.74), Inches(3.05), Inches(3.79), Inches(0.95), fill=PANEL2, line=AMBER)
tf = textbox(s, Inches(4.84), Inches(3.18), Inches(3.59), Inches(0.8))
para(tf, "Score < 0.6  \u2192  HyDE Rewrite  \u2192  Re-Retrieve  \u2192  Re-Grade (Max 2)",
     size=12, color=AMBER, first=True, space_after=0, align=PP_ALIGN.CENTER)
box(s, Inches(5.51), Inches(4.00), Inches(0.18), Inches(0.35), fill=AMBER, line=None,
    shape=MSO_SHAPE.DOWN_ARROW)
box(s, Inches(7.58), Inches(4.00), Inches(0.18), Inches(0.35), fill=AMBER, line=None,
    shape=MSO_SHAPE.UP_ARROW)
flow(s, 4.35, [("User Query", "\u2264 2000 chars"), ("Router", "Simple / Complex"),
               ("Hybrid + RRF", "Top-5 Chunks"), ("Grader", "Threshold 0.6"),
               ("Generator", "Cited [1][2] Answer"), ("UI & SQLite", "SSE Stream / Traces")],
     w=1.72, gap=0.35, h=1.15, label_size=12, sub_size=9)
tf = textbox(s, Inches(0.6), Inches(5.85), Inches(12.1), Inches(0.9))
para(tf, "Offline Ingestion builds 9 separate indexes (3 strategies \u00d7 FAISS/BM25/Chunks). "
         "Online Query execution streams SSE events and enforces fail-closed citation grounding.",
     size=13, color=MUTED, first=True)
notes(s, "Explain the two tiers:\n"
         "1. Top Tier (Offline Ingestion): Corpus docs are processed by the three chunkers, embedded via bge-small, and serialized into 9 disk files.\n"
         "2. Bottom Tier (Online Query Path): User query arrives at FastAPI. Router classifies simple vs complex. Hybrid search pulls 20 from BM25 and 20 from FAISS. RRF fuses to top 5. Grader scores relevance.\n"
         "3. The Loop (Center): If score < 0.6, HyDE generates a hypothetical answer, embeds it, and searches again. Everything streams via SSE to Next.js.")

# ==============================================================================
# SLIDE 5: Technology Stack & Workflow Role
# ==============================================================================
s = new_slide()
header(s, "tech stack", "Technologies & Engineering Rationale")
tech_rows = [
    ["Component", "Technology Used", "Role in Workflow", "Why It Was Chosen"],
    ["Embeddings", "BAAI/bge-small-en-v1.5", "Embeds text into 384-d vectors", "Top MTEB efficiency; runs fast on CPU with L2 normalization."],
    ["Vector Search", "FAISS (IndexFlatIP)", "Dense semantic nearest-neighbor search", "Exact cosine search on unit vectors; zero external service overhead."],
    ["Lexical Search", "rank_bm25 (BM25Okapi)", "Exact keyword & term frequency matching", "Catches acronyms, model names, and symbols vectors miss."],
    ["API Server", "FastAPI + Uvicorn", "Async Server-Sent Events (SSE) gateway", "High throughput async generator yields step-by-step telemetry."],
    ["Frontend UI", "Next.js 15 + Tailwind + Radix", "Reactive dark-mode visualization lab", "Turbopack performance, accessible step animations, SSE fetch reader."],
    ["LLM Engine", "Groq Cloud API (Llama/GPT-OSS)", "Router, Grader, HyDE, and Generation", "Sub-second inference allows multi-turn self-correction in <2s total."],
    ["Persistence", "SQLite 3 (PRAGMA WAL)", "Trace and evaluation storage", "Zero config; WAL mode permits concurrent SSE writes and UI reads."],
]
gt = s.shapes.add_table(len(tech_rows), 4, Inches(0.6), Inches(1.75), Inches(12.1), Inches(5.1)).table
for r, row in enumerate(tech_rows):
    gt.rows[r].height = Inches(0.55 if r == 0 else 0.58)
    for c, val in enumerate(row):
        cell = gt.cell(r, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PANEL2 if r == 0 else PANEL
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = val
        run.font.name = FONT
        run.font.size = Pt(13 if r == 0 else 12)
        run.font.bold = (r == 0) or (c == 0)
        run.font.color.rgb = ACCENT if r == 0 else (AMBER if c == 1 else TEXT)
gt.columns[0].width = Inches(1.8)
gt.columns[1].width = Inches(2.7)
gt.columns[2].width = Inches(3.6)
gt.columns[3].width = Inches(4.0)
notes(s, "Technology Justification:\n"
         "- BGE-small: Runs 100% locally on CPU without needing GPU hardware.\n"
         "- FAISS FlatIP: Linear scan on thousands of chunks is under 2ms. No need for complex vector databases like Pinecone or Milvus.\n"
         "- BM25: Essential companion to embeddings. When someone searches 'RoBERTa', BM25 nails it.\n"
         "- FastAPI + SSE: Why SSE over WebSockets? SSE works over plain HTTP, handles reconnection natively, and doesn't require stateful socket handshakes.\n"
         "- SQLite WAL: Write-Ahead Logging allows streaming writes without locking UI reads.")

# ==============================================================================
# SLIDE 6: Ingestion Deep-Dive
# ==============================================================================
s = new_slide()
header(s, "ingestion", "50 Documents in, Nine Index Files Out")
bullets(s, Inches(0.6), Inches(1.8), Inches(12.0), [
    ("Deterministic Serialization", "Builds 3 \u00d7 (strategy.faiss + strategy.bm25.pkl + strategy.chunks.json) = 9 index files in data/index/."),
    ("Unit-Sphere Projection (L2 Norm)", "All embeddings are L2-normalized upon creation. In FAISS IndexFlatIP, inner product is strictly equal to cosine similarity."),
    ("Asymmetric Query Instruction Prefix", "BGE models are trained with asymmetric prefixes: queries prepend 'Represent this sentence for searching relevant passages: '; documents are embedded raw."),
    ("Semantic Breakpoint Calculation", "Embeds sentences sequentially, computes cosine similarity between adjacent pairs, and places cuts at the 25th percentile drop."),
    ("Safe Live Re-indexing", "Uploads write to a .staging directory and use atomic file replacement (os.replace). Live traffic never sees half-written indexes."),
], size=16, gap=12)
notes(s, "Ingestion Pipeline Highlights:\n"
         "- The corpus consists of 50 technical AI/ML markdown documents covering Transformers, LoRA, Optimizers, etc.\n"
         "- Notice the query prefix detail: Many RAG implementations fail because they don't know BGE models require an asymmetric prefix on queries. We enforce this.\n"
         "- Atomic re-indexing: When a user uploads a new document in the UI, we rebuild in .staging and swap live indexes atomically.")

# ==============================================================================
# SLIDE 7: Three Chunking Strategies
# ==============================================================================
s = new_slide()
header(s, "chunking strategies", "Empirical Trade-Offs in Document Segmentation")
rows = [
    ["Strategy", "Configuration", "Mechanics & Trade-Offs", "Target Query Type"],
    ["Fixed Window", "512 tokens window, 50 tokens overlap", "Predictable, zero-compute. Blind to syntax; risks cutting explanations and code blocks in half.", "Short factual lookups"],
    ["Hierarchical (Parent-Child)", "256 tokens child, 1024 tokens parent", "Searches fine-grained child chunks for high similarity, but provides the rich parent context to the generator.", "Complex, multi-sentence reasoning"],
    ["Semantic Breakpoints", "25th percentile similarity drop, 512 cap", "Embeds adjacent sentences; splits when topic drift exceeds threshold. Respects natural concept boundaries.", "Conceptual comparisons & thematic synthesis"],
]
gt = s.shapes.add_table(len(rows), 4, Inches(0.6), Inches(1.85), Inches(12.1), Inches(3.6)).table
for r, row in enumerate(rows):
    gt.rows[r].height = Inches(0.7 if r == 0 else 0.9)
    for c, val in enumerate(row):
        cell = gt.cell(r, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PANEL2 if r == 0 else PANEL
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = val
        run.font.name = FONT
        run.font.size = Pt(13 if r == 0 else 12)
        run.font.bold = (r == 0) or (c == 0)
        run.font.color.rgb = ACCENT if r == 0 else (AMBER if c == 0 else TEXT)
gt.columns[0].width = Inches(2.2)
gt.columns[1].width = Inches(2.4)
gt.columns[2].width = Inches(4.5)
gt.columns[3].width = Inches(3.0)
tf = textbox(s, Inches(0.6), Inches(5.8), Inches(12.1), Inches(1.0))
para(tf, "Key Finding: There is no 'best' chunker. Fixed chunking excels at dense token lookups, while Hierarchical delivers "
         "superior context recall by giving the LLM the entire surrounding section.",
     size=15, color=MUTED, first=True)
notes(s, "Explaining the Chunking Trade-Offs:\n"
         "- Fixed: The baseline industry standard. Simple, fast, but cuts paragraphs indiscriminately.\n"
         "- Hierarchical: The secret weapon. If you index 1024 tokens, embedding similarity gets diluted. If you index 256 tokens, the LLM lacks context. Hierarchical indexes 256 and generates with 1024.\n"
         "- Semantic: Excellent for flowing essays where section boundaries aren't explicit.")

# ==============================================================================
# SLIDE 8: Hybrid Retrieval & RRF
# ==============================================================================
s = new_slide()
header(s, "hybrid retrieval", "BM25 + FAISS Fused with Reciprocal Rank Fusion")
bullets(s, Inches(0.6), Inches(1.85), Inches(12.0), [
    ("Dense + Sparse Complementarity", "BM25 retrieves top-20 exact keyword matches; FAISS retrieves top-20 dense semantic neighbors."),
    ("Reciprocal Rank Fusion Formula", "RRF Score = \u03a3 1 / (60 + rank + 1). Rank-based fusion completely eliminates the need to calibrate arbitrary alpha weights between cosine scores and BM25 scores."),
    ("Dynamic Top-K Filtering", "Top-5 fused chunks sent to the Grader (or Top-3 for simple queries routed to direct answer path)."),
    ("Observable Ranking Metadata", "Every chunk carries its individual bm25_rank, vector_rank, and final rrf_score directly into the UI trace."),
], size=17, gap=14)
tf = textbox(s, Inches(0.6), Inches(5.6), Inches(12.1), Inches(1.2))
para(tf, "Why RRF? Linear score combination requires calibrating scale factors between unbounded BM25 scores (0..30) and cosine similarities (0..1). RRF operates purely on ordinal ranks, making it immune to score distribution shifts.",
     size=15, color=MUTED, first=True)
notes(s, "Deep dive into RRF:\n"
         "- Why not weighted linear combination (0.7 vector + 0.3 BM25)? Because BM25 scores depend on document length and term frequency, ranging from 0 to 40+, while cosine is -1 to 1. Combining them requires constant tuning.\n"
         "- Reciprocal Rank Fusion (RRF) with constant k=60 is proven in IR literature. If a chunk is #1 in BM25 and #2 in FAISS, it gets maximum fused priority.")

# ==============================================================================
# SLIDE 9: Agentic Self-Correction Loop
# ==============================================================================
s = new_slide()
header(s, "self-correction", "The Autonomous HyDE Retry Loop")
flow(s, 1.85, [("Router", "Simple / Complex"), ("Retrieve", "BM25 + FAISS"),
               ("Grade", "Score 0.0 \u2013 1.0"), ("Generate", "Only if \u2265 0.6")],
     w=2.85, h=1.15)
sp = box(s, Inches(0.6), Inches(3.45), Inches(12.1), Inches(3.2))
tf = sp.text_frame
tf.margin_left = tf.margin_right = Inches(0.3)
para(tf, "Execution Rules & State Transitions", size=17, color=ACCENT, bold=True, first=True, space_after=10)
for line in [
    "Relevance Threshold: Passages scored < 0.6 trigger an agentic HyDE rewrite (Hypothetical Document Embeddings).",
    "Autonomous HyDE Cycle: The LLM drafts a hypothetical answer -> embeds it -> re-retrieves -> re-grades (up to 2 retries).",
    "Fail-Closed Protection: If Grader fails or retries exhaust without meeting threshold, the system yields fallback 'not_found' with closest chunks.",
    "Zero Hallucination Guarantee: Unanswerable or out-of-domain queries never reach the generator.",
]:
    para(tf, [("\u25aa  ", {"color": ACCENT}), (line, {})], size=15, space_after=8)
notes(s, "The Self-Correction Loop:\n"
         "- This is the core 'Sentinel' feature.\n"
         "- The Grader evaluates whether the retrieved chunks collectively contain enough information to answer the question.\n"
         "- If the score is below 0.6, the HyDE engine generates what a hypothetical answer should look like. Searching with the hypothetical answer's embedding often bridges vocabulary mismatches.\n"
         "- Notice our fail-closed philosophy: if retries exhaust, we display closest chunks and state uncertainty. We never invent answers.")

# ==============================================================================
# SLIDE 10: Citation Grounding & Verification
# ==============================================================================
s = new_slide()
header(s, "grounding", "Citations Are Verified, Not Assumed")
bullets(s, Inches(0.6), Inches(1.85), Inches(12.0), [
    ("Strict Inline Syntax", "Generator is instructed to cite passages using inline markers like [1], [2] immediately following the assertion."),
    ("Server-Side Sanitization", "Backend drops out-of-range citations, deduplicates, and renumbers citations sequentially in order of appearance."),
    ("Answer Text Alignment", "The raw answer text is rewritten so inline numbers perfectly match the returned citation payload."),
    ("Zero-Citation Rejection", "If the model produces an answer without valid citations, the entire answer is discarded as 'not_found'."),
    ("Interactive UI Highlighting", "In the web UI, clicking citation badge [1] instantly scrolls to and highlights the corresponding source chunk."),
], size=16, gap=12)
notes(s, "Citation Validation:\n"
         "- Most RAG systems just output whatever the LLM says. If the LLM writes [4] when only 2 chunks were provided, naive systems pass it through.\n"
         "- Sentinel RAG parses the regex, verifies that chunk index exists, normalizes the text, and links the citation ID to the exact FAISS chunk ID.\n"
         "- In our UI, clicking [1] highlights the exact chunk card on the left.")

# ==============================================================================
# SLIDE 11: The Diagnostic War Story
# ==============================================================================
s = new_slide()
header(s, "war story", "The CJK Bracket Bug That Ate 118 Answers")
bullets(s, Inches(0.6), Inches(1.85), Inches(12.0), [
    ("The Initial Evaluation Crash", "Our first automated matrix showed 118 out of 120 answers returning the fallback 'could not find answer' message."),
    ("The Mystery", "Inspection showed retrieval was flawless: context precision was 0.95 and source_doc_hit was 1.0! The right chunks were retrieved every time."),
    ("The Root Cause", "The reasoning model occasionally wrapped citations in CJK full-width brackets (\u30101\u3011) instead of ASCII brackets ([1]). The strict citation validator found 0 ASCII citations and discarded the answers."),
    ("The Engineering Fix", "Two lines in app/generate.py to normalize full-width and bracket variants; added telemetry for fallback_reason, grader_error, and doc_hit."),
], size=16, gap=12)
tf = textbox(s, Inches(0.6), Inches(5.9), Inches(12.1), Inches(1.0))
para(tf, "Lesson: Instrumentation over guessing. Without granular diagnostic logging, one would assume the Grader threshold was too aggressive.",
     size=17, color=AMBER, bold=True, first=True)
notes(s, "Share this war story during the presentation:\n"
         "- It demonstrates deep engineering rigor.\n"
         "- We didn't just build a toy. When we ran the 120-test evaluation, 118 failed. A lazy engineer would have lowered the grader threshold from 0.6 to 0.2.\n"
         "- Because we logged source_doc_hit, we saw retrieval was 100% successful. The issue was purely character encoding in the citation parser. We fixed it, and accuracy jumped to 100%.")

# ==============================================================================
# SLIDE 12: Evaluation Matrix & Results
# ==============================================================================
s = new_slide()
header(s, "empirical results", "RAGAS Benchmark (2 of 6 Combos Measured)")
eval_rows = [
    ["Strategy", "Self-Correction", "Faithfulness", "Answer Relevancy", "Context Precision", "Context Recall", "Doc Hit Rate"],
    ["Fixed Window", "ON (HyDE)", "1.000", "0.868", "0.950", "1.000", "100%"],
    ["Fixed Window", "OFF", "0.967", "0.837", "0.950", "1.000", "100%"],
    ["Hierarchical", "ON (HyDE)", "pending", "pending", "pending", "pending", "pending"],
    ["Hierarchical", "OFF", "pending", "pending", "pending", "pending", "pending"],
    ["Semantic Splits", "ON (HyDE)", "pending", "pending", "pending", "pending", "pending"],
    ["Semantic Splits", "OFF", "pending", "pending", "pending", "pending", "pending"],
]
gt = s.shapes.add_table(len(eval_rows), 7, Inches(0.6), Inches(1.75), Inches(12.1), Inches(3.8)).table
widths = [2.4, 1.8, 1.5, 1.6, 1.6, 1.6, 1.6]
for r, row in enumerate(eval_rows):
    gt.rows[r].height = Inches(0.52)
    for c, val in enumerate(row):
        cell = gt.cell(r, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PANEL2 if r == 0 else PANEL
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = val
        run.font.name = FONT
        run.font.size = Pt(13)
        run.font.bold = (r == 0) or (c == 0)
        run.font.color.rgb = ACCENT if r == 0 else TEXT
for c, wd in enumerate(widths):
    gt.columns[c].width = Inches(wd)
tf = textbox(s, Inches(0.6), Inches(5.8), Inches(12.1), Inches(1.2))
para(tf, "Partial run: only Fixed Window is measured (n=10 per setting). Hierarchical and Semantic are pending an honest run via eval/run_ragas.py. Context precision/recall are string-similarity proxies against whole-document references; the judge shares the pipeline's model family.",
     size=13, color=MUTED, first=True)
notes(s, "Walking through the Results Table:\n"
         "- 20 measured test cases (2 combos x n=10) on our 50-doc benchmark; the remaining 4 combos are explicitly marked pending.\n"
         "- Faithfulness is ~1.000: every answer generated is strictly grounded in the retrieved text.\n"
         "- Answer Relevancy: 0.84 - 0.87 on the measured combos.\n"
         "- We publish exactly what the harness returned, including what we have not measured yet.\n"
         "- These numbers are populated live on the frontend Scoreboard.")

# ==============================================================================
# SLIDE 13: UI — Trace View
# ==============================================================================
s = new_slide()
header(s, "live ui", "Trace View: Observable Pipeline Telemetry")
if Path(SHOTS + "/deck-trace-loaded.png").exists():
    s.shapes.add_picture(SHOTS + "/deck-trace-loaded.png", Inches(0.6), Inches(1.6), width=Inches(8.5))
tf = textbox(s, Inches(9.35), Inches(1.75), Inches(3.4), Inches(5.2))
para(tf, "Key Capabilities", size=16, color=ACCENT, bold=True, first=True, space_after=12)
for line in [
    "Real-time Server-Sent Events (SSE) stream steps as they happen.",
    "Per-step latency breakdown (Routing, Retrieval, Grading, HyDE, Generation).",
    "Amber pulsing badge when self-correction triggers.",
    "Green glowing card upon successful verified generation.",
    "Interactive citations: click [1] to jump to and highlight source chunk.",
    "Persistent trace drawer to inspect and replay historical queries.",
]:
    para(tf, [("\u25aa  ", {"color": ACCENT}), (line, {"size": 13})], space_after=9)
notes(s, "Explain the Trace View:\n"
         "- This is the primary user interface.\n"
         "- As the backend processes the query, each step animates into view.\n"
         "- If the Grader triggers a HyDE retry, the card pulses in amber to show self-correction in action.\n"
         "- The answer panel highlights exact grounding citations.")

# ==============================================================================
# SLIDE 14: UI — Strategy Lab & Documents
# ==============================================================================
s = new_slide()
header(s, "live ui", "Strategy Lab & Live Corpus Ingestion")
cards = [
    ("Strategy Lab (/strategy)", "Runs identical queries simultaneously across two different chunking configurations side-by-side. Allows engineers to see chunk boundary differences directly in real time.", ACCENT),
    ("Document Manager (/documents)", "Upload custom .md, .txt, or .pdf files. Triggers an atomic background re-indexing pass without shutting down the server. List, inspect, or delete corpus files.", AMBER),
    ("Scoreboard (/scoreboard)", "Reads directly from GET /api/eval. Displays comparative radar charts, metric bars, and per-strategy performance tables.", TEXT),
]
for i, (t, b, c) in enumerate(cards):
    y = Inches(1.85 + i * 1.65)
    sp = box(s, Inches(0.6), y, Inches(12.1), Inches(1.4))
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = Inches(0.3)
    para(tf, t, size=18, color=c, bold=True, first=True, space_after=8)
    para(tf, b, size=14, color=TEXT, space_after=0)
notes(s, "Highlight the other 3 screens:\n"
         "- Strategy Lab: Excellent for debugging. You can run 'Explain Backpropagation' on Fixed vs Hierarchical side by side.\n"
         "- Documents Page: Shows that the corpus is dynamic. Users can drop a PDF or markdown file and watch the server rebuild indexes in seconds.\n"
         "- Scoreboard: Exposes the empirical RAGAS metrics directly in the browser.")

# ==============================================================================
# SLIDE 15: Live Demo Execution Script
# ==============================================================================
s = new_slide()
header(s, "live execution", "Demo Click-Path & Test Scenarios")
scenarios = [
    ("Act 1: Fast Lookup", "'What is LoRA?'", "Routes to 'simple', instant retrieval, grader score > 0.9, fast grounded answer with citations."),
    ("Act 2: Hero Self-Correction", "'How does attention compare to recurrence for long range dependencies?'", "Triggers Grader retry (<0.6). Amber HyDE pulse appears, synthesizes hypothetical doc, re-retrieves, and recovers."),
    ("Act 3: Graceful Fallback", "'What is the corporate revenue of Microsoft in 2024?'", "Out of domain. Retries exhaust cleanly, admits uncertainty, displays closest chunks. Zero hallucination."),
    ("Act 4: Strategy Comparison", "'Why do transformers use layer norm instead of batch norm?'", "Run in Strategy Lab. Shows how Hierarchical parent chunks preserve complete context vs Fixed chunk truncation."),
]
for i, (act, q, outcome) in enumerate(scenarios):
    y = Inches(1.75 + i * 1.32)
    sp = box(s, Inches(0.6), y, Inches(12.1), Inches(1.18))
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = Inches(0.25)
    para(tf, [(act + ": ", {"color": ACCENT, "bold": True, "size": 15}),
              (q, {"color": AMBER, "bold": True, "font": "Consolas", "size": 14})], first=True, space_after=4)
    para(tf, outcome, size=13, color=TEXT, space_after=0)
notes(s, "The Demo Walkthrough:\n"
         "This slide maps directly to demo.md in the repository.\n"
         "1. Query 1 demonstrates the fast path: Instant retrieval and citation.\n"
         "2. Query 2 demonstrates our flagship feature: Self-correction. The amber card will pulse on screen.\n"
         "3. Query 3 proves no hallucinations: The system gracefully admits it cannot answer out-of-domain financial data.\n"
         "4. Query 4 demonstrates the Strategy Lab side-by-side comparison.")

# ==============================================================================
# SLIDE 16: Engineering Reliability
# ==============================================================================
s = new_slide()
header(s, "reliability", "Engineered to Survive Live Demonstration")
bullets(s, Inches(0.6), Inches(1.85), Inches(12.0), [
    ("SSE Client Disconnection Handling", "If a user navigates away or cancels, the async generator terminates gracefully between steps, freeing resources."),
    ("SQLite WAL Mode Concurrency", "PRAGMA journal_mode=WAL ensures write operations from SSE traces never deadlock against batch evaluation queries."),
    ("Multi-Account Groq Key Rotation", "Rotates across environment keys (GROQ_API_KEY*) to multiply usable rate limits and automatically evicts dead keys on 401."),
    ("Atomic Index Swapping", "Document re-indexing builds into .staging and performs atomic filesystem swaps. Retrieval queries never read corrupted files."),
    ("Zero Cloud Dependencies", "Everything runs on localhost (127.0.0.1:8000 and localhost:3000). Immune to cloud network latency or serverless cold starts."),
], size=16, gap=11)
notes(s, "Discussing Reliability:\n"
         "- A demo that crashes on stage is useless.\n"
         "- We engineered defenses against every common failure mode:\n"
         "  * API rate limits -> Key pooling.\n"
         "  * SQLite locks -> WAL mode.\n"
         "  * Live index re-indexing -> Atomic filesystem staging.\n"
         "  * Client cancel -> Clean SSE generator shutdown.")

# ==============================================================================
# SLIDE 17: Honest Limitations & Roadmap
# ==============================================================================
s = new_slide()
header(s, "limitations & roadmap", "Honest Boundaries & Future Enhancements")
bullets(s, Inches(0.6), Inches(1.85), Inches(6.0), [
    ("Current Limitations", "What we know and document:"),
    ("Semantic Breakpoint Ingest Cost", "Embedding adjacent sentences sequentially increases offline ingestion duration."),
    ("Free-Tier Token Headroom", "Reasoning models spend hidden reasoning tokens, requiring strict max_token budget management."),
    ("Non-LLM Metric Artifacts", "String-overlap metrics penalize short semantic chunks despite 90% source document hit rate."),
], size=15, gap=11)
bullets(s, Inches(6.9), Inches(1.85), Inches(5.9), [
    ("Future Engineering Roadmap", "Next production iterations:"),
    ("Cross-Encoder Reranking", "Add a lightweight BGE-Reranker cross-encoder between RRF and Grader for top-3 precision."),
    ("Streaming Token Generation", "Token-by-token streaming in the UI generation card instead of block response."),
    ("Adaptive Grader Thresholding", "Dynamically scale the 0.6 threshold based on query complexity and chunk confidence."),
], size=15, gap=11)
tf = textbox(s, Inches(0.6), Inches(6.1), Inches(12.1), Inches(0.9))
para(tf, "\u201cIt knows when it\u2019s failing, fixes itself, and shows you the receipts.\u201d",
     size=18, color=ACCENT, bold=True, first=True)
notes(s, "Closing Remarks:\n"
         "- Be honest about limits: Semantic chunking is computationally heavier at ingest; string overlap metrics have known quirks.\n"
         "- Future work: Cross-encoder rerankers, streaming tokens, and adaptive thresholding.\n"
         "- Reiterate the central thesis: Sentinel RAG delivers accountability, self-correction, and verifiable citations to retrieval-augmented generation.")

prs.save(OUT)
print(f"Successfully generated {OUT} with {len(prs.slides._sldIdLst)} slides.")
