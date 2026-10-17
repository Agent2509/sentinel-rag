export const FALLBACK_LABELS: Record<string, string> = {
  grader_error: "the grader could not be reached",
  low_score: "the grader scored the retrieved chunks too low",
  simple_low_score: "a simple query graded too low to answer from",
  retries_exhausted: "retries were exhausted without a confident score",
  correction_disabled: "self-correction was off and the first grade was low",
  hyde_failed: "the HyDE rewrite could not be generated",
  no_citations: "the answer cited nothing in the retrieved chunks",
};

export function fallbackLabel(reason: string | undefined): string | null {
  if (!reason) return null;
  return FALLBACK_LABELS[reason] ?? reason.replace(/_/g, " ");
}
