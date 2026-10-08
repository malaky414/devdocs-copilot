# Retrieval Evaluation

- Golden questions: **30**
- Candidate limit: **20**
- Final limit: **5**

## Results

| System | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---:|---:|---:|
| Dense | 0.333 | 0.600 | 0.667 | 0.483 |
| BM25 | 0.300 | 0.533 | 0.667 | 0.432 |
| Hybrid RRF | 0.467 | 0.700 | 0.800 | 0.592 |
| Hybrid + Rerank | 0.600 | 0.800 | 0.933 | 0.715 |

## Metric Definitions

- **Hit@k**: fraction of questions where an expected source file appears within the top-k results.
- **MRR**: mean reciprocal rank of the first result whose source file is expected.

## Retrieval Pipeline

```text
Dense Top-20 ─────┐
                  ├──> RRF Top-20 ──> Cross-Encoder ──> Top-5
BM25 Top-20 ──────┘
```
