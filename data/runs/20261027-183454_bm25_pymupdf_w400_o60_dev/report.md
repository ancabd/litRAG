# Retrieval eval: bm25

- **Retriever:** `{"name": "bm25", "k1": 1.2, "b": 0.75, "include_title": true, "include_section": true}`
- **Chunks:** pymupdf_w400_o60 (parser pymupdf@2)
- **Questions:** 27 scored of 32 (split: dev, file sha1 9e6de1d92dea)
- **Commit:** 273e162-dirty   **Created:** 2026-10-27T17:34:54+00:00
- **Speed:** index 1.376s, 0.13 ms/query

## Overall

Mean with 95% bootstrap CI over questions. **Strict** counts only the original evidence; **lenient** also accepts the alternative passages you marked (3 evidence items have alternatives).

| metric | strict | lenient |
|---|---|---|
| hit@1 | 0.259 [0.11, 0.44] | 0.333 [0.19, 0.52] |
| hit@5 | 0.556 [0.37, 0.74] | 0.667 [0.48, 0.85] |
| hit@10 | 0.593 [0.41, 0.78] | 0.704 [0.56, 0.85] |
| recall@10 | 0.537 [0.37, 0.70] | 0.630 [0.46, 0.80] |
| mrr | 0.377 [0.24, 0.53] | 0.461 [0.32, 0.62] |
| ndcg@10 | 0.376 [0.24, 0.52] | 0.431 [0.31, 0.57] |
| paper_hit@10 | 0.815 [0.67, 0.96] | 0.889 [0.78, 1.00] |

**judged@10: 0.09**, the share of each question's top 10 that you have judged (evidence, alternative or not relevant). Below ~0.5, unjudged passages may still answer questions, so even the lenient score can undercount; review them in the app.

## By question type and tag

| group | n | hit@5 | lenient_hit@5 | mrr | lenient_mrr |
|---|---|---|---|---|---|
| tag:behler-parrinello | 6 | 0.33 | 0.67 | 0.22 | 0.55 |
| tag:definition | 5 | 0.80 | 1.00 | 0.71 | 0.77 |
| tag:difftre | 10 | 0.80 | 0.80 | 0.56 | 0.56 |
| tag:equation | 6 | 0.67 | 0.67 | 0.44 | 0.44 |
| tag:nequip | 7 | 0.29 | 0.57 | 0.21 | 0.39 |
| tag:numeric | 3 | 1.00 | 1.00 | 0.58 | 0.58 |
| tag:schnet | 9 | 0.56 | 0.56 | 0.41 | 0.41 |
| type:comparison | 5 | 0.20 | 0.40 | 0.23 | 0.43 |
| type:lookup | 19 | 0.63 | 0.74 | 0.41 | 0.47 |
| type:multihop | 3 | 0.67 | 0.67 | 0.43 | 0.43 |

_Groups with fewer than 10 questions (tag:behler-parrinello, tag:definition, tag:equation, tag:nequip, tag:numeric, tag:schnet, type:comparison, type:multihop) are anecdotal; don't read much into differences there._

**Found only through alternatives** (strict miss, lenient hit): q001, q004, q005. The retriever found a passage that answers the question, but not the original source.

## Misses: nothing acceptable in the top 10 (8)

Unjudged passages listed here are worth reviewing in the app: they may answer the question.

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

**q028** (lookup, difftre): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- gold: Learning neural network potentials from experimental data vi › 3 Discussion
- got #1: Learning neural network potentials from experimental data vi › Coarse-grained water model (unjudged)
- got #2: Refining potential energy surface through dynamical properti › Transferability to Other Properties (unjudged)
- got #3: A practical guide to machine learning interatomic potentials › 7 MLIP Choices – What Should I Use When? (unjudged)

**q030** (multihop, difftre, behler-parrinello): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- gold: Learning neural network potentials from experimental data vi › Atomistic model of Diamond; Generalized Neural-Network Representation of High-Dimensiona › Generalized Neural-Network Representatio
- got #1: Gaussian Process Regression for Materials and Molecules › Prediction (unjudged)
- got #2: Recent advances and applications of machine learning in soli › Front matter (unjudged)
- got #3: A fast neural network approach for direct covariant forces p › System A (unjudged)

## Data issues

- q019 excluded: no evidence quote matched any chunk; run `evaluate.py check`
- q020 excluded: no evidence quote matched any chunk; run `evaluate.py check`
- q021 excluded: unanswerable (scored in the answer eval, not here)
- q022 excluded: unanswerable (scored in the answer eval, not here)
- q033 excluded: unanswerable (scored in the answer eval, not here)
