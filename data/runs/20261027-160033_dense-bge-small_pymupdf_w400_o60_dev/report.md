# Retrieval eval: dense

- **Retriever:** `{"name": "dense", "model": "BAAI/bge-small-en-v1.5", "preset": "bge-small", "query_prefix": "Represent this sentence for searching relevant passages: ", "doc_prefix": "", "max_tokens": 512, "text": "title - section + chunk"}`
- **Chunks:** pymupdf_w400_o60 (parser pymupdf@2)
- **Questions:** 27 scored of 32 (split: dev, file sha1 487184e30344)
- **Commit:** ddd18aa-dirty   **Created:** 2026-10-27T15:00:33+00:00
- **Speed:** index 0.033s, 75.78 ms/query

## Overall

Mean with 95% bootstrap CI over questions. **Strict** counts only the original evidence; **lenient** also accepts the alternative passages you marked (2 evidence items have alternatives).

| metric | strict | lenient |
|---|---|---|
| hit@1 | 0.074 [0.00, 0.19] | 0.074 [0.00, 0.19] |
| hit@5 | 0.370 [0.19, 0.56] | 0.370 [0.19, 0.56] |
| hit@10 | 0.593 [0.41, 0.78] | 0.593 [0.41, 0.78] |
| recall@10 | 0.500 [0.33, 0.67] | 0.500 [0.33, 0.67] |
| mrr | 0.201 [0.11, 0.31] | 0.203 [0.12, 0.31] |
| ndcg@10 | 0.241 [0.15, 0.34] | 0.241 [0.15, 0.34] |
| paper_hit@10 | 0.963 [0.89, 1.00] | 0.963 [0.89, 1.00] |

**judged@10: 0.07**, the share of each question's top 10 that you have judged (evidence, alternative or not relevant). Below ~0.5, unjudged passages may still answer questions, so even the lenient score can undercount; review them in the app.

## By question type and tag

| group | n | hit@5 | lenient_hit@5 | mrr | lenient_mrr |
|---|---|---|---|---|---|
| tag:behler-parrinello | 6 | 0.50 | 0.50 | 0.32 | 0.32 |
| tag:definition | 5 | 0.40 | 0.40 | 0.19 | 0.20 |
| tag:difftre | 10 | 0.60 | 0.60 | 0.20 | 0.20 |
| tag:equation | 6 | 0.17 | 0.17 | 0.13 | 0.13 |
| tag:nequip | 7 | 0.29 | 0.29 | 0.12 | 0.12 |
| tag:numeric | 3 | 0.67 | 0.67 | 0.50 | 0.50 |
| tag:schnet | 9 | 0.33 | 0.33 | 0.29 | 0.29 |
| type:comparison | 5 | 0.60 | 0.60 | 0.28 | 0.28 |
| type:lookup | 19 | 0.26 | 0.26 | 0.17 | 0.17 |
| type:multihop | 3 | 0.67 | 0.67 | 0.25 | 0.25 |

_Groups with fewer than 10 questions (tag:behler-parrinello, tag:definition, tag:equation, tag:nequip, tag:numeric, tag:schnet, type:comparison, type:multihop) are anecdotal; don't read much into differences there._

## Misses: nothing acceptable in the top 10 (11)

Unjudged passages listed here are worth reviewing in the app: they may answer the question.

**q001** (lookup, behler-parrinello): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- gold: Generalized Neural-Network Representation of High-Dimensiona › Generalized Neural-Network Representatio
- got #1: Machine Learning for Molecular Simulation › 4 Deep Learning Architectures for Molecu (unjudged)
- got #2: JAX, M.D.: End-to-End Differentiable, Hardware Accelerated,  › 4 Three Vignettes > 4.1 Neural Network P (unjudged)
- got #3: Performance and Cost Assessment of Machine Learning Interato › A. Behler-Parrinello neural network (unjudged)

**q004** (lookup, definition, nequip): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- gold: E(3)-equivariant graph neural networks for data-efficient an › Potentials
- got #1: E(3)-equivariant graph neural networks for data-efficient an › Data Efficiency (unjudged)
- got #2: UNiTE: Unitary N-body Tensor Equivariant Network with Applic › S2.2 Equivariance (unjudged)
- got #3: E(3)-equivariant graph neural networks for data-efficient an › RESULTS (unjudged)

**q005** (comparison, behler-parrinello, nequip): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- gold: Generalized Neural-Network Representation of High-Dimensiona › Generalized Neural-Network Representatio; E(3)-equivariant graph neural networks for data-efficient an › RESULTS
- got #1: E(3)-equivariant graph neural networks for data-efficient an › Data Efficiency (unjudged)
- got #2: On representing chemical environments › F. Parrinello-Behler descriptor (unjudged)
- got #3: E(3)-equivariant graph neural networks for data-efficient an › RESULTS (unjudged)

