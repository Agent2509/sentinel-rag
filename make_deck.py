"""Generate the Sentinel RAG presentation deck.

    python3 make_deck.py   -> Sentinel_RAG.pptx (project root)

Dark theme matches the product. Detail lives in speaker notes.
"""
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

SHOTS = "/tmp/commandcode-1000/-home-mohdfaizanali-Desktop-my-projects-sentinal-rag/cbe1e519-04b6-4b35-b98e-f6f2411f4c2b/scratchpad"
OUT = "/home/mohdfaizanali/Desktop/my projects/sentinal rag/Sentinel_RAG.pptx"

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
    """content: str, or list of (text, {overrides})."""
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


# ---------------------------------------------------------------- 1 title
s = new_slide()
tf = textbox(s, Inches(0.9), Inches(2.1), Inches(11.5), Inches(3.4))
para(tf, "SENTINEL RAG", size=54, color=TEXT, bold=True, first=True, space_after=8)
para(tf, "A self-correcting RAG laboratory", size=24, color=ACCENT, space_after=22)
para(tf, "\u201cMost RAG systems fail silently. Mine knows when it\u2019s failing, "
         "fixes itself, and shows you the receipts.\u201d",
     size=17, color=MUTED, space_after=0)
tf2 = textbox(s, Inches(0.9), Inches(6.4), Inches(11.5), Inches(0.6))
para(tf2, "3 chunking strategies  \u00b7  hybrid BM25 + FAISS  \u00b7  Grader + HyDE  "
          "\u00b7  RAGAS evaluation  \u00b7  live four-screen UI",
     size=14, color=MUTED, first=True)
notes(s, "Locally hosted, end to end: ingestion, three chunking strategies, hybrid "
         "retrieval, an agentic self-correction loop, a RAGAS evaluation harness and a "
         "four-screen web UI. ~50 synthetic AI/ML docs. Embeddings run locally "
         "(bge-small-en-v1.5); the LLM roles run on Groq. Everything is observable: every "
         "pipeline step streams to the UI and every run is persisted.")

# ---------------------------------------------------------------- 2 problem
s = new_slide()
header(s, "the problem", "RAG pipelines fail silently")
cards = [
    ("Wrong retrieval", "The generator never saw the passage that contains the answer.", RED),
    ("Confident hallucination", "It answers anyway \u2014 fluently, and with made-up citations.", AMBER),
    ("No attribution", "A wrong answer could be a retrieval miss or bad generation; nothing tells you which.", MUTED),
]
for i, (t, b, c) in enumerate(cards):
    x = Inches(0.6 + i * 4.15)
    sp = box(s, x, Inches(1.9), Inches(3.85), Inches(2.6))
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = Inches(0.25)
    para(tf, t, size=20, color=c, bold=True, first=True, space_after=10)
    para(tf, b, size=15, color=TEXT, space_after=0)
tf = textbox(s, Inches(0.6), Inches(5.1), Inches(12.1), Inches(1.4))
para(tf, "Two-stage pipelines fail in two places. If you can\u2019t see the stages, "
         "you can\u2019t fix the pipeline \u2014 you find out when a user does.",
     size=19, color=TEXT, first=True)
notes(s, "This is the core motivation. A RAG system is a two-stage pipeline: retrieve, then "
         "generate. Each stage fails differently. Sentinel RAG makes both stages visible, "
         "graded and self-correcting \u2014 and stores the receipts for every run.")

# ---------------------------------------------------------------- 3 what it is
s = new_slide()
header(s, "what it is", "Four pillars, one observable pipeline")
pillars = [
    ("01", "Chunk three ways", "fixed 512/50 \u00b7 hierarchical 256/1024 \u00b7 semantic percentile splits \u2014 compared, not assumed"),
    ("02", "Retrieve hybrid", "BM25 top-20 + FAISS top-20, fused with Reciprocal Rank Fusion"),
    ("03", "Correct itself", "a grader scores every retrieval; a low score triggers a HyDE rewrite and re-retrieval"),
    ("04", "Prove it", "RAGAS metrics across a 6-combo matrix, rendered in a live scoreboard"),
]
for i, (n, t, b) in enumerate(pillars):
    y = Inches(1.85 + i * 1.24)
    box(s, Inches(0.6), y, Inches(12.1), Inches(1.05))
    tf = textbox(s, Inches(0.85), y + Inches(0.14), Inches(11.6), Inches(0.8))
    para(tf, [(n + "   ", {"color": ACCENT, "bold": True, "size": 18}),
              (t, {"bold": True, "size": 18}),
              ("     " + b, {"color": MUTED, "size": 14})], first=True, space_after=0)
