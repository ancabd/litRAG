# Retrieval eval: bm25

- **Retriever:** `{"name": "bm25", "k1": 1.2, "b": 0.75, "include_title": true, "include_section": true}`
- **Chunks:** pymupdf_w400_o60 (parser pymupdf@2)
- **Questions:** 17 scored of 21 (split: dev, file sha1 8dd6f14cec1a)
- **Commit:** 75105d3-dirty   **Created:** 2026-10-16T14:33:13+00:00
- **Speed:** index 1.327s, 0.18 ms/query

## Overall

Mean with 95% bootstrap CI over questions. **Strict** counts only the original evidence; **lenient** also accepts the alternative passages you marked (2 evidence items have alternatives).

| metric | strict | lenient |
|---|---|---|
| hit@1 | 0.176 [0.00, 0.35] | 0.235 [0.06, 0.41] |
| hit@5 | 0.412 [0.18, 0.65] | 0.471 [0.24, 0.71] |
| hit@10 | 0.471 [0.24, 0.71] | 0.588 [0.35, 0.82] |
| recall@10 | 0.412 [0.21, 0.65] | 0.500 [0.29, 0.74] |
| mrr | 0.268 [0.11, 0.45] | 0.337 [0.16, 0.53] |
| ndcg@10 | 0.288 [0.13, 0.48] | 0.329 [0.17, 0.51] |
| paper_hit@10 | 0.706 [0.47, 0.88] | 0.765 [0.53, 0.94] |

**judged@10: 0.06**, the share of each question's top 10 that you have judged (evidence, alternative or not relevant). Below ~0.5, unjudged passages may still answer questions, so even the lenient score can undercount; review them in the app.

## By question type and tag

| group | n | hit@5 | lenient_hit@5 | mrr | lenient_mrr |
|---|---|---|---|---|---|
| tag:behler-parrinello | 5 | 0.40 | 0.60 | 0.25 | 0.45 |
| tag:definition | 3 | 0.67 | 0.67 | 0.67 | 0.72 |
| tag:equation | 5 | 0.60 | 0.60 | 0.33 | 0.33 |
| tag:nequip | 6 | 0.17 | 0.33 | 0.07 | 0.27 |
| tag:numeric | 1 | 1.00 | 1.00 | 1.00 | 1.00 |
| tag:schnet | 8 | 0.50 | 0.50 | 0.34 | 0.34 |
| type:comparison | 4 | 0.00 | 0.25 | 0.04 | 0.29 |
| type:lookup | 12 | 0.50 | 0.50 | 0.34 | 0.36 |
| type:multihop | 1 | 1.00 | 1.00 | 0.25 | 0.25 |

_Groups with fewer than 10 questions (tag:behler-parrinello, tag:definition, tag:equation, tag:nequip, tag:numeric, tag:schnet, type:comparison, type:multihop) are anecdotal; don't read much into differences there._

**Found only through alternatives** (strict miss, lenient hit): q004, q005. The retriever found a passage that answers the question, but not the original source.

## Misses: nothing acceptable in the top 10 (7)

Unjudged passages listed here are worth reviewing in the app: they may answer the question.

**q001** (lookup, behler-parrinello): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- gold: Generalized Neural-Network Representation of High-Dimensiona › Generalized Neural-Network Representatio
- got #1: JAX, M.D.: End-to-End Differentiable, Hardware Accelerated,  › 4 Three Vignettes > 4.1 Neural Network P (unjudged)
- got #2: JAX, M.D.: End-to-End Differentiable, Hardware Accelerated,  › 4 Three Vignettes > 4.1 Neural Network P (unjudged)
- got #3: Machine Learning for Molecular Simulation › 4 Deep Learning Architectures for Molecu (unjudged)

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

**q011** (lookup, equation, schnet): How does SchNet turn an interatomic distance into the input of its filter network?
- gold: SchNet – A deep learning architecture for molecules and mate › 1. Rotational invariance
- got #1: SchNet: A continuous-filter convolutional neural network for › 4 SchNet > 4.1 Architecture (unjudged)
- got #2: SchNet: A continuous-filter convolutional neural network for › 2 Related work (unjudged)
- got #3: E(3)-equivariant graph neural networks for data-efficient an › RESULTS (unjudged)

**q015** (lookup, equation, schnet): How does SchNet make sure its predicted forces conserve energy?
- gold: SchNet – A deep learning architecture for molecules and mate › E. Property prediction
- got #1: E(3)-equivariant graph neural networks for data-efficient an › Related Work (unjudged)
- got #2: How to validate machine-learned interatomic potentials › B. Scaling with system size (unjudged)
- got #3: SchNet: A continuous-filter convolutional neural network for › 5 Experiments and results > 5.3 ISO17 –  (unjudged)

**q016** (comparison, schnet, nequip): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- gold: SchNet – A deep learning architecture for molecules and mate › 1. Rotational invariance; E(3)-equivariant graph neural networks for data-efficient an › Data Efficiency
- got #1: Tensor field networks: Rotation- and translation-equivariant › 2 Related work (unjudged)
- got #2: E(3)-equivariant graph neural networks for data-efficient an › RESULTS (unjudged)
- got #3: E(3)-equivariant graph neural networks for data-efficient an › RESULTS (unjudged)

**q018** (comparison, schnet, behler-parrinello): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- gold: Generalized Neural-Network Representation of High-Dimensiona › Generalized Neural-Network Representatio; SchNet – A deep learning architecture for molecules and mate › A. Learning molecular properties
- got #1: Machine Learning for Molecular Simulation › 4 Deep Learning Architectures for Molecu (unjudged)
- got #2: Machine Learning for Molecular Simulation › E Total energy (unjudged)
- got #3: Machine Learning Force Fields › Energy conservation: > 2.3.4 Neural Netw (unjudged)

## Data issues

- q019 excluded: no evidence quote matched any chunk; run `evaluate.py check`
- q020 excluded: no evidence quote matched any chunk; run `evaluate.py check`
- q021 excluded: unanswerable (scored in the answer eval, not here)
- q022 excluded: unanswerable (scored in the answer eval, not here)
