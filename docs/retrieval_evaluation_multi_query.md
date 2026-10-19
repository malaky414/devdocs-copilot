# Retrieval Evaluation: Multi-Query

- Golden questions: **30**
- Hybrid candidate limit: **20**
- Per-query candidate limit: **50**
- Final limit: **5**
- Cached question expansions: **30**

## Results

| System | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---:|---:|---:|
| Dense | 0.333 | 0.600 | 0.667 | 0.483 |
| BM25 | 0.300 | 0.533 | 0.667 | 0.432 |
| Hybrid RRF | 0.467 | 0.700 | 0.800 | 0.592 |
| Hybrid + Rerank | 0.767 | 0.933 | 0.967 | 0.853 |
| Multi-Query Hybrid + Rerank | 0.767 | 0.900 | 0.967 | 0.837 |

## Change vs. Hybrid + Rerank

| Metric | Baseline | Multi-Query | Delta |
|---|---:|---:|---:|
| hit@1 | 0.767 | 0.767 | +0.000 |
| hit@3 | 0.933 | 0.900 | -0.033 |
| hit@5 | 0.967 | 0.967 | +0.000 |
| mrr | 0.853 | 0.837 | -0.016 |

## Metric Definitions

- **Hit@k**: fraction of questions with an expected source file in the top-k.
- **MRR**: mean reciprocal rank of the first expected source file.

This is retrieval evaluation, not a direct measure of answer faithfulness or factual correctness.
