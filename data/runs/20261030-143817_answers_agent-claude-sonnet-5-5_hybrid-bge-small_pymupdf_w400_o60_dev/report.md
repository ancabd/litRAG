# Answer eval: claude-sonnet-5-5

- **Generator:** `{"name": "agent", "provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "agent-v3", "tools": ["search", "read_around", "open_paper"], "max_turns": 8, "token_budget": 100000}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1"}`
- **Retrieval:** hybrid, top 5 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 9e6de1d92dea)
- **Cost:** generator $0.753, judge $0.303

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.93 [0.84, 1.00] | 28 |
| Supported by its citations | 1.00 [1.00, 1.00] | 5 |
| Cites your evidence | 0.70 [0.52, 0.85] | 27 |
| Evidence was retrieved | 0.74 [0.59, 0.89] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 28 |
| Declines when unanswerable | 1.00 [1.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.03 [0.00, 0.10] | 29 |

Correct when the evidence was retrieved: 1.00 (n=20)

Correct when no evidence was retrieved: 0.92 (n=6)

## Effort per question (mean)

2.5 model calls, 1.8 tool calls (1.7 searches), 7.7 passages read, 12,615 input tokens, $0.0235 per question, 6.6 s. Gave up on 12%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: Behler and Parrinello demonstrated their neural network potential on bulk silicon. Their abstract says the method's "high accuracy ... is demonstrated for bulk silicon and compared with empirical potentials and DFT" [W2025444507#000]. A review of the work adds that the potential reproduced DFT energies to within 5 meV/atom. It also says molecular dynamics runs with the potential reproduced the radial distribution function (RDF) of a silicon melt at 3000 K [W2968923792#056].
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: correct (The answer identifies bulk silicon as the test system and mentions comparison with DFT, matching the reference; the extra details do not contradict it.)
- support: supported (The abstract quote appears verbatim in W2025444507, and the review passage W2968923792#056 states the 5 meV/atom DFT energy error and the RDF reproduction of a silicon melt at 3000 K.)

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: In the original high-dimensional neural network potential (Behler and Parrinello, 2007), the cutoff function is a cosine, written here from the garbled equation in the passage. It depends on the interatomic distance R_ij and the cutoff radius R_c:

fc(R_ij) = 0.5 · [cos(π R_ij / R_c) + 1] for R_ij ≤ R_c, and fc(R_ij) = 0 for R_ij > R_c [W2025444507#004].

The function gives zero value and zero slope at separations beyond R_c. The paper used R_c = 6 Å [W2025444507#005].
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: correct (The answer gives the same cosine cutoff, 0.5[cos(pi R/R_c)+1] for R <= R_c and 0 beyond, matching the reference; the extra details about zero slope and R_c = 6 Å do not contradict it.)
- support: None (judge returned no valid verdict: )

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: In a high-dimensional neural network potential (HDNNP), the total energy E is the sum of environment-dependent atomic energy contributions: E = Σ_i E_i. Here i runs over all N atoms. [W2025444507#003][W4312043350#015]

Each E_i is the output of an atomic ("sub") neural network. The input to that network is a set of symmetry-function values describing the local environment of atom i. [W2025444507#003] The subnets share the same structure and weights, so swapping two atoms of the same type leaves the total energy unchanged. [W2025444507#003] The same network can also predict systems with different numbers of atoms. [W3093149769#038]
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states that total energy is the sum of atomic energies, each output by an atomic neural network from the local environment (via symmetry functions), matching the reference; the cutoff is implicit in 'local environment' and the extra detail is accurate.)
- support: None (judge returned no valid verdict: Checking each claim:

1. E = Σ_i E_i with i over N atoms: supported by W4312043350 and W2025444507.
2. Each E_i is output of an atomic subnet with symmetry-function inputs describing the local environ)

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP is equivariant to E(3), the group of rotations, reflections (parity) and translations in 3D [W4225405705#005]. Its internal features are geometric tensors that are equivariant to rotation and reflection [W4225405705#005]. Translation is handled separately. Convolutions are naturally translation invariant because their filters act on relative interatomic distance vectors [W4225405705#006].

How the features are built:
- **Feature type:** Each atom carries scalars, vectors and higher-order tensors. Formally, these are a direct sum of irreducible representations of O(3) [W4225405705#006].
- **Indexing:** The features V^(l,p)_acm are indexed by rotation order l = 0, 1, 2, ... and parity p ∈ {1, −1}, which together label the irreps of O(3). The other indices are atom a, channel c and representation index m ∈ [−l, l] [W4225405705#006].
- **Layers:** NequIP builds on the Tensor Field Network layers, with primitives implemented in e3nn [W4225405705#006].
- **Equivariant convolutions:** If a feature at layer k is rotated or reflected, the output of the convolution to layer k+1 transforms accordingly [W4225405705#006].
- **Filters:** The filters are constrained to be products of a learnable radial function and spherical harmonics, F(r_ij) = R(r_ij) Y^(l)_m(r̂_ij). The spherical harmonics are equivariant under SO(3) [W4225405705#006].
- **Radial function:** All learnable filter weights sit in R(r_ij), which is rotationally invariant. It is a small MLP acting on interatomic distances expressed in a chosen basis [W4225405705#006].
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: correct (The answer identifies E(3), describes features as O(3) irrep-indexed geometric tensors (l, parity), and notes filters built from spherical harmonics of relative position vectors combined via tensor-product (TFN) convolutions, matching the reference.)
- support: None (judge returned no valid verdict: {"verdict": "supported", "reason": "Every claim matches the cited passages: E(3) equivariance, geometric-tensor features, O(3) irrep indexing, TFN/e3nn, equivariant convolutions, the radial-times-sphe)

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: Behler-Parrinello networks and NequIP both respect rotational symmetry, but they do it in different ways. Behler-Parrinello networks make their inputs rotation-invariant. NequIP keeps its internal features rotation-equivariant.

**Behler-Parrinello.** The atom-centered symmetry functions (ACSF) convert each local atomic environment into numeric vectors that are rotationally and translationally invariant [W3000291311#028]. These vectors are built from radial terms (distances) and angular terms (the angles θijk between neighbors) [W2968923792#011]. They are fed into a dense network that outputs the atom's energy. That energy is therefore invariant "by design of the input feature functions" [W2988055229#031]. Only invariant scalars enter the network.

**NequIP.** It does not use fixed invariant descriptors. Each atom carries features that are tensors of different orders: scalars, vectors and higher-order tensors. These are indexed by rotation order l and parity p, which label irreducible representations of O(3) [W4225405705#006]. The convolutions are equivariant rather than invariant. If a feature is rotated, the next layer's output transforms accordingly [W4225405705#006]. The filters are products of a learnable radial function and spherical harmonics, F(r_ij) = R(r_ij) Y_m^(l)(r̂_ij). All the learnable weights sit in the rotationally invariant radial function R [W4225405705#006].

The NequIP paper presents this as its core difference from scalar-valued invariant models, and says the accuracy gains come from replacing invariant representations with equivariant ones [W4225405705#006][W4225405705#022].
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: correct (Matches the reference: BP uses fixed invariant symmetry-function descriptors, while NequIP uses learned equivariant tensor features via convolutions; the answer also notes the energy is invariant for BP and the equivariant features internally for NequIP, though it doesn't explicitly say the final NequIP energy is invariant.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- ACSF yields rotationally and translationally invariant vectors: supported by W3000291311#028.
- Radial terms (distances) and angular terms (θijk): supporte)
- steps: search "NequIP E(3)-equivariant interatomic potential compared to Behler-Parrinello symmetry functions invariant descriptors" (5 passages, 5 new); search "Behler-Parrinello atom-centered symmetry functions rotation invariance" (5 passages, 5 new); answer

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: NequIP's own paper names several features that it shares with SchNet.

- **Atomic-number embedding:** NequIP generates its initial feature with a trainable embedding of the atomic number Zi, given as a one-hot encoding. The paper says it does this "following SchNet" [W4225405705#009].
- **Atom-wise self-interaction layers:** NequIP updates atomic features with dense layers applied atom by atom, with weights shared across atoms. The paper describes these as "similar to the self-interaction layers in SchNet" [W4225405705#008].
- **Interaction blocks built on convolutions over interatomic distances:** NequIP's filters act on relative interatomic distance vectors. The radial part is a small MLP that takes the distances expressed in a basis [W4225405705#006]. SchNet likewise feeds radial-basis-expanded distances into a filter-generating network [W2726670313#009]. NequIP says that dropping all interactions above l = 0 leaves a conventional invariant GNN-IP with convolutions over scalar features, "similar to e.g. SchNet" [W4225405705#008]. The paper also calls this a "SchNet-style" setup [W4225405705#019].
- **Atom-wise energy output:** NequIP's output block gives a scalar atomic energy for each atom, and these are summed to the total energy. Forces are the negative gradient of that energy [W4225405705#009]. SchNet likewise has atom-wise energy contributions [W2778051509#003]. SchNet's force predictions are energy-conserving [W2726670313#007].

The main difference is that NequIP uses E(3)-equivariant tensor features, while SchNet's filters are rotationally invariant [W4225405705#006][W2726670313#009].
- reference: Several design choices come from SchNet. The initial atom features are a trainable embedding of the atomic number (one-hot encoded). Atoms then pass through a stack of interaction blocks that do continuous convolutions over neighbors within a cutoff. In those convolutions the learnable filter weights are an MLP of the interatomic distance expanded in a radial basis: Gaussians in SchNet, Bessel functions with an envelope in NequIP. The output is per-atom energies summed to a total energy, and forces are its negative gradient. The difference is that NequIP also multiplies the radial part by spherical harmonics of the bond direction. If only l = 0 (scalar) features are kept, NequIP reduces to a SchNet-style invariant network.
- correctness: correct (The answer covers the key shared features from the reference: the one-hot atomic-number embedding, convolutions over interatomic distances with a radial MLP, per-atom energies summed to a total with forces as the negative gradient, and reduction to a SchNet-style network at l = 0. It also states the main difference, equivariant versus invariant features; the extra self-interaction detail is accurate, and the omitted Gaussian-versus-Bessel contrast is minor.)
- support: None (judge returned no valid verdict: )
- steps: search "NequIP architecture compared to SchNet" (5 passages, 5 new); search "SchNet continuous-filter convolution interatomic distances radial basis" (5 passages, 5 new); search "NequIP E(3)-equivariant convolutions radial basis embedding atom types interaction blocks, similar to SchNet" (5 passages, 5 new); answer

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: As its first step, NequIP embeds each atom. The initial feature comes from a trainable embedding that depends only on the atomic number Zi, given as a one-hot encoding. This follows SchNet and is implemented as a trainable self-interaction layer [W4225405705#009]. The embedding is followed by a series of interaction blocks and then an output block [W4225405705#009].
- reference: It embeds each atom's chemical species. The atomic number Z_i, one-hot encoded, goes through a trainable self-interaction (linear) layer. This gives the initial per-atom features, which are scalar (l = 0) only. The embedding follows SchNet. Higher-order tensor features first appear in the interaction blocks.
- correctness: correct (The answer captures the key facts: embedding each atom from one-hot atomic number via a trainable self-interaction layer, following SchNet; omitting the scalar-only detail is minor.)
- support: supported (The passage states that the embedding follows SchNet, is trainable, depends on atomic number Zi alone (one-hot), uses a trainable self-interaction layer, and is followed by interaction blocks and an output block.)

**q009** (lookup): What datasets is Nequip tested on?
- answer: In the original NequIP paper, it is tested on the following datasets [W4225405705]:

- **MD-17 (revised):** the aspirin molecule is used for data-efficiency learning curves. [W4225405705#037][W4225405705#020]
- **Liquid water and ices:** this is the 140,000-structure PBE0-TS AIMD/path-integral dataset. It has liquid water plus Ice Ih b, c and d. [W4225405705#024][W4225405705#015]
- **Water from Cheng et al.:** 1,593 revPBE0-D3 structures, used for data-efficiency experiments. [W4225405705#026]
- **Formate dehydrogenation on Cu(110):** 6,855 DFT structures, of which 2,500 were used for training. [W4225405705#024]
- **Li4P2O7 glass:** an ab-initio melt-quench MD dataset. [W4225405705#024][W4225405705#020]
- **LiPS:** 25,001 MD frames, with training sets of 10, 100, 1,000 and 2,500 frames. [W4225405705#026][W4225405705#020]

Other papers also use NequIP as a baseline or model on other data:

- **M3GNet dataset:** the GNoME paper trained NequIP on it. [W4389132751#033]
- **DPA-2 datasets:** the DPA-2 paper trained NequIP on its datasets, including OC2M, as a baseline. [W4405574099#057]
- reference: 1) MD-17 small organic molecules, both the original DFT version and the revised MD-17 (rMD17). 2) Small molecules at quantum-chemical accuracy: aspirin at CCSD; benzene, malonaldehyde, toluene and
   ethanol at CCSD(T).
3) Periodic systems:
   - liquid water and ice
   - a chemical reaction at a solid/gas interface (formate decomposition on a copper surface)
   - amorphous lithium phosphate (Li4P2O7)
   - a lithium superionic conductor (Li6.75P3S11, "LiPS")
- correctness: partial (The answer covers the periodic systems (water/ice, formate on Cu, Li4P2O7, LiPS) and MD-17 (aspirin only), but omits the original MD-17 DFT version, other rMD17 molecules, and the CCSD/CCSD(T) small-molecule benchmarks (aspirin CCSD; benzene, malonaldehyde, toluene, ethanol CCSD(T)).)
- support: None (judge returned no valid verdict: )
- steps: search "NequIP evaluated on datasets" (5 passages, 5 new); search "NequIP experiments MD-17, water and ices, formate on Cu, Li4P2O7, LiPS" (5 passages, 3 new); answer

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: On MD-17, the NequIP paper compares NequIP against a range of published leading machine-learning interatomic potentials. It benchmarks on both the original and the revised MD-17 data sets, with 1,000 training configurations [W4225405705#010]. The comparison models fall into these groups:
- **Invariant GNN potentials:** SchNet and DimeNet.
- **Shallow neural network:** ANI.
- **Kernel-based methods:** GAP, FCHL19/GPR and sGDML.
- **Other methods:** ACE, SpookyNet and GemNet.
- **Other equivariant networks:** PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are lmax = 1-only versions of equivariant networks.

[W4225405705#010]

The paper reports that NequIP outperforms all of these methods [W4225405705#011]. The results for ACE, GAP and ANI on the revised data set are those reported in an earlier work, cited as [43] in the paper [W4225405705#010].

The paper also compares NequIP with sGDML and GemNet on a separate set of molecules computed at the CCSD(T) level of theory [W4225405705#012]. That is a different benchmark from the MD-17 comparison above.
- reference: Invariant GNN potentials: SchNet and DimeNet. A shallow neural network: ANI. Kernel methods: GAP, FCHL19/GPR and sGDML. Other methods: ACE, SpookyNet and GemNet. Other equivariant networks: PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are restricted to l_max = 1. Results for ACE, GAP and ANI on revised MD-17 are taken from another paper (Kovács et al.), not retrained by the authors. NequIP reports the best accuracy of all of them.
- correctness: correct (The answer lists all the same model groups (SchNet, DimeNet, ANI, GAP, FCHL19/GPR, sGDML, ACE, SpookyNet, GemNet, PaiNN, NewtonNet, UNiTE), notes the lmax=1 restriction, that ACE/GAP/ANI revised results come from earlier work, and that NequIP is best.)
- support: None (judge returned no valid verdict: )
- steps: search "NequIP MD-17 comparison with other models (sGDML, DeepMD, DimeNet, SchNet, TensorMol)" (5 passages, 5 new); read_around "W4225405705#011" (3 passages, 2 new); answer

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet first computes the interatomic distance d_ij = ∥r_i − r_j∥. Using the distance makes the filters rotationally invariant [W2726670313#009].

It then expands that distance with radial basis functions, e_k(r_i − r_j) = exp(−γ∥d_ij − μ_k∥²). The centers μ_k lie between 0 Å and 30 Å, spaced every 0.1 Å, and γ = 10 Å [W2726670313#009]. This range is chosen so that it covers all distances in the data sets [W2726670313#009].

The expansion is used because, without it, the filters would be highly correlated. A neural network is close to linear at initialization, and the correlation would cause a plateau at the start of training. The added non-linearity makes the initial filters less correlated, so training is faster [W2726670313#009].

The expanded distances are then fed into two dense layers with softplus activations. These layers compute the filter weight W(r_i − r_j) [W2726670313#009].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: None (judge returned no valid verdict: )
- support: None (judge returned no valid verdict: Each claim in the answer matches the passage. The distance d_ij = ∥r_i − r_j∥ is given as the input to the filter network, and this is what makes the filters rotationally invariant. The radial basis e)

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses a shifted softplus, ssp(x) = ln(0.5e^x + 0.5), as the non-linearity throughout the network [W2726670313#010].

This matters for force fields for these reasons:
- SchNet predicts forces as the negative gradient of the predicted energy with respect to atom positions. This makes the force field energy-conserving by construction [W2726670313#010].
- The force loss is trained by gradient descent, so the model has to be at least twice differentiable [W2726670313#010].
- The shifted softplus has infinite order of continuity and gives a smooth potential energy surface [W2726670313#010].
- The shift makes ssp(0) = 0, which improves the network's convergence [W2726670313#010].
- The passages don't compare it with ReLU. For ReLU, the PhysNet paper notes that max(0, x) is not differentiable at x = 0, which causes problems when continuous derivatives of the output are needed [W2923693308#007].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (The answer gives the same shifted softplus formula, notes ssp(0)=0 improves convergence, and explains infinite differentiability yielding a smooth energy surface and the second-derivative needs for force training; it does not mention vibrational modes explicitly, but this is a minor omission.)
- support: None (judge returned no valid verdict: The SchNet claims all match the passage. The activation ssp(x) = ln(0.5e^x + 0.5) is used throughout the network. Forces are the negative gradient of the energy, which makes the force field energy-con)

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: SchNet can't use ordinary convolutional layers because they need a regular grid, and atoms aren't on one. Image pixels, video frames and audio samples sit on a regular grid, so a discrete filter tensor can be defined on that same grid. Atoms in a molecule are unevenly spaced and can sit at arbitrary positions, so a filter tensor doesn't apply [W2726670313#006][W2778051509#006].

You could resample the atoms onto a grid. But choosing an interpolation scheme is a challenge in its own right, and the grid may need many points [W2726670313#006]. A discrete filter also can't capture small positional changes of atoms, which gives discontinuous energy predictions [W2726670313#005].

SchNet instead uses continuous-filter convolutions. A filter-generating neural network maps atom positions to filter values [W2778051509#006].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (The answer states that atoms are at arbitrary positions rather than on a regular grid, so a fixed filter tensor doesn't apply, and that SchNet uses continuous-filter convolutions with a filter-generating network mapping positions to filter values, matching the reference.)
- support: supported (Every claim — the regular-grid requirement, the resampling and interpolation challenge, discontinuous predictions from discrete filters, and the filter-generating network — is stated in the cited passages.)

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of rcut = 5 Å when predicting formation energies for bulk crystals. The data were 69,640 structures from the Materials Project. Two examples were discarded because they would have contained isolated atoms at this cutoff [W2778051509#014].
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer gives the same 5 Å cutoff on Materials Project data and the same two structures dropped for isolated atoms; the extra 69,640 figure doesn't contradict the reference, and omitting the QM9/MD17 note is minor.)
- support: supported (The passage states the 5 Å cutoff, the 69,640 Materials Project structures, formation energy prediction for bulk crystals, and that two examples were discarded because they would include isolated atoms at this setting.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: SchNet predicts a scalar energy and gets the forces by differentiating that energy with respect to the atom positions: F_i = −∂E/∂r_i. This makes the force field energy-conserving by construction [W2726670313#010]. The paper credits Chmiela et al. for pointing this out.

Two further details come from the same passage:
- **Smoothness:** the model has to be at least twice differentiable so the force loss can be trained by gradient descent. SchNet uses a shifted softplus non-linearity throughout, which gives a smooth potential energy surface [W2726670313#010].
- **Symmetry:** because the energy prediction is rotationally invariant, the forces are rotationally equivariant by construction [W2726670313#010].

This holds even when the model is trained on forces alone. A later SchNet paper notes that using the derivative of an energy model as the force model still guarantees an energy-conserving force field [W2778051509#020].
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: correct (The answer states that forces are the negative gradient of the predicted energy with respect to positions, and that rotational invariance of the energy makes the forces equivariant, matching the reference; the extra details are consistent.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- The energy is differentiated with respect to atom positions to get forces, F_i = −∂E/∂r_i, which is energy-conserving by construction: supported by W272667)

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: SchNet's filters see only the distance to each neighbor. NequIP's filters see the full relative position vector, meaning both the distance and the direction.

**SchNet.** The filter-generating network takes the interatomic distance d_ij = ||r_i − r_j|| as input, which makes the filters rotationally invariant. The distance is first expanded in radial basis functions [W2726670313#009]. Each filter then emphasizes certain ranges of interatomic distance, so an interaction block updates an atom's representation according to its radial environment. Stacking three interaction blocks gives complex many-body representations, and they stay rotation invariant because the filters are radial [W2726670313#009]. The features are therefore scalar-valued invariants that carry no directional information about the neighbors.

**NequIP.** The filter is F(r_ij) = R(r_ij) Y_m^(l)(r̂_ij). It is a learnable radial function of the distance times spherical harmonics of the unit direction vector. All the learnable weights sit in the rotationally invariant radial function R, which is an MLP on a basis expansion of the distance. The spherical harmonics supply the angular dependence and make the filter equivariant [W4225405705#006]. Because the filters carry angular information, atom features are geometric tensors of rotation order l = 0, 1, 2, … and parity p. These are scalars, vectors and higher-order tensors, and the convolutions are equivariant instead of invariant [W4225405705#006]. The passage describes this as the core difference between NequIP and scalar-valued invariant GNN interatomic potentials [W4225405705#006].
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: correct (Matches the reference: SchNet filters see only distance (radial basis), giving invariant scalar features; NequIP filters include direction via spherical harmonics, giving equivariant geometric tensor features. The omitted scalar-only reduction is a minor detail.)
- support: None (judge returned no valid verdict: )
- steps: search "SchNet continuous-filter convolution filter-generating network interatomic distances" (5 passages, 5 new); search "NequIP equivariant convolution filters radial function spherical harmonics tensor product" (5 passages, 5 new); answer

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: SchNet was compared against GDML (gradient-domain machine learning), a kernel method. It was also compared against DTNN. The SchNet paper says GDML is accurate with 1,000 training examples but does not scale well with the number of atoms and training examples, so it could not be trained on 50,000 examples [W2726670313#014]. SchNet beat GDML on the more flexible molecules, malonaldehyde and ethanol. GDML reached much lower force errors on the remaining trajectories, all of which include aromatic rings [W2726670313#014].

The NequIP paper compared against sGDML and FCHL19/GPR, which are kernel methods, and reports that NequIP outperforms all other methods it tested. The authors call the consistent improvement over these two kernel methods "particularly surprising", because kernel methods typically do better than deep neural networks on small training sets [W4225405705#011]. They also note that the revised MD-17 data set is the one that should be used for comparing methods [W4225405705#011]. The passages I found do not give NequIP's numerical errors against these kernel methods.
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: correct (Identifies GDML as the kernel method SchNet compared against and notes GDML was stronger on most molecules, and states NequIP outperforms kernel methods sGDML and FCHL19; omits GAP but this is a minor gap and nothing contradicts the reference.)
- support: None (judge returned no valid verdict: )
- steps: search "SchNet MD17 comparison with kernel method (sGDML, GDML)" (5 passages, 5 new); search "NequIP MD17 compared to kernel methods sGDML accuracy" (5 passages, 2 new); answer

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: The SchNet paper says the decomposition into atomic contributions is a poor fit for the polarizability α and the electronic spatial extent ⟨R²⟩. SchNet's predictions for these two properties "fall noticeably short in terms of accuracy". The authors think this is "most likely due to the decomposition of the energy into atomic contributions which is not appropriate for these properties" [W2778051509#013][W2778051509#012].

By contrast, they say SchNet matches or improves on enn-s2s in 8 of 12 QM9 properties, where an atomic decomposition is a good choice [W2778051509#013]. enn-s2s is a model that learns a global representation with a set2set variant.

The passages I read don't mention the Behler-Parrinello potential, so this answers only the SchNet side of your question.
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: correct (The answer identifies polarizability α and electronic spatial extent ⟨R²⟩ as the poorly fitting properties and attributes this to the atom-wise decomposition, matching the reference; the extra detail about enn-s2s and the note about Behler-Parrinello do not contradict it.)
- support: None (judge returned no valid verdict: The answer's claims are mostly stated in the passages. The quotes about α and ⟨R²⟩ appear in both passages. The "8 out of 12 properties where a decomposition into atomic contributions is a good choice)

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: CHARMM36m was designed to fix CHARMM36's inaccurate polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins (IDPs). It is described as a refinement of CHARMM36 with improved accuracy for those ensembles [W2555870966#000]. The only passage I found from the CHARMM36m paper is its abstract, which doesn't give the specific cause of the inaccuracy.

A separate comparison study found a high population of left-handed α-helix in the CHARMM36 ensemble, which was inconsistent with measured scalar couplings [W2234602429#000]. That study doesn't say this was the motivation for CHARMM36m.
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (The answer correctly identifies inaccurate IDP backbone ensembles as the problem and mentions left-handed helix in CHARMM36, but it explicitly disclaims the link to CHARMM36m's motivation, omits overstabilized compact structures, and does not state that accuracy for folded proteins was kept.)
- support: None (judge returned no valid verdict: {"verdict":"supported","reason":"The CHARMM36m abstract says it refines CHARMM36 with improved backbone ensemble accuracy for IDPs, and the comparison abstract reports the left-handed α-helix populati)
- steps: search "CHARMM36m improved force field for folded and intrinsically disordered proteins" (5 passages, 5 new); search "CHARMM36 overly compact IDPs, salt bridges, left-handed helix; CHARMM36m refinement" (1 passage, 0 new); answer

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The collection has the CHARMM36m paper only as an abstract [W2555870966#000]. That abstract says CHARMM36m is a refinement of CHARMM36 with improved accuracy for polypeptide backbone conformational ensembles of intrinsically disordered peptides and proteins. It doesn't list which force-field terms were changed, such as CMAP, side-chain dihedrals or Lennard-Jones parameters. Other passages describe CHARMM36 itself [W2109154308#000], CHARMM36m-SBFIX [W4289550218#000] and the Drude-2019 force field [W3016074441#000]. None of them lists the CHARMM36 to CHARMM36m changes.
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (declined to answer although the corpus has the answer)
- steps: search "CHARMM36m modifications relative to CHARMM36 force field" (5 passages, 5 new); search "CHARMM36m refinement CMAP backbone, arginine lysine side chain Lennard-Jones, TIP3P modified" (1 passage, 0 new); search "CHARMM36m backbone CMAP changes and LJ pair-specific salt bridge" (5 passages, 3 new); open_paper "W2555870966" (1 section); search "CHARMM36m differs from CHARMM36 by backbone CMAP, side-chain dihedral, and Lennard-Jones parameters of arginine-carboxylate" (8 passages, 6 new); give_up

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: The collection has no passage that reports RFdiffusion's experimental success rate for binder design. [W4393118201#005] says only that Watson et al. repurposed RoseTTAFold to generate novel protein-binder backbones "with successful experimental validation". [W4391542588#028] cites the RFdiffusion paper in a reference list. Neither gives a hit rate or percentage.
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.
- steps: search "RFdiffusion binder design experimental success rate" (5 passages, 5 new); search "RFdiffusion de novo protein binders experimentally validated hit rate" (5 passages, 5 new); search "diffusion model protein design binders high success rate experimental characterization" (5 passages, 4 new); give_up

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: The passages that describe SchNet training don't mention a dropout rate. [W2726670313#012] gives Adam, batch size 32, learning rate 1e-3 with 0.96 decay every 100,000 steps, and an EMA of weights with decay 0.99. [W2778051509#011] and [W2778051509#017] give similar optimizer and loss settings. [W3159653252#028] gives Adam, learning rate 1e-4 and batch size 10. None of them state dropout.
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.
- steps: search "SchNet dropout rate training" (5 passages, 5 new); search "SchNet trained with dropout" (5 passages, 2 new); give_up

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: DiffTRe doesn't backpropagate through the simulation. It reweights a stored reference trajectory and differentiates through that reweighting instead.

**How it works.** DiffTRe generates a reference trajectory under reference potential parameters θ̂ and keeps only the subsampled, decorrelated states and their reference energies. For the current parameters θ, it computes each state's energy Uθ(Si) and weight wi. It then forms reweighted observables ⟨Ok(Uθ)⟩, and these give the loss. Reverse-mode AD runs only through this reweighting and the potential-energy evaluation, so the differentiation path doesn't depend on how the trajectory was generated [W3168247670#006][W3168247670#007]. Reweighting is reused until the effective sample size Neff drops below a threshold. After that, a new reference trajectory is sampled [W3168247670#007].

**What it buys:**
- **Stable gradients.** In the toy example, direct reverse-mode AD through the simulation suffered exploding gradients. Their magnitude grew exponentially with simulation length. DiffTRe gradients had constant magnitude regardless of length [W3168247670#011].
- **Speed.** Trajectories can be reused, and the backward pass only covers the decorrelated states. In the toy example the measured speed-ups were 486 for gradient computation and 3.7 per update overall. The authors' rule-of-thumb estimates gave 330 and 4 [W3168247670#011][W3168247670#012].
- **Low memory.** Only the subsampled states and their energies are stored, similar to the adjoint method [W3168247670#007]. Direct AD ran out of memory on the toy example, which limited trajectory lengths. It also prevented a speed-up measurement on the real-world cases [W3168247670#011].

**Limitations.** Reweighting makes DiffTRe invariant to the order of states in the trajectory, so dynamical properties can't be target observables [W3168247670#019]. Accuracy also depends on keeping Neff high, which means θ can't move far from θ̂ between new reference trajectories [W3168247670#006].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: correct (The answer captures that DiffTRe differentiates through reweighting rather than the simulation, avoids exploding gradients, gives roughly two orders of magnitude faster gradients (486 measured, 330 estimated), and has memory similar to the adjoint method; the extra details are consistent with the reference.)
- support: None (judge returned no valid verdict: )
- steps: search "DiffTRe differentiable trajectory reweighting versus backpropagating through MD simulation" (5 passages, 5 new); search "DiffTRe avoids exploding gradients, memory cost of differentiating through simulation, speedup" (5 passages, 4 new); answer

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: In DiffTRe, the weights are Boltzmann probability ratios between the current potential θ and the reference potential θ̂, normalized over the retained states. The kinetic energy cancels because it is the same in the numerator and the denominator.

Each weight is wi = [pθ(Si)/pθ̂(Si)] / Σj [pθ(Sj)/pθ̂(Sj)] [W3168247670#006]. In the canonical ensemble the state probabilities are Boltzmann, pθ(Si) ∼ exp(−βH(Si)). Here H is the Hamiltonian, the sum of potential and kinetic energy, and β = 1/(kB T) [W3168247670#006].

Inserting this into the ratio, the kinetic energy cancels. The weights then depend only on potential-energy differences [W3168247670#006]:

wi = exp(−β(Uθ(Si) − Uθ̂(Si))) / Σj exp(−β(Uθ(Sj) − Uθ̂(Sj)))

The passage does not spell out the cancellation. The reason is that the kinetic term is the same for a given state under both potentials, so it divides out.

When θ = θ̂, every weight is 1/N [W3168247670#006].
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (The answer gives the same normalized Boltzmann weight with only potential-energy differences, explains that the kinetic energy is identical under both potentials and cancels in the ratio, and notes that the weights are 1/N when θ equals the reference.)
- support: None (judge returned no valid verdict: )

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe stops reusing the old trajectory when the effective sample size Neff falls below a predefined threshold N̄eff. Until then it keeps cycling through reweighting, gradient computation and parameter updates on the stored states [W3168247670#007].

Once Neff < N̄eff, the statistical error from reweighting is no longer acceptably small. A new reference trajectory is then sampled, using the current θ as the new reference θ̂ [W3168247670#007]. It starts from the last sampled state S_N of the old trajectory [W3168247670#006].

Neff starts at N, so each reference trajectory gets at least one θ update [W3168247670#007].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (The answer matches the reference: a new trajectory is simulated when N_eff falls below a threshold, using current parameters and starting from the last state of the old trajectory; the omitted exponential-entropy formula is a minor detail.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

1. The criterion of Neff falling below N̄eff, with the loop of reweighting, gradient computation and updates, is stated in #007 and #006. The phrase "on the )

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The DiffTRe diamond potential, a DimeNet++ model, was trained only on the experimental elastic stiffness tensor of diamond. That tensor has three distinct moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa [W3168247670#013]. The loss also required the crystal to be stress-free (σ = 0) at zero strain [W3168247670#013]. The simulations used the experimental density (3512 kg/m3) and temperature (298.15 K) as simulation conditions [W3168247670#013]. Density functional theory data was used only afterwards, to compare the stress-strain curve, and not for training [W3168247670#014].
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer matches the reference on the experimental elastic stiffness tensor (C11=1079, C12=124, C44=578 GPa) and the stress-free condition at zero strain; the extra details about density, temperature and DFT are not contradicted by the reference.)
- support: None (judge returned no valid verdict: {"verdict": ")

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: The held-out property DiffTRe's coarse-grained water model got wrong was the self-diffusion coefficient D. The learned model predicted D = 10.91 μm²/ms, against an experimental value of 2.2 μm²/ms [W3168247670#017]. The other held-out property, the tetrahedral order parameter q, matched well: about 0.569 against 0.576 experimentally [W3168247670#017].

The paper attributes the error to the coarse-graining itself. CG models have smoother potential energy surfaces, so their dynamics run faster than those of atomistic models [W3168247670#017]. For CG water, diffusion coefficients also fall as the number of interaction sites rises [W3168247670#017]. A tabulated single-site potential built by iterative Boltzmann inversion with pressure correction gave an even larger D of 14.15 μm²/ms [W3168247670#017].

The authors suggest that D decreased during optimization because the potential began by acting like a single-site model. As it learned 3-body interactions, it became more like multi-site CG models [W3168247670#017]. DiffTRe also cannot use dynamical properties as training targets, because its reweighting scheme ignores the order of states in the trajectory [W3168247670#019].
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (The answer identifies the self-diffusion coefficient (10.91 vs 2.2 μm²/ms) as wrong, attributes it to smoother potential energy surfaces in CG models speeding dynamics, and notes the tetrahedral order parameter matched; extra details do not contradict the reference.)
- support: supported (Every claim in the answer, including the D and q values, the smoother-PES and multi-site explanations, the IBI value of 14.15, and the reweighting limitation, is stated in the cited passages #017 and #019.)

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: Not directly. DiffTRe can't use a diffusion coefficient as a fitting target, because the paper says dynamical properties can't be target observables. The reweighting scheme doesn't depend on the order of states in the trajectory, so it can't handle observables that depend on time ordering [W3168247670#019]. The method is aimed at time-independent observables [W3168247670#001][W3168247670#003].

The authors did compute the self-diffusion coefficient D for their coarse-grained water model, but only as a held-out check, not as a training target. The model predicted D = 10.91 μm2/ms against an experimental 2.2 μm2/ms [W3168247670#017]. So fitting to a measured D would need a different approach, such as differentiating through the simulation.
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: correct (The answer states that DiffTRe cannot target diffusion coefficients because reweighting ignores the temporal order of states, so only time-independent observables work, matching the reference; the extra detail about held-out D evaluation is consistent.)
- support: None (judge returned no valid verdict: Checking claims: (1) DiffTRe can't use diffusion coefficient as target because dynamical properties can't be target observables — supported by #019. (2) Reweighting is invariant to sequence of states )
- steps: search "DiffTRe differentiable trajectory reweighting diffusion coefficient" (5 passages, 5 new); search "time-dependent observables dynamical properties limitation DiffTRe future work" (5 passages, 5 new); answer

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: The DiffTRe paper never mentions SchNet's C20 model in the passages I found. The answer below comes from its general critique of bottom-up training on DFT data.

**Main limitation:** The authors say bottom-up training limits a model's accuracy to the quality of the data-generating simulation, which is usually DFT on small molecules in vacuum [W3168247670#002]. State-of-the-art NN potentials already reach the DFT accuracy limit within the data distribution. Any remaining deviation from experiment is therefore due to DFT uncertainty, and DFT is sensitive to the functional used [W3168247670#002]. More precise methods such as CCSD(T) cost far more. For macromolecules, quantum mechanics calculations will stay intractable for the foreseeable future [W3168247670#002]. The authors conclude that the main obstacle is the limited availability of highly precise and sufficiently broad data sets [W3168247670#003].

**What they train on instead:** DiffTRe is a top-down approach that learns NN potentials directly from experimental data. Its examples use the diamond stiffness tensor for an atomistic model, and pressure plus radial and angular distribution functions for a coarse-grained water model [W3168247670#004][W3168247670#001]. It does this by reweighting trajectories, which avoids backpropagating through the MD simulation [W3168247670#001].
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: correct (The answer states the same key points as the reference: bottom-up DFT training is limited by the accuracy of the reference method and by the availability of precise, broad data sets, and DiffTRe trains top-down on experimental observables. The extra detail it adds is consistent with the reference.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- The opening caveat about SchNet's C20 model is a statement about the search, not a claim that needs support.
- Bottom-up training limits accuracy to the qu)
- steps: search "DiffTRe differentiable trajectory reweighting limitation of training on DFT data, train on experimental data" (5 passages, 5 new); search "bottom-up NN potentials trained on DFT, SchNet C20, accuracy limited by reference quantum data" (5 passages, 4 new); answer

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: The potential is the Stillinger-Weber potential, which DiffTRe's diamond model uses in its original form parametrized for silicon. DiffTRe takes it as the prior potential, Uprior, and rescales its length and energy scales for carbon atoms [W3168247670#013].

The neural network potential paper that used silicon as its test system is "Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces" (2007). It builds an NN-based many-body potential for bulk silicon [W2025444507#001]. The passages I read don't name any other neural network potential paper that tests on silicon, apart from the JAX, M.D. paper (2019), which fits Behler-Parrinello and graph network potentials to silicon DFT data as one of three examples [W2991697224#016]. The 2007 paper fits the question best because silicon is its main test system.
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: correct (It identifies the Stillinger-Weber potential parametrized for silicon and rescaled for carbon, and names the 2007 Behler-Parrinello paper (bulk silicon) as the NN potential paper, matching the reference.)
- support: None (judge returned no valid verdict: )
- steps: search "DiffTRe diamond model empirical potential" (5 passages, 5 new); search "neural network potential test system silicon" (5 passages, 5 new); answer

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: DiffTRe uses DimeNet++ as its graph neural network potential in the diamond and coarse-grained water examples. The paper describes the model as "a graph neural network operating iteratively on the atomic graph defined by D" (the pairwise distance matrix) [W3168247670#007]. The paper calls DimeNet++ a "state-of-the-art graph neural network potential" [W3168247670#004]. DimeNet++ is built on DimeNet, which the NequIP paper counts among invariant GNN potentials.

On MD-17, NequIP "significantly outperforms invariant GNN-IPs (such as SchNet and DimeNet)". It also outperforms shallow neural networks, such as ANI, and kernel methods such as GAP, FCHL19/GPR and sGDML [W4225405705#010]. The paper reports that NequIP outperforms all the other methods it compares against, including other equivariant networks such as PaiNN and NewtonNet [W4225405705#010][W4225405705#011].

The NequIP paper's convergence scan over rotation order l gives a clear improvement from l = 0 to l = 1. Increasing the order beyond l = 1 gives a further consistent improvement. The authors say this shows the "crucial role of equivariance" for accuracy on this task [W4225405705#011].

The passages I found do not compare NequIP with DimeNet++ directly. The comparison is with DimeNet, the model DimeNet++ is built on.
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: correct (The answer identifies DimeNet++ for diamond and coarse-grained water and states that NequIP significantly outperforms invariant GNN potentials such as SchNet and DimeNet on MD-17, matching the reference; the extra details do not contradict it.)
- support: None (judge returned no valid verdict: )
- steps: search "DiffTRe differentiable trajectory reweighting graph neural network potential" (5 passages, 5 new); search "NequIP MD-17 comparison with other graph neural network potentials accuracy" (5 passages, 5 new); answer

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: In DiffTRe, the prior potential U_prior is not a Bayesian prior. It does not put a lasting bias on the learnable parameters in the small-data regime. If U_prior contradicts the data, the learned model potential U_model corrects for it during optimization [W3168247670#008].

The paper gives it three roles:
- **Trajectory generation:** U_prior controls how trajectories are generated at the start of the optimization [W3168247670#008]. This also affects how much information the gradient carries. A well-chosen prior should give trajectories close to those from the true potential [W3168247670#010].
- **Easier learning problem:** U_prior turns the task into learning the difference between the prior and the optimal potential, instead of learning the potential directly. A well-chosen prior is therefore a physics-informed initialization that speeds up convergence [W3168247670#008].
- **Encoded prior knowledge:** U_prior is a constant potential that approximates known properties of the system, such as the Pauli exclusion principle [W3168247670#008]. In the double-well example, the learned potential only has to adapt a single-well prior instead of building large energy barriers from scratch [W3168247670#010].

The authors also list the need for a reasonably chosen prior as a limitation of the test cases. They suggest a pre-trained model could remove that need [W3168247670#019][W3168247670#020].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: correct (The answer covers the key points: it is not a Bayesian prior, controls trajectory generation and gradient information early on, acts as a physics-informed starting point so the network learns a correction, and is overridden by the data if it contradicts it.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- Not Bayesian, no pervasive bias, and U_model corrects if U_prior contradicts the data: supported by #008.
- Trajectory generation at the start of optimizat)

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The available DiffTRe passages don't give a total GPU-hour figure for training the diamond potential. They describe the diamond setup: a DimeNet++ potential trained on the experimental stiffness tensor, with 700 or so update steps shown in Fig. 3 [W3168247670#013][W3168247670#014]. They say wall-clock time per update is plotted in Supplementary Fig. 5a, but no total training time or GPU hours appears in the text I could access [W3168247670#014]. The only timing numbers given are for the double-well toy example, an average of 39.2 s and 2.76 s per update [W3168247670#009].
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.
- steps: search "DiffTRe diamond potential training GPU hours" (5 passages, 5 new); search "diamond DimeNet++ training time hours GPU stiffness tensor" (5 passages, 4 new); search "wall-clock time per update, total training time on GPU, hours" (5 passages, 4 new); search "computations performed on NVIDIA GPU; training took hours; compute cost of diamond and water models" (5 passages, 1 new); search "DiffTRe diamond training required GPU hours total" (10 passages, 7 new); search "Supplementary Fig. 5 time per update diamond DimeNet++ total training time approximately hours single GPU" (8 passages, 1 new); give_up

