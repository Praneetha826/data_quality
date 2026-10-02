# Performance Measurement Report

**Generated:** 2026-09-23T16:17:54.495342

**Total Datasets Measured:** 3

## Average Performance (by operation)

| Operation | Avg Time (s) |
|-----------|--------------|
| File Loading | 0.0072 |
| Quality Assessment | 0.0125 |
| Metadata Generation | 0.0032 |
| Embedding Generation | 7.8812 |
| Faiss Indexing | 0.0095 |
| Faiss Retrieval | 0.0120 |
| Rag Setup | 0.0000 |
| Rag Query | 0.0117 |
| Total Pipeline | 7.9372 |

## Detailed Results

### clean_dataset.csv

- **Quality Score:** 95.0/100

**Timings:**
- File Loading: 0.0084s
- Quality Assessment: 0.0146s
- Metadata Generation: 0.0035s
- Embedding Generation: 8.4052s
- Faiss Indexing: 0.0115s
- Faiss Retrieval: 0.013s
- Rag Setup: 0.0s
- Rag Query: 0.0123s
- Total Pipeline: 8.4684s

---

### missing_values.csv

- **Quality Score:** 75.0/100

**Timings:**
- File Loading: 0.0081s
- Quality Assessment: 0.0117s
- Metadata Generation: 0.004s
- Embedding Generation: 7.4427s
- Faiss Indexing: 0.0091s
- Faiss Retrieval: 0.011s
- Rag Setup: 0.0s
- Rag Query: 0.0103s
- Total Pipeline: 7.4969s

---

### mixed_quality_dataset.csv

- **Quality Score:** 60.0/100

**Timings:**
- File Loading: 0.005s
- Quality Assessment: 0.0111s
- Metadata Generation: 0.002s
- Embedding Generation: 7.7956s
- Faiss Indexing: 0.008s
- Faiss Retrieval: 0.012s
- Rag Setup: 0.0s
- Rag Query: 0.0126s
- Total Pipeline: 7.8463s

---