**q008** (lookup, nequip): What does Nequip do as a first step in the architecture?
- gold: E(3)-equivariant graph neural networks for data-efficient an › RESULTS
- got #1: Scalable Parallel Algorithm for Graph Neural Network Interat › TENTIAL > 2.2 NequIP Structure (unjudged)
- got #2: Scalable Parallel Algorithm for Graph Neural Network Interat › TENTIAL > 2.2 NequIP Structure (unjudged)
- got #3: E(3)-equivariant graph neural networks for data-efficient an › Data Efficiency (unjudged)

**q009** (lookup): What datasets is Nequip tested on?
- gold: E(3)-equivariant graph neural networks for data-efficient an › Experiments
- got #1: E(3)-equivariant graph neural networks for data-efficient an › METHODS (unjudged)
- got #2: E(3)-equivariant graph neural networks for data-efficient an › Data Efficiency (unjudged)
- got #3: DPA-2: a large atomic model as a multi-task learner › S10 Training details of GemNet-OC/Equifo (unjudged)

**q011** (lookup, equation, schnet): How does SchNet turn an interatomic distance into the input of its filter network?
- gold: SchNet – A deep learning architecture for molecules and mate › 1. Rotational invariance
- got #1: SchNet – A deep learning architecture for molecules and mate › D. Filter-generating networks (unjudged)
- got #2: SchNet: A continuous-filter convolutional neural network for › 4 SchNet > 4.1 Architecture (unjudged)
- got #3: SchNet: A continuous-filter convolutional neural network for › 4 SchNet (unjudged)

**q012** (lookup, equation, schnet): Which activation function does SchNet use, and why does that matter for force fields?
- gold: SchNet – A deep learning architecture for molecules and mate › C. Interaction blocks
- got #1: SpookyNet: Learning force fields with electronic degrees of  › SchNet and PaiNN training (unjudged)
- got #2: SchNet: A continuous-filter convolutional neural network for › 4 SchNet (unjudged)
- got #3: SchNet: A continuous-filter convolutional neural network for › 4 SchNet > 4.2 Training with energies an (unjudged)

**q015** (lookup, equation, schnet): How does SchNet make sure its predicted forces conserve energy?
- gold: SchNet – A deep learning architecture for molecules and mate › E. Property prediction
- got #1: SchNet: A continuous-filter convolutional neural network for › 4 SchNet (unjudged)
- got #2: SchNet: A continuous-filter convolutional neural network for › 4 SchNet > 4.2 Training with energies an (unjudged)
- got #3: SchNet: A continuous-filter convolutional neural network for › 5 Experiments and results > 5.2 MD17 – c (unjudged)

**q016** (comparison, schnet, nequip): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- gold: SchNet – A deep learning architecture for molecules and mate › 1. Rotational invariance; E(3)-equivariant graph neural networks for data-efficient an › Data Efficiency
- got #1: SchNet: A continuous-filter convolutional neural network for › 2 Related work (unjudged)
- got #2: SchNet: A continuous-filter convolutional neural network for › 4 SchNet (unjudged)
- got #3: SchNet: A continuous-filter convolutional neural network for › 3 Continuous-filter convolutions (unjudged)

**q023** (lookup, definition, difftre): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- gold: Learning neural network potentials from experimental data vi › 1 Introduction
- got #1: Learning neural network potentials from experimental data vi › 8 Contributions (unjudged)
- got #2: Learning neural network potentials from experimental data vi › 6 Code availability (unjudged)
- got #3: Learning neural network potentials from experimental data vi › Double-well toy example (unjudged)

**q024** (lookup, equation, difftre): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- gold: Learning neural network potentials from experimental data vi › Differentiable Trajectory Reweighting
- got #1: Learning neural network potentials from experimental data vi › Differentiable Trajectory Reweighting (unjudged)
- got #2: Learning neural network potentials from experimental data vi › Differentiable Trajectory Reweighting (unjudged)
- got #3: Learning neural network potentials from experimental data vi › Statistical mechanics foundations (unjudged)

## Data issues

- q019 excluded: no evidence quote matched any chunk; run `evaluate.py check`
- q020 excluded: no evidence quote matched any chunk; run `evaluate.py check`
- q021 excluded: unanswerable (scored in the answer eval, not here)
- q022 excluded: unanswerable (scored in the answer eval, not here)
- q033 excluded: unanswerable (scored in the answer eval, not here)
