# Retrieval eval: hybrid

- **Retriever:** `{"name": "hybrid", "fusion": "rrf", "k_rrf": 60, "candidates": 100, "bm25": {"name": "bm25", "k1": 1.2, "b": 0.75, "include_title": true, "include_section": true}, "dense": {"name": "dense", "model": "BAAI/bge-small-en-v1.5", "preset": "bge-small", "query_prefix": "Represent this sentence for searching relevant passages: ", "doc_prefix": "", "max_tokens": 512, "text": "title - section + chunk"}}`
- **Chunks:** pymupdf_w400_o60 (parser pymupdf@2)
- **Questions:** 27 scored of 32 (split: dev, file sha1 487184e30344)
- **Commit:** ddd18aa-dirty   **Created:** 2026-10-27T15:01:56+00:00
- **Speed:** index 1.438s, 80.63 ms/query

## Overall

Mean with 95% bootstrap CI over questions. **Strict** counts only the original evidence; **lenient** also accepts the alternative passages you marked (2 evidence items have alternatives).

| metric | strict | lenient |
|---|---|---|
| hit@1 | 0.259 [0.11, 0.41] | 0.259 [0.11, 0.41] |
| hit@5 | 0.630 [0.44, 0.81] | 0.667 [0.48, 0.85] |
| hit@10 | 0.704 [0.52, 0.85] | 0.778 [0.63, 0.93] |
| recall@10 | 0.630 [0.44, 0.78] | 0.685 [0.52, 0.83] |
| mrr | 0.393 [0.25, 0.54] | 0.417 [0.28, 0.56] |
| ndcg@10 | 0.412 [0.28, 0.54] | 0.432 [0.31, 0.56] |
| paper_hit@10 | 0.963 [0.89, 1.00] | 0.963 [0.89, 1.00] |

**judged@10: 0.09**, the share of each question's top 10 that you have judged (evidence, alternative or not relevant). Below ~0.5, unjudged passages may still answer questions, so even the lenient score can undercount; review them in the app.

## By question type and tag

| group | n | hit@5 | lenient_hit@5 | mrr | lenient_mrr |
|---|---|---|---|---|---|
| tag:behler-parrinello | 6 | 0.67 | 0.67 | 0.47 | 0.50 |
| tag:definition | 5 | 0.60 | 0.80 | 0.63 | 0.73 |
| tag:difftre | 10 | 0.90 | 0.90 | 0.49 | 0.49 |
| tag:equation | 6 | 0.50 | 0.50 | 0.30 | 0.30 |
| tag:nequip | 7 | 0.43 | 0.57 | 0.23 | 0.32 |
| tag:numeric | 3 | 1.00 | 1.00 | 0.78 | 0.78 |
| tag:schnet | 9 | 0.56 | 0.56 | 0.47 | 0.47 |
| type:comparison | 5 | 0.60 | 0.60 | 0.28 | 0.31 |
| type:lookup | 19 | 0.58 | 0.63 | 0.37 | 0.40 |
| type:multihop | 3 | 1.00 | 1.00 | 0.73 | 0.73 |

_Groups with fewer than 10 questions (tag:behler-parrinello, tag:definition, tag:equation, tag:nequip, tag:numeric, tag:schnet, type:comparison, type:multihop) are anecdotal; don't read much into differences there._

**Found only through alternatives** (strict miss, lenient hit): q004, q005. The retriever found a passage that answers the question, but not the original source.

## Misses: nothing acceptable in the top 10 (6)

Unjudged passages listed here are worth reviewing in the app: they may answer the question.

**q001** (lookup, behler-parrinello): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- gold: Generalized Neural-Network Representation of High-Dimensiona › Generalized Neural-Network Representatio
- got #1: JAX, M.D.: End-to-End Differentiable, Hardware Accelerated,  › 4 Three Vignettes > 4.1 Neural Network P (unjudged)
- got #2: Machine Learning for Molecular Simulation › 4 Deep Learning Architectures for Molecu (unjudged)
- got #3: Machine Learning for Molecular Simulation › E Total energy (unjudged)

**q008** (lookup, nequip): What does Nequip do as a first step in the architecture?
- gold: E(3)-equivariant graph neural networks for data-efficient an › RESULTS
- got #1: Scalable Parallel Algorithm for Graph Neural Network Interat › TENTIAL > 2.2 NequIP Structure (unjudged)
- got #2: Scalable Parallel Algorithm for Graph Neural Network Interat › TENTIAL > 2.2 NequIP Structure (unjudged)
- got #3: E(3)-equivariant graph neural networks for data-efficient an › Experiments (unjudged)

**q009** (lookup): What datasets is Nequip tested on?
- gold: E(3)-equivariant graph neural networks for data-efficient an › Experiments
- got #1: DPA-2: a large atomic model as a multi-task learner › S10 Training details of GemNet-OC/Equifo (unjudged)
- got #2: Scaling deep learning for materials discovery › Article Methods (unjudged)
- got #3: E(3)-equivariant graph neural networks for data-efficient an › METHODS (unjudged)

**q011** (lookup, equation, schnet): How does SchNet turn an interatomic distance into the input of its filter network?
- gold: SchNet – A deep learning architecture for molecules and mate › 1. Rotational invariance
- got #1: SchNet: A continuous-filter convolutional neural network for › 4 SchNet > 4.1 Architecture (unjudged)
- got #2: SchNet – A deep learning architecture for molecules and mate › D. Filter-generating networks (unjudged)
- got #3: SchNet: A continuous-filter convolutional neural network for › 2 Related work (unjudged)

**q012** (lookup, equation, schnet): Which activation function does SchNet use, and why does that matter for force fields?
- gold: SchNet – A deep learning architecture for molecules and mate › C. Interaction blocks
- got #1: SpookyNet: Learning force fields with electronic degrees of  › SchNet and PaiNN training (unjudged)
- got #2: SchNet: A continuous-filter convolutional neural network for › 4 SchNet > 4.2 Training with energies an (unjudged)
- got #3: SchNet – A deep learning architecture for molecules and mate › IV. CONCLUSIONS (unjudged)

**q016** (comparison, schnet, nequip): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- gold: SchNet – A deep learning architecture for molecules and mate › 1. Rotational invariance; E(3)-equivariant graph neural networks for data-efficient an › Data Efficiency
- got #1: SchNet: A continuous-filter convolutional neural network for › 3 Continuous-filter convolutions (unjudged)
- got #2: SchNet: A continuous-filter convolutional neural network for › 2 Related work (unjudged)
- got #3: SchNet – A deep learning architecture for molecules and mate › E. Property prediction (unjudged)

## Data issues

- q019 excluded: no evidence quote matched any chunk; run `evaluate.py check`
- q020 excluded: no evidence quote matched any chunk; run `evaluate.py check`
- q021 excluded: unanswerable (scored in the answer eval, not here)
- q022 excluded: unanswerable (scored in the answer eval, not here)
- q033 excluded: unanswerable (scored in the answer eval, not here)