notes(s, "The point of the lab is comparison: the same query through three chunking "
         "strategies, with self-correction on and off, measured. Nothing is hand-waved \u2014 "
         "the architecture diagram, the grader threshold, the eval numbers are all in the repo.")

# ---------------------------------------------------------------- 4 architecture
s = new_slide()
header(s, "architecture", "Ingestion \u2192 indexes \u2192 the correcting loop")


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


flow(s, 1.65, [("Corpus", "50 AI/ML docs"), ("3 chunkers", "fixed / hier / semantic"),
               ("bge-small", "384-d, L2-norm"), ("Indexes", "FAISS IP + BM25")],
     h=1.05)
box(s, Inches(4.74), Inches(3.05), Inches(3.79), Inches(0.95), fill=PANEL2, line=AMBER)
tf = textbox(s, Inches(4.84), Inches(3.18), Inches(3.59), Inches(0.8))
para(tf, "score < 0.6  \u2192  HyDE rewrite  \u2192  re-retrieve  \u2192  re-grade   (max 2)",
     size=12, color=AMBER, first=True, space_after=0, align=PP_ALIGN.CENTER)
# loop feeds back into Hybrid (down), Grader feeds the loop (up)
box(s, Inches(5.51), Inches(4.00), Inches(0.18), Inches(0.35), fill=AMBER, line=None,
    shape=MSO_SHAPE.DOWN_ARROW)
box(s, Inches(7.58), Inches(4.00), Inches(0.18), Inches(0.35), fill=AMBER, line=None,
    shape=MSO_SHAPE.UP_ARROW)
flow(s, 4.35, [("Query", "\u2264 2000 chars"), ("Router", "simple / complex"),
               ("Hybrid + RRF", "top-5"), ("Grader", "score 0\u20131"),
               ("Generate", "cited answer"), ("Trace + UI", "SQLite / SSE")],
     w=1.72, gap=0.35, h=1.15, label_size=12, sub_size=9)
tf = textbox(s, Inches(0.6), Inches(5.85), Inches(12.1), Inches(0.9))
para(tf, "Documents are embedded raw; queries carry the BGE instruction prefix. "
         "Reindex builds into a staging dir, then swaps the live index files.",
     size=13, color=MUTED, first=True)
notes(s, "Top row is ingestion: 50 markdown docs are chunked three ways, embedded with "
         "bge-small-en-v1.5 (384-dim, L2-normalized so inner product equals cosine), and "
         "stored as nine files \u2014 a FAISS IndexFlatIP and a BM25 index plus chunk metadata "
         "per strategy. Bottom row is the query path. The router decides simple vs complex "
         "(top-3 vs top-5 and whether HyDE is allowed). The grader gates generation. The "
         "whole loop streams over SSE and lands in SQLite.")

# ---------------------------------------------------------------- 5 ingestion
s = new_slide()
header(s, "ingestion", "50 docs in, nine index files out")
bullets(s, Inches(0.6), Inches(1.8), Inches(12.0), [
    ("python -m app.ingest", "chunks every doc three ways, embeds, builds 3 \u00d7 (FAISS + BM25 + chunks.json)"),
    ("bge-small-en-v1.5", "384-dim, L2-normalized \u2014 so IndexFlatIP is exact cosine search"),
    ("Query prefix", "queries carry the BGE instruction prefix; documents are embedded raw"),
    ("Semantic chunker", "the only chunker that runs the model at ingest: embeds sentences to find breakpoints"),
    ("Live reindex", "builds into .staging, then os.replace onto the live index; retriever cache resets"),
    ("Provenance", "corpus_version = SHA-256 of the corpus \u2014 the eval test set is stamped with it"),
])
notes(s, "Ingestion is a single CLI command and is also invoked by the Documents page. "
         "Reindexing is single-flight (a lock), so an upload during a rebuild queues rather "
         "than corrupts. The staging swap means a reader never sees a half-built index; the "
         "known limit is that the swap is per-file, not atomic across all three strategies.")

