# Retrieval eval: bm25

- **Retriever:** `{"name": "bm25", "k1": 1.2, "b": 0.75, "include_title": true, "include_section": true}`
- **Chunks:** pymupdf_w400_o60 (parser pymupdf@2)
- **Questions:** 8 scored of 8 (split: dev, file sha1 750ea9043f6d)
- **Commit:** a33bedf-dirty   **Created:** 2026-10-16T13:17:05+00:00
- **Speed:** index 1.26s, 0.18 ms/query

## Overall

Mean with 95% bootstrap CI over questions. **Strict** counts only the original evidence; **lenient** also accepts the alternative passages you marked (1 evidence item has alternatives).

| metric | strict | lenient |
|---|---|---|
| hit@1 | 0.125 [0.00, 0.38] | 0.250 [0.00, 0.62] |
| hit@5 | 0.250 [0.00, 0.62] | 0.375 [0.00, 0.75] |
| hit@10 | 0.375 [0.12, 0.75] | 0.500 [0.12, 0.88] |
| recall@10 | 0.312 [0.06, 0.62] | 0.375 [0.12, 0.69] |
| mrr | 0.170 [0.01, 0.42] | 0.295 [0.03, 0.62] |
| ndcg@10 | 0.196 [0.02, 0.45] | 0.255 [0.05, 0.51] |
| paper_hit@10 | 0.625 [0.25, 0.88] | 0.750 [0.38, 1.00] |

**judged@10: 0.05**, the share of each question's top 10 that you have judged (evidence, alternative or not relevant). Below ~0.5, unjudged passages may still answer questions, so even the lenient score can undercount; review them in the app.

## By question type and tag

| group | n | hit@5 | lenient_hit@5 | mrr | lenient_mrr |
|---|---|---|---|---|---|
| tag:behler-parrinello | 4 | 0.50 | 0.75 | 0.31 | 0.56 |
| tag:definition | 2 | 0.50 | 0.50 | 0.50 | 0.50 |
| tag:equation | 2 | 1.00 | 1.00 | 0.62 | 0.62 |
| tag:nequip | 4 | 0.00 | 0.25 | 0.03 | 0.28 |
| type:comparison | 2 | 0.00 | 0.50 | 0.06 | 0.56 |
| type:lookup | 6 | 0.33 | 0.33 | 0.21 | 0.21 |

_Groups with fewer than 10 questions (tag:behler-parrinello, tag:definition, tag:equation, tag:nequip, type:comparison, type:lookup) are anecdotal; don't read much into differences there._

**Found only through alternatives** (strict miss, lenient hit): q005. The retriever found a passage that answers the question, but not the original source.

## Misses: nothing acceptable in the top 10 (4)

Unjudged passages listed here are worth reviewing in the app: they may answer the question.

**q001** (lookup, behler-parrinello): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- gold: Generalized Neural-Network Representation of High-Dimensiona › Generalized Neural-Network Representatio
- got #1: JAX, M.D.: End-to-End Differentiable, Hardware Accelerated,  › 4 Three Vignettes > 4.1 Neural Network P (unjudged)
- got #2: JAX, M.D.: End-to-End Differentiable, Hardware Accelerated,  › 4 Three Vignettes > 4.1 Neural Network P (unjudged)
- got #3: Machine Learning for Molecular Simulation › 4 Deep Learning Architectures for Molecu (unjudged)

**q004** (lookup, definition, nequip): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- gold: E(3)-equivariant graph neural networks for data-efficient an › Potentials
- got #1: The design space of E(3)-equivariant atom-centred interatomi › Front matter (unjudged)
- got #2: The design space of E(3)-equivariant atom-centred interatomi › Number of parameters (unjudged)
- got #3: Learning local equivariant representations for large-scale a › Front matter (unjudged)

**q008** (lookup, nequip): What does Nequip do as a first step in the architecture?
- gold: E(3)-equivariant graph neural networks for data-efficient an › RESULTS
- got #1: Scalable Parallel Algorithm for Graph Neural Network Interat › TENTIAL > 2.2 NequIP Structure (unjudged)
- got #2: Scalable Parallel Algorithm for Graph Neural Network Interat › TENTIAL > 2.2 NequIP Structure (unjudged)
- got #3: Scalable Parallel Algorithm for Graph Neural Network Interat › 3 PARALLELIZATION of GNN-IP > 3.2 Implem (unjudged)

**q009** (lookup): What datasets is Nequip tested on?
- gold: E(3)-equivariant graph neural networks for data-efficient an › Experiments
- got #1: DPA-2: a large atomic model as a multi-task learner › S10 Training details of GemNet-OC/Equifo (unjudged)
- got #2: DPA-2: a large atomic model as a multi-task learner › S2 Single-task benchmark of the generali (unjudged)
- got #3: DPA-2: a large atomic model as a multi-task learner › S10 Training details of GemNet-OC/Equifo (unjudged)

