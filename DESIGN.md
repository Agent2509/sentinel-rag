# Sentinel RAG — design brief

## The subject

A local retrieval lab. One corpus, three chunkers, one traced query pipeline, and
citations that point back to the source. The audience is the person who owns the
documents; the primary job is **to see how an answer was produced**, not just to
read the answer.

The materials are documents, index cards, catalogue numbers, ruled ledgers,
timings, footnotes and a rubber stamp. The interface should look like it belongs
to that world, not to a SaaS dashboard.

## Direction: lab ledger, instrumented

A printed laboratory log with one instrumented page. Paper, ink, one oxide stamp;
ruled tables; a real timing diagram. Light-first; dark mode is the same page read
under a lamp.

### Colour (light)

| Token | Value | Use |
|---|---|---|
| paper | `#F4F4F0` | page |
| paper-sunk | `#E9E9E3` | quiet fill |
| ink | `#171717` | text, rules, primary button |
| ink-soft | `#5D605A` | secondary text |
| rule | `rgba(23, 23, 23, 0.16)` | 1px rules |
| stamp | `#A33A2B` | retries, errors, the one accent |
| ochre | `#8A6A2F` | `not_found` status only |

Dark inverts: page `#151514`, text `#E8E6DF`, rule `18%`, stamp `#D2604E`.
No gradients, glow, backdrop blur or decorative washes.

### Type

- **Instrument Sans** — interface, labels, buttons, metadata.
- **Newsreader** — page titles, answers, document titles. Reading 18/1.75 at a
  64-character measure.
- **Geist Mono** — literal data only: ids, scores, durations.

Scale: **11 / 12 / 14 / 16 / 20 / 34**, line-height 1.25–1.75. Sentence case;
no all-caps labels, no middle-dot meta strings, no stray em-dash labels.

### Layout

```
┌──────────┬────────────────────────────────────────────────┐
│ Sentinel │  Ask                                           │
│          │  one sentence                                  │
│ Ask      │ ────────────────────────────────────────────── │
│ Compare  │  [ question .......................... ] Run    │
│ Docs  1  │ ────────────────────────────────────────────── │
│          │  Trace                         total 3006 ms   │
│ Recent   │  0 ─────────────────────────────── 3.0s        │
│ ▸ trace  │  Route    ████▏                    647 ms       │
│ ▸ trace  │  Retrieve ▏                         57 ms       │
│ ▸ trace  │  Grade       ███████▏              980 ms       │
│ ▸ trace  │  Answer            ██████████▏     1322 ms      │
│          │ ────────────────────────────────────────────── │
│ ok 1 doc │  stage ledger                answer (serif)    │
└──────────┴────────────────────────────────────────────────┘
```

- 14rem rail, 1px rule, content max 72rem, left-aligned.
- Sections separated by rules, not boxes. Radius 2px, no shadows.
- **The timing diagram is the only loud element.** One lane per stage on a
  shared time axis; retry in stamp; bars draw once on run. Everything around it
  stays quiet.
- Compare puts two diagrams on the **same axis** above the delta table, so the
  difference is visible before it is read.
- Numbers appear only where they are measurements or a real sequence.

### Principles

1. The trace is the hero; the interface gets out of its way.
2. One accent, one motion. Boldness lives in the timing diagram.
3. Rules carry structure; shadows carry nothing.
4. Sentence case, active verbs, no marketing copy.
5. Empty and error states direct the next action.

## Self-review against the AI-tell list

| Tell | Verdict |
|---|---|
| Cream + serif display + terracotta | Cooler paper, serif for reading, oxide stamp |
| Near-black + acid green | Removed; light-first |
| Broadsheet hairline columns | Rail + reading column + instrument; 2px radius |
| SaaS card kit, shadows, gradients | Ruled sections only |
| All-caps / middle dots / mono labels | Sentence case, columns, mono for data only |
