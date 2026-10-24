# Retrieval eval: bm25

- **Retriever:** `{"name": "bm25", "k1": 1.2, "b": 0.75, "include_title": true, "include_section": true}`
- **Chunks:** pymupdf_w400_o60 (parser pymupdf@2)
- **Questions:** 5 scored of 6 (split: dev, file sha1 c966967f6e5a)
- **Commit:** a33bedf-dirty   **Created:** 2026-10-16T11:41:17+00:00
- **Speed:** index 1.288s, 0.2 ms/query

## Overall

Mean with 95% bootstrap CI over questions. **Strict** counts only the original evidence; **lenient** also accepts the alternative passages you marked (0 evidence items have alternatives).

| metric | strict | lenient |
|---|---|---|
| hit@1 | 0.200 [0.00, 0.60] | 0.200 [0.00, 0.60] |
| hit@5 | 0.400 [0.00, 0.80] | 0.400 [0.00, 0.80] |
| hit@10 | 0.400 [0.00, 0.80] | 0.400 [0.00, 0.80] |
| recall@10 | 0.400 [0.00, 0.80] | 0.400 [0.00, 0.80] |
| mrr | 0.250 [0.00, 0.60] | 0.250 [0.00, 0.60] |
| ndcg@10 | 0.286 [0.00, 0.66] | 0.286 [0.00, 0.66] |
| paper_hit@10 | 0.600 [0.20, 1.00] | 0.600 [0.20, 1.00] |

**judged@10: 0.04**, the share of each question's top 10 that you have judged (evidence, alternative or not relevant). Below ~0.5, unjudged passages may still answer questions, so even the lenient score can undercount; review them in the app.

## By question type and tag

| group | n | hit@5 | lenient_hit@5 | mrr | lenient_mrr |
|---|---|---|---|---|---|
| tag:behler-parrinello | 4 | 0.50 | 0.50 | 0.31 | 0.31 |
| tag:definition | 2 | 0.50 | 0.50 | 0.50 | 0.50 |
| tag:equation | 2 | 1.00 | 1.00 | 0.62 | 0.62 |
| tag:nequip | 2 | 0.00 | 0.00 | 0.00 | 0.00 |
| type:comparison | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| type:lookup | 4 | 0.50 | 0.50 | 0.31 | 0.31 |

_Groups with fewer than 10 questions (tag:behler-parrinello, tag:definition, tag:equation, tag:nequip, type:comparison, type:lookup) are anecdotal; don't read much into differences there._

## Misses: nothing acceptable in the top 10 (3)

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

**q005** (comparison, behler-parrinello, nequip): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- gold: Generalized Neural-Network Representation of High-Dimensiona › Generalized Neural-Network Representatio; E(3)-equivariant graph neural networks for data-efficient an › RESULTS
- got #1: Machine Learning for Molecular Simulation › 4 Deep Learning Architectures for Molecu (unjudged)
- got #2: Deep Potential Molecular Dynamics: A Scalable Model with the › Abstract (unjudged)
- got #3: Performance and Cost Assessment of Machine Learning Interato › A. Behler-Parrinello neural network (unjudged)

## Data issues

- q007 excluded: unanswerable (scored in the answer eval, not here)
