"""RAGAS evaluation across the strategy x correction matrix.

Runs the pipeline for each question, scores with RAGAS, writes results.json and
persists per-question rows to the eval_results table.

    python -m eval.run_ragas --smoke
    python -m eval.run_ragas --limit 20
    python -m eval.run_ragas --limit 0 --resume   # all rows, survive quota resets
"""
import argparse
import asyncio
import json
import os
import sys
import time
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from app import config, ingest, trace_store
from app.embeddings import embed_documents as _embed_documents
from app.embeddings import embed_query as _embed_query
from app.llm import api_keys
from app.pipeline import run as run_pipeline
from eval.harness import clean_nan, mean_metrics, trace_diagnostics, trace_to_sample


class RunAborted(Exception):
    """Raised when a combo's failure rate shows an outage, not a result."""


class BgeEmbeddings:
    """RAGAS embeddings adapter over the project's bge singleton.

    Implements the BaseRagasEmbeddings surface (sync + async) so we reuse the
    already-loaded model instead of instantiating a second one.
    """

    def embed_query(self, text: str) -> list[float]:
        return _embed_query(text).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return _embed_documents(texts).tolist()

    async def aembed_query(self, text: str) -> list[float]:
        return self.embed_query(text)

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embed_documents(texts)


def _make_judge(model_override: str | None = None, key: str | None = None):
    # One judge per Groq account key. ChatOpenAI binds OPENAI_API_KEY at
    # construction, so set it immediately before building each judge.
    key = key or os.getenv("GROQ_API_KEY_3") or os.getenv("GROQ_API_KEY")
    if not key:
        sys.exit("Missing GROQ_API_KEY (set it in backend/.env)")
    os.environ["OPENAI_API_KEY"] = key
    from ragas import RunConfig
    from ragas.llms import llm_factory

    # request_timeout + retry policy for the judge HTTP client. Concurrency is
    # controlled by our own loop (--concurrency), not ragas' executor.
    run_config = RunConfig(timeout=300, max_retries=3, max_wait=30)
    return llm_factory(
        model_override or config.GROQ_MODEL,
        base_url=config.GROQ_BASE_URL,
        run_config=run_config,
    )


# The non-LLM context metrics report different names; fold them onto the
# canonical columns so DB schema / results.json / README stay stable.
_METRIC_KEY = {
    "non_llm_context_precision_with_reference": "context_precision",
    "non_llm_context_recall": "context_recall",
}


def _make_metrics(judge, embeddings, mode: str = "lean"):
    from ragas.metrics import (
        AnswerRelevancy,
        ContextPrecision,
        ContextRecall,
        Faithfulness,
        NonLLMContextPrecisionWithReference,
        NonLLMContextRecall,
    )

    metrics = [
        Faithfulness(llm=judge),
        # strictness=1: one generated question instead of three, ~2 fewer judge
        # calls per sample. Enough signal, materially faster on the free tier.
        AnswerRelevancy(llm=judge, embeddings=embeddings, strictness=1),
    ]
    if mode == "full":
        metrics += [ContextPrecision(llm=judge), ContextRecall(llm=judge)]
    else:
        # String-similarity context metrics: no judge calls at all.
        metrics += [NonLLMContextPrecisionWithReference(), NonLLMContextRecall()]
    return metrics


async def _score_sample(sample, metrics) -> dict:
    record = {
        "user_input": sample.user_input,
        "response": sample.response,
        "retrieved_contexts": sample.retrieved_contexts,
        "reference": sample.reference,
    }
    for metric in metrics:
        name = metric.name or ""
        key = _METRIC_KEY.get(name, name)
        value = float("nan")
        for attempt in range(3):  # exponential backoff absorbs rate-limit blips
            try:
                value = float(await metric.single_turn_ascore(sample, timeout=None))
                break
            except Exception as e:  # noqa: BLE001 - one failed metric => NaN
                if attempt == 2:
                    print(f"    {key} failed: {type(e).__name__}")
                else:
                    await asyncio.sleep(2 ** (attempt + 1))
        record[key] = value
    return record


