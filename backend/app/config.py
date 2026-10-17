"""Single source of truth for all tunable constants (mirrors IMPLEMENTATION_PLAN.md)."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CORPUS_DIR = DATA_DIR / "corpus"
INDEX_DIR = DATA_DIR / "index"
DB_PATH = INDEX_DIR / "sentinel.db"

# Embeddings
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DIM = 384
EMBED_BATCH = 32
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

TOKENIZER_ENCODING = "cl100k_base"

# Chunking
STRATEGIES = ("fixed", "hierarchical", "semantic")
FIXED_CHUNK_TOKENS = 512
FIXED_OVERLAP_TOKENS = 50
HIER_PARENT_TOKENS = 1024
HIER_CHILD_TOKENS = 256
SEMANTIC_BREAKPOINT_PERCENTILE = 25
SEMANTIC_MAX_CHUNK_TOKENS = 512

# Retrieval
BM25_TOP_K = 20
VECTOR_TOP_K = 20
RRF_K = 60
FINAL_TOP_K = 5
SIMPLE_TOP_K = 3

# LLM provider (OpenAI-compatible). Router, grader, HyDE and generation all run on
# Groq's gpt-oss-120b. It is a reasoning model, so max_tokens must leave room for
# the hidden reasoning tokens before the visible output.
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-120b"

ROUTER_TEMP = 0.0
GRADER_TEMP = 0.0
GEN_TEMP = 0.3
HYDE_TEMP = 0.7
ROUTER_MAX_TOKENS = 512
GRADER_MAX_TOKENS = 512
HYDE_MAX_TOKENS = 1024
GEN_MAX_TOKENS = 1536

# LLM reliability
LLM_TIMEOUT = 30.0
LLM_MAX_RETRIES = 2
LLM_RETRY_BACKOFF = 2.0

# Self-correction
GRADER_THRESHOLD = 0.6
MAX_RETRIES = 2

# API server
API_HOST = "127.0.0.1"
API_PORT = 8000
FRONTEND_ORIGIN = "http://localhost:3000"
MAX_CONCURRENT_PIPELINES = 2

# Input guard
MAX_QUERY_CHARS = 2000