# ---------------------------------------------------------------- 6 chunking
s = new_slide()
header(s, "chunking", "Three strategies, three trade-offs")
rows = [
    ["Strategy", "Parameters", "Trade-off"],
    ["Fixed", "512-token windows, 50-token overlap", "Predictable and cheap; blind to content, can cut a definition in half"],
    ["Hierarchical", "child 256 / parent 1024, children carry parent_id", "Match on small, generate on big; parent text duplicated per child"],
    ["Semantic", "cosine breakpoints at the 25th percentile, 512-token cap", "Respects meaning; costs an extra embedding pass over every sentence"],
]
gt = s.shapes.add_table(4, 3, Inches(0.6), Inches(1.85), Inches(12.1), Inches(3.2)).table
for r, row in enumerate(rows):
    gt.rows[r].height = Inches(0.8)
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
        run.font.size = Pt(14 if r else 14)
        run.font.bold = r == 0
        run.font.color.rgb = ACCENT if r == 0 else TEXT
tf = textbox(s, Inches(0.6), Inches(5.5), Inches(12.1), Inches(1.2))
para(tf, "No strategy dominates \u2014 short factual queries favour small chunks, explanatory "
         "questions favour larger context. That is exactly why the lab compares them.",
     size=16, color=MUTED, first=True)
notes(s, "Every chunk is a dataclass with chunk_id, doc_title, text, strategy and optional "
         "parent_id/parent_text. Hierarchical retrieval matches at the child level and "
         "expands to the parent before generation, which is what the eval calls the "
         "'context'. The semantic chunker hard-caps any over-long sentence at 512 tokens.")

# ---------------------------------------------------------------- 7 retrieval
s = new_slide()
header(s, "retrieval", "Hybrid search, fused by rank")
bullets(s, Inches(0.6), Inches(1.85), Inches(12.0), [
    ("BM25 top-20 + FAISS top-20", "lexical catches exact terms, dense catches paraphrase"),
    ("Reciprocal Rank Fusion, k = 60", "score = \u03a3 1/(60 + rank) \u2014 fuses ranks, no score calibration needed"),
    ("Top-5 into the grader", "top-3 when the router classifies the query as simple"),
    ("Simple path skips HyDE", "retrieve \u2192 grade once \u2192 answer or not_found"),
], size=17, gap=14)
tf = textbox(s, Inches(0.6), Inches(5.6), Inches(12.1), Inches(1.2))
para(tf, "Every chunk keeps its bm25_rank, vector_rank and rrf_score \u2014 the UI shows you "
         "which retriever found it and how it was ranked.",
     size=16, color=MUTED, first=True)
notes(s, "RRF is deliberately boring: it needs no tuned weights between a sparse score and a "
         "cosine score. The per-chunk ranks are persisted in the trace, so the UI can show "
         "exactly why a chunk surfaced.")

# ---------------------------------------------------------------- 8 loop
s = new_slide()
header(s, "self-correction", "The loop that refuses to guess")
flow(s, 1.9, [("Router", "simple / complex"), ("Retrieve", "top-3 or top-5"),
              ("Grade", "0\u20131 relevance"), ("Generate", "only if \u2265 0.6")],
     w=2.85, h=1.2)
sp = box(s, Inches(0.6), Inches(3.6), Inches(12.1), Inches(2.9))
tf = sp.text_frame
tf.margin_left = tf.margin_right = Inches(0.3)
para(tf, "The rules", size=17, color=ACCENT, bold=True, first=True, space_after=10)
for line in [
    "score < 0.6 on a complex query \u2192 HyDE rewrite \u2192 re-retrieve \u2192 re-grade, max 2 retries",
    "grader error \u2192 fail closed immediately \u2014 a broken grader never burns the retry budget",
    "an answer with zero valid citations is thrown away as not_found, never shown",
    "final statuses: success | not_found | error \u2014 and the trace records why (fallback_reason)",
]:
    para(tf, [("\u25aa  ", {"color": ACCENT}), (line, {})], size=15, space_after=8)