def _evaluate_combo(rows, strategy, correction, metric_sets, limit, concurrency, pace):
    """Score with our own bounded-concurrency loop (no ragas executor).

    ragas' executor cuts judge calls off mid-flight on a rate-limited free tier,
    producing NaN score storms. We run a small number at once with a retry each,
    and abort if the pipeline itself is erroring rather than answering. Judging
    round-robins across `metric_sets` (one per Groq account), so judge quota
    multiplies with the number of accounts.
    ponytail: fixed small concurrency. Raise it on a paid tier.
    """
    from ragas.dataset_schema import SingleTurnSample

    samples, latencies, diags = [], [], []
    errors = 0
    for idx, row in enumerate(rows[:limit]):
        try:
            trace = run_pipeline(row["question"], strategy, correction)
        except Exception as e:  # noqa: BLE001 - skip one row, keep the matrix alive
            print(f"  skip {row['question'][:50]}: {type(e).__name__}")
            continue
        d = trace_diagnostics(trace, row)
        if d["final_status"] == "error" or d["grader_error"]:
            errors += 1
        latencies.append(trace.get("total_latency_ms", 0))
        diags.append(d)
        samples.append(SingleTurnSample(**trace_to_sample(trace, row)))
        seen = len(samples)
        if seen >= 5 and errors / seen >= 0.5:
            raise RunAborted(
                f"{errors}/{seen} pipeline runs failed (grader/LLM outage) on "
                f"{strategy}/correction={correction}; stopped before wasting more quota."
            )
        if pace and idx < limit - 1:
            time.sleep(pace)

    semaphore = asyncio.Semaphore(concurrency)

    async def one(idx: int, sample) -> dict:
        async with semaphore:
            return await _score_sample(sample, metric_sets[idx % len(metric_sets)])

    async def run_all() -> list[dict]:
        return await asyncio.gather(*(one(i, s) for i, s in enumerate(samples)))

    records = asyncio.run(run_all())
    for lat, rec, d in zip(latencies, records, diags):
        rec["latency_ms"] = lat
        rec.update(d)
    return records


def _summarize(records: list[dict], requested: int, strategy: str, correction: bool) -> dict:
    n = len(records)
    return {
        "strategy": strategy,
        "correction_enabled": correction,
        "n": n,
        "skipped": requested - n,
        "metrics": mean_metrics(records),
        "status_counts": dict(Counter(r.get("final_status") for r in records)),
        "fallback_reasons": dict(
            Counter(r["fallback_reason"] for r in records if r.get("fallback_reason"))
        ),
        "grader_error_rate": round(sum(1 for r in records if r.get("grader_error")) / n, 4)
        if n
        else None,
        "source_doc_hit_rate": round(sum(1 for r in records if r.get("source_doc_hit")) / n, 4)
        if n
        else None,
    }


def _probe(rows, strategy, correction, metric_sets) -> str | None:
    """Run a few rows end-to-end; return a reason to stop, or None if healthy.

    This is the guard that stops an LLM outage from being persisted as a result
    (and from clearing an existing good run).
    """
    records = _evaluate_combo(
        rows[:3], strategy, correction, metric_sets, 3, 1, pace=0
    )
    if not records:
        return "no pipeline runs completed (pipeline crashed on every probe row)"
    failed = [
        r for r in records if r.get("final_status") == "error" or r.get("grader_error")
    ]
    if len(failed) >= 2:
        return f"{len(failed)}/{len(records)} probe rows hit a grader/LLM error"
    judged = [
        r
        for r in records
        if r.get("faithfulness") is not None or r.get("answer_relevancy") is not None
    ]
    if not judged:
        return "every probe sample's judge call failed (NaN) — Groq quota likely exhausted"
    return None


def _write(out: str, version: str, summaries: list[dict], records: list[dict]) -> None:
    json.dump(
        {"corpus_version": version, "combos": summaries, "records": records},
        open(out, "w"),
        indent=2,
        default=str,
    )


