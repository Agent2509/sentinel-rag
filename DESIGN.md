# Sentinel RAG — design brief

## The subject

A local retrieval lab. One corpus, three chunkers, one traced query pipeline, and
citations that point back to the source. The audience is the person who owns the
documents; the primary job is **to see how an answer was produced**, not just to
read the answer.

The subject's materials are documents, index cards, catalogue numbers, ruled
ledgers, timings, footnotes and a rubber stamp. The interface should look like it
belongs to that world, not to a SaaS dashboard.

## Direction: lab ledger

A printed laboratory log. Cool paper, ink, one oxide-red stamp, ruled tables, a
timing strip. Light-first; dark mode is the same page read under a lamp.

### Colour (light)

| Token | Value | Use |
|---|---|---|
| paper | `#F4F4F0` | page |
| paper-sunk | `#E9E9E3` | quiet fill, inline code |
| ink | `#171717` | text, rules, primary button |
| ink-soft | `#5D605A` | secondary text |
| rule | `rgba(23, 23, 23, 0.16)` | 1px rules |
| stamp | `#A33A2B` | retries, errors, the one accent |

Status is text + shape, never colour alone: `ok` ink square, `warn` amber,
`error`/retry stamp.

Dark mode inverts: page `#151514`, text `#E8E6DF`, rule `18%`, stamp `#D2604E`.

No gradients, no glow, no backdrop blur, no decorative washes.

### Type

- **Instrument Sans** — interface, labels, buttons, metadata.
- **Newsreader** — page titles, the answer, document titles. Body is serif with
  slightly more line-height; measure ≤ 68 characters.
- **Geist Mono** — only literal data: ids, scores, durations.

Scale: 12 / 13 / 15 / 17 / 22 / 34. Body 15/1.6, reading 17/1.75, headings
1.25. Sentence case everywhere; no all-caps labels, no middle-dot meta strings.

### Layout

```
┌────────────┬──────────────────────────────────────────────┐
│ Sentinel   │  Ask                                         │
│            │  one sentence of context                     │
│ Ask        │ ──────────────────────────────────────────── │
│ Compare    │  [ question ......................... ] Run   │
│ Documents  │ ──────────────────────────────────────────── │
│            │  ██████ timing strip ████ 34ms ── 2.9s       │
│ Recent     │  route     599ms   simple, definition        │
│ · trace    │  retrieve   19ms   3 chunks, BM25 + FAISS    │
│ · trace    │  grade     1129ms  score 0.93, pass ≥ 0.6    │
│            │ ──────────────────────────────────────────── │
│            │  Answer (serif, 68ch)                        │
│ ok · 1 doc │  … with footnotes at the bottom              │
└────────────┴──────────────────────────────────────────────┘
```

- 15rem rail, 1px rule, content max 72rem, left-aligned.
- Sections are separated by rules, not boxes. Radius 2px, no shadows.
- The **timing strip** is the only loud element: a single stacked bar of stage
  durations, with retry in stamp. Everything around it stays quiet.
- Numbers appear only where they are measurements or a real sequence.
- Compare is two ruled columns with a delta table above; Documents is a ruled
  table. No cards, no glass.

### Principles

1. The trace is the hero; the interface gets out of its way.
2. One accent: oxide stamp. One motion: the timing strip draws in on load.
3. Rules carry structure; shadows carry nothing.
4. Sentence case, active verbs, no marketing copy.
5. Empty and error states direct the next action.

## Self-review against the AI-tell list

| Tell | Verdict |
|---|---|
| Cream + serif display + terracotta | Paper is cooler (`#F4F4F0`), serif is for reading not display, accent is oxide red, not terracotta |
| Near-black + acid green | Removed; light-first ink and paper |
| Broadsheet hairline columns | Not a newspaper grid: a rail + one reading column + a timing strip; 2px radius, not zero |
| SaaS card kit + soft shadows + gradient washes | Cards are ruled sections; shadows and gradients removed |
| All-caps eyebrows / middle dots / mono labels / `→` CTAs | Labels are sentence case; fields are separated by rules; mono only for literal data; buttons say what they do |