notes(s, "Router and grader run at temperature 0; generation 0.3; HyDE 0.7. Token budgets "
         "are sized for a reasoning model, which spends hidden tokens before answering. "
         "Fail-closed is a deliberate choice: an infrastructure error must not look like a "
         "confident answer, and it must be distinguishable from a retrieval miss \u2014 which is "
         "what fallback_reason gives us.")

# ---------------------------------------------------------------- 9 grounding
s = new_slide()
header(s, "grounding", "Citations are checked, not trusted")
bullets(s, Inches(0.6), Inches(1.85), Inches(12.0), [
    ("The generator must cite [n]", "inline markers placed right after the claim they support"),
    ("The backend validates", "out-of-range markers dropped, duplicates removed, renumbered in order of appearance"),
    ("The answer is rewritten", "so the visible markers always match the citation list exactly"),
    ("Zero valid citations", "the whole answer is discarded as not_found \u2014 never shown ungrounded"),
    ("Per-run diagnostics", "fallback_reason, grader_error, source_doc_hit, retries \u2014 stored with every trace"),
], size=17, gap=13)
notes(s, "The citation validator is also why the UI can make citations interactive: click a "
         "[n] and the UI scrolls to and highlights the exact chunk that backs the claim. "
         "The chunk_id in each citation is the ground truth link.")

# ---------------------------------------------------------------- 10 war story
s = new_slide()
header(s, "war story", "The bug that ate 118 of 120 answers")
bullets(s, Inches(0.6), Inches(1.85), Inches(12.0), [
    ("The eval looked terrible", "118/120 answers were \u201cI couldn\u2019t find a confident answer\u201d"),
    ("But retrieval was perfect", "context precision \u2248 0.97, source_doc_hit = 1.0 \u2014 the right chunks were found every time"),
    ("The model wrote \u30101\u3011, the validator knew only [1]", "CJK bracket variants meant zero valid citations \u2192 every grounded answer discarded"),
    ("Fix + receipts", "normalize the bracket variants; add final_status / fallback_reason / grader_error / doc_hit to every record"),
], size=17, gap=13)
tf = textbox(s, Inches(0.6), Inches(5.9), Inches(12.1), Inches(1.0))
para(tf, "Lesson: diagnose before tuning \u2014 the grader threshold was never the problem.",
     size=18, color=AMBER, bold=True, first=True)
notes(s, "This is the most honest slide in the deck. The first eval run was invalid because "
         "of a citation-parser bug, not a bad pipeline. The fix was two lines; the valuable "
         "part was the instrumentation that made the bug obvious instead of invisible. The "
         "harness now refuses to persist a run whose failure rate says 'outage', and can "
         "resume across quota resets.")

# ---------------------------------------------------------------- 11 eval setup
s = new_slide()
header(s, "evaluation", "Measured with RAGAS")
bullets(s, Inches(0.6), Inches(1.85), Inches(12.0), [
    ("Test set", "50 question/answer rows \u2014 one per corpus doc \u2014 each with a reference answer and reference contexts"),
    ("Matrix", "3 strategies \u00d7 correction on/off = 6 combos"),
    ("Metrics", "faithfulness + answer relevancy (LLM judge) and non-LLM context precision / recall"),
    ("Judging scales", "one judge per Groq account; the pipeline pools and rotates all keys"),
    ("Guard rails", "pre-flight probe before anything is cleared, abort-on-error-rate, --resume across quota resets"),
], size=17, gap=13)
notes(s, "The harness maps a pipeline trace to a RAGAS sample: on success the response is "
         "the generated answer and the contexts are the last retrieval; on fallback it uses "
         "the fallback message and the closest chunks. Reference contexts are the full source "
         "doc, which is what makes context precision/recall computable.")