def main() -> None:
    here = Path(__file__).parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategies", nargs="+", default=list(config.STRATEGIES))
    parser.add_argument("--correction", choices=["on", "off", "both"], default="both")
    parser.add_argument("--limit", type=int, default=20, help="rows per combo; 0 = all")
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--pace", type=float, default=1.0, help="seconds between pipeline calls")
    parser.add_argument("--resume", action="store_true", help="keep completed combos from results.json")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--judge-model", default=None, help="override judge model id")
    parser.add_argument(
        "--metrics",
        choices=["lean", "full"],
        default="lean",
        help="lean = non-LLM context metrics (cheap); full = all-LLM (needs headroom)",
    )
    parser.add_argument(
        "--pipeline-model",
        default=None,
        help="override the pipeline router/grader model (e.g. a lighter Groq model "
        "so the eval fits free-tier quota; consistent across strategies)",
    )
    parser.add_argument("--testset", default=str(here / "testset.jsonl"))
    parser.add_argument("--out", default=str(here / "results.json"))
    args = parser.parse_args()

    if args.smoke:
        args.limit, args.strategies, args.correction = 5, ["semantic"], "on"

    if args.pipeline_model:
        config.GROQ_MODEL = args.pipeline_model  # pipeline router/grader/hyde
        print(f"[eval] pipeline router/grader model -> {args.pipeline_model}")

    if not Path(args.testset).exists():
        sys.exit(f"Testset missing: {args.testset}. Run python -m eval.build_testset")

    rows = [json.loads(line) for line in open(args.testset) if line.strip()]
    corrections = {"on": [True], "off": [False], "both": [True, False]}[args.correction]
    combos = [(s, c) for s in args.strategies for c in corrections]

    version = ingest.corpus_version()
    built_for = {r.get("corpus_version") for r in rows} - {None}
    if built_for and version not in built_for:
        print(
            f"WARNING: testset was built for corpus {sorted(built_for)}, "
            f"current is {version}. Re-run eval.build_testset if the corpus changed."
        )

    embeddings = BgeEmbeddings()
    keys = api_keys()
    if not keys:
        sys.exit("Missing GROQ_API_KEY (set it in backend/.env)")
    # One judge per key so judging spreads across separate accounts' quota.
    metric_sets = [
        _make_metrics(_make_judge(args.judge_model, key=k), embeddings, args.metrics)
        for k in keys
    ]
    print(f"[eval] pipeline keys: {len(keys)}, judge accounts: {len(metric_sets)}")

    # Refuse to clobber a good run with an outage: probe before touching any output.
    probe_err = _probe(rows, combos[0][0], combos[0][1], metric_sets)
    if probe_err:
        sys.exit(f"Probe failed: {probe_err}. Fix Groq keys/quota and re-run; nothing changed.")

    requested = len(rows) if args.limit <= 0 else min(args.limit, len(rows))
    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    summaries: list[dict] = []
    all_records: list[dict] = []
    done: set = set()
    if args.resume and Path(args.out).exists():
        try:
            prev = json.load(open(args.out))
        except Exception:  # noqa: BLE001 - a corrupt artifact just means start fresh
            prev = None
        if prev and prev.get("corpus_version") == version:
            summaries = prev.get("combos", [])
            all_records = prev.get("records", [])
            done = {(s["strategy"], s["correction_enabled"]) for s in summaries if s.get("n")}
            print(f"[eval] resume: {len(done)} combo(s) done, {len(all_records)} records kept")
        else:
            print("[eval] resume ignored: no matching results.json")

    if not done:
        trace_store.init_db()
        _write(args.out, version, summaries, all_records)

    try:
        for strategy, correction in combos:
            if (strategy, correction) in done:
                print(f"\n=== {strategy} | correction={correction} | already done, skipped ===")
                continue
            print(f"\n=== {strategy} | correction={correction} | n={requested} ===")
            records = _evaluate_combo(
                rows, strategy, correction, metric_sets, requested,
                args.concurrency, args.pace,
            )
            summary = _summarize(records, requested, strategy, correction)
            summaries.append(summary)
            print(f"  -> {summary['metrics']}")
            print(
                f"     status={summary['status_counts']} "
                f"grader_err={summary['grader_error_rate']} "
                f"doc_hit={summary['source_doc_hit_rate']}"
            )
            for rec in records:
                cleaned = {k: clean_nan(v) for k, v in rec.items()}
                all_records.append(
                    {**cleaned, "strategy": strategy, "correction_enabled": correction}
                )
            # incremental write: a long/resumed run should leave partial results
            _write(args.out, version, summaries, all_records)
    except RunAborted as e:
        print(f"\n[eval] ABORTED: {e}")

    # Rebuild the DB to match results.json exactly (resume-safe, no duplicates).
    trace_store.init_db()
    trace_store.clear_eval_results()
    for rec in all_records:
        trace_store.save_eval_result(
            {
                "id": str(uuid.uuid4()),
                "strategy": rec.get("strategy"),
                "correction_enabled": rec.get("correction_enabled"),
                "question": rec.get("user_input", ""),
                "faithfulness": rec.get("faithfulness"),
                "answer_relevancy": rec.get("answer_relevancy"),
                "context_precision": rec.get("context_precision"),
                "context_recall": rec.get("context_recall"),
                "latency_ms": rec.get("latency_ms"),
                "run_timestamp": run_ts,
                "corpus_version": version,
            }
        )

    _write(args.out, version, summaries, all_records)
    print(f"\nWrote {args.out} ({len(summaries)} combos, {len(all_records)} rows)")


if __name__ == "__main__":
    main()
