export type Strategy = "fixed" | "hierarchical" | "semantic";

export type FinalStatus = "success" | "not_found" | "error";

export interface Chunk {
  chunk_id: string;
  doc_title: string;
  text: string;
  context?: string | null;
  parent_id?: string | null;
  bm25_rank?: number | null;
  vector_rank?: number | null;
  rrf_score?: number | null;
}

export interface Citation {
  ref: number;
  chunk_id: string;
  doc_title: string;
}

export interface Step {
  step_number: number;
  action: string;
  duration_ms: number;
  result?: { type: "simple" | "complex"; reason: string };
  query_used?: string;
  chunks?: Chunk[];
  grade?: { relevant: boolean; score: number | null; reason: string };
  hypothetical_document?: string;
  answer?: string;
  citations?: Citation[];
}

export interface Trace {
  trace_id: string;
  timestamp: string;
  query: string;
  strategy: Strategy;
  correction_enabled: boolean;
  steps: Step[];
  final_status: FinalStatus;
  total_latency_ms: number;
  retries: number;
  fallback_message?: string;
  closest_chunks?: Chunk[];
  error?: string;
}

export type SSEEvent =
  | {
      type: "start";
      trace_id: string;
      strategy: Strategy;
      correction_enabled: boolean;
    }
  | { type: "step"; trace_id: string; step: Step }
  | { type: "final"; trace_id: string; trace: Trace };

export interface Health {
  status: "ok" | "degraded";
  indexes_ok: boolean;
  model_ready: boolean;
  corpus_size: number;
  trace_count: number;
  strategies: Strategy[];
}

export interface EvalRow {
  id: string;
  strategy: Strategy;
  correction_enabled: number;
  question: string;
  faithfulness: number | null;
  answer_relevancy: number | null;
  context_precision: number | null;
  context_recall: number | null;
  latency_ms: number | null;
  run_timestamp: string;
  corpus_version: string | null;
}

export interface DocumentInfo {
  name: string;
  tokens: number;
  added_at: number;
}

export interface DocumentsPayload {
  documents: DocumentInfo[];
  corpus_version: string;
  reindexing: boolean;
}