# ---------------------------------------------------------------- 12 results
s = new_slide()
header(s, "results", "What the numbers say so far")
rows = [
    ["Strategy", "Correction", "Faithful.", "Relevancy", "Ctx prec.", "Ctx recall", "Answered"],
    ["fixed", "on", "1.000", "0.868", "0.950", "1.000", "10/10"],
    ["fixed", "off", "0.967", "0.837", "0.950", "1.000", "10/10"],
    ["hierarchical", "on", "\u2014", "\u2014", "0.850", "0.900", "6/10"],
    ["hierarchical", "off", "pending", "", "", "", ""],
    ["semantic", "on / off", "pending", "", "", "", ""],
]
gt = s.shapes.add_table(len(rows), 7, Inches(0.6), Inches(1.8), Inches(12.1), Inches(3.3)).table
widths = [2.3, 1.6, 1.5, 1.6, 1.5, 1.6, 2.0]
for r, row in enumerate(rows):
    gt.rows[r].height = Inches(0.55)
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
        run.font.bold = r == 0 or c == 0
        run.font.color.rgb = ACCENT if r == 0 else (MUTED if val == "pending" else TEXT)
for c, wd in enumerate(widths):
    gt.columns[c].width = Inches(wd)
tf = textbox(s, Inches(0.6), Inches(5.4), Inches(12.1), Inches(1.4))
para(tf, "n = 10 per combo on gpt-oss-20b (the 120b free-tier quota was exhausted). "
         "\u201c\u2014\u201d means the judge was throttled, not zero. source_doc_hit = 1.0 and "
         "grader_error = 0 on the completed combos: retrieval and grading are healthy.",
     size=14, color=MUTED, first=True, space_after=6)
para(tf, "Remaining combos finish with: python -m eval.run_ragas --limit 10 --resume",
     size=14, color=MUTED)
notes(s, "Be straight about coverage: three of six combos, ten rows each. Fixed is the "
         "headline: 10/10 answered, faithfulness 1.0 with correction on. The known "
         "limitations are the free tier (account-wide limits, which is why the keys pool "
         "across accounts) and a non-LLM context-metric artifact on the semantic strategy "
         "where doc_hit is 1.0 but the string-overlap metric scores low.")

# ---------------------------------------------------------------- 13 UI trace
s = new_slide()
header(s, "the ui", "Trace View \u2014 the pipeline, live")
s.shapes.add_picture(SHOTS + "/deck-trace-loaded.png", Inches(0.6), Inches(1.6), width=Inches(8.5))
tf = textbox(s, Inches(9.35), Inches(1.75), Inches(3.4), Inches(5.2))
para(tf, "What you are looking at", size=15, color=ACCENT, bold=True, first=True, space_after=10)
for line in [
    "steps stream in over SSE with per-step timings",
    "grading shows the score and the pass threshold",
    "chunks expand to full text",
    "citations are clickable \u2014 they jump to and highlight the exact chunk",
    "Recent traces replays any stored run",
    "fallbacks say why they fell back",
]:
    para(tf, [("\u25aa  ", {"color": ACCENT}), (line, {"size": 13})], space_after=9)
notes(s, "This is the demo screen. The trace shown was loaded from history, not re-run \u2014 "
         "which is the resilience feature: if the quota dies during the demo, every previous "
         "run is still replayable. The idle state teaches the five stages before the first "
         "query is typed.")

# ---------------------------------------------------------------- 14 UI scoreboard
s = new_slide()
header(s, "the ui", "Scoreboard \u2014 the receipts")
s.shapes.add_picture(SHOTS + "/deck-scoreboard.png", Inches(0.6), Inches(1.7), width=Inches(9.6))
tf = textbox(s, Inches(10.45), Inches(1.9), Inches(2.5), Inches(4.8))
para(tf, "Per-combo cards", size=15, color=ACCENT, bold=True, first=True, space_after=10)
for line in [
    "RAGAS means per strategy \u00d7 correction",
    "latency bars, n and corpus version shown",
    "reads GET /api/eval \u2014 same numbers as the README",
]:
    para(tf, [("\u25aa  ", {"color": ACCENT}), (line, {"size": 13})], space_after=9)
