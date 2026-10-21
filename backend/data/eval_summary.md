| Strategy | Rerank | Context Precision | Context Recall | Faithfulness | Answer Relevance | Latency p50 | Latency p95 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `fixed` | No | **0.979** | **0.909** | 0.738 | 0.913 | 15.5 ms | 2313.6 ms |
| `fixed` | Yes | **0.958** | **0.911** | 0.750 | 0.909 | 655.3 ms | 1820.7 ms |
| `hierarchical` | No | **0.905** | **0.895** | 0.750 | 0.913 | 15.2 ms | 23.4 ms |
| `hierarchical` | Yes | **0.848** | **0.882** | 0.600 | 0.913 | 305.6 ms | 370.9 ms |
| `semantic` | No | **0.833** | **0.859** | 0.591 | 0.911 | 16.4 ms | 26.4 ms |
| `semantic` | Yes | **0.900** | **0.861** | 0.658 | 0.908 | 277.4 ms | 526.5 ms |