notes(s, "The scoreboard is populated by the eval harness writing to the eval_results table. "
         "The corpus version is stamped so numbers are always attributable to a corpus state.")

# ---------------------------------------------------------------- 15 reliability
s = new_slide()
header(s, "engineering", "Built to survive a demo")
bullets(s, Inches(0.6), Inches(1.85), Inches(12.0), [
    ("SSE streaming", "first event carries trace_id; client disconnect stops the pipeline between steps"),
    ("SQLite, WAL mode", "traces and eval results coexist with live traffic; one connection per call"),
    ("Live reindex", "staging dir \u2192 atomic file swap per strategy; retriever cache reset; single-flight lock"),
    ("Groq key pool", "round-robin across separate accounts, a 401 evicts a dead key, one judge per account"),
    ("Eval harness guards", "probe \u2192 abort-on-error-rate \u2192 resume; a bad run can never overwrite a good one"),
    ("Bounded concurrency", "asyncio.Semaphore(2) around pipelines; blocking calls pushed to threads"),
], size=16, gap=11)
notes(s, "Everything here was added because it failed once: the revoked key, the exhausted "
         "quota, the mid-matrix rate limit. The system's failure modes are handled in code, "
         "not in hope.")

# ---------------------------------------------------------------- 16 run it
s = new_slide()
header(s, "run it", "Three commands, three screens")
cmds = [
    ("backend", ["uv venv .venv && uv pip install -r requirements.txt",
                 "python -m app.ingest          # build the indexes",
                 "uvicorn app.main:app --port 8000"]),
    ("frontend", ["pnpm install",
                  "pnpm dev                       # http://localhost:3000"]),
    ("evaluate", [".venv-eval/bin/python -m eval.run_ragas --limit 10 --resume",
                  "python scripts/check_api.py    # deterministic self-checks"]),
]
for i, (label, lines) in enumerate(cmds):
    y = Inches(1.85 + i * 1.62)
    box(s, Inches(0.6), y, Inches(12.1), Inches(1.42))
    tf = textbox(s, Inches(0.9), y + Inches(0.14), Inches(11.6), Inches(1.2))
    para(tf, label.upper(), size=13, color=ACCENT, bold=True, first=True, space_after=6)
    for ln in lines:
        para(tf, ln, size=14, color=TEXT, font="Consolas", space_after=3)
notes(s, "Ports: backend 8000, frontend 3000. The frontend talks to the backend directly "
         "(CORS), no Next.js proxy \u2014 that is what makes SSE work. The eval runs in a "
         "separate venv because RAGAS pins an older openai SDK than the app.")

# ---------------------------------------------------------------- 17 limits
s = new_slide()
header(s, "honest limits", "What I\u2019d fix next")
bullets(s, Inches(0.6), Inches(1.85), Inches(6.0), [
    ("Coverage", "3 of 6 eval combos done, n = 10 \u2014 the rest are a quota question, not a code question"),
    ("Metric artifact", "semantic scores low on non-LLM context metrics despite perfect doc hits"),
    ("Chunker cost", "semantic chunking embeds every sentence at ingest"),
], size=16, gap=12)
bullets(s, Inches(6.9), Inches(1.85), Inches(5.9), [
    ("Next", "finish the full gpt-oss-120b matrix on the pooled accounts"),
    ("Next", "a cross-encoder reranker between retrieval and grading"),
    ("Next", "per-question drill-down on the scoreboard; token streaming in the answer"),
], size=16, gap=12)
tf = textbox(s, Inches(0.6), Inches(6.1), Inches(12.1), Inches(0.9))
para(tf, "\u201cIt knows when it\u2019s failing, fixes itself, and shows you the receipts.\u201d",
     size=18, color=ACCENT, bold=True, first=True)
notes(s, "Close on the receipts line. Everything claimed in this deck is in the repo: the "
         "architecture matches the implementation plan, the numbers come from results.json, "
         "and the failure story (the citation bug, the quota outage) is documented in the "
         "README rather than hidden.")

prs.save(OUT)
print(f"saved {OUT} with {len(prs.slides._sldIdLst)} slides")
