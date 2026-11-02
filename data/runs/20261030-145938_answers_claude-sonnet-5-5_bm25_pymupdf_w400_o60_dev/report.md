# Answer eval: claude-sonnet-5-5

- **Generator:** `{"name": "claude", "provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "answer-v2"}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1", "max_tokens": 1500}`
- **Retrieval:** bm25, top 5 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 9e6de1d92dea)
- **Cost:** generator $0.353, judge $0.203

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.60 [0.45, 0.76] | 29 |
| Supported by its citations | 0.98 [0.93, 1.00] | 21 |
| Cites your evidence | 0.75 [0.55, 0.90] | 20 |
| Evidence was retrieved | 0.67 [0.48, 0.85] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 21 |
| Declines when unanswerable | 1.00 [1.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.28 [0.14, 0.45] | 29 |

Correct when the evidence was retrieved: 0.78 (n=18)

Correct when no evidence was retrieved: 0.33 (n=9)

## Effort per question (mean)

1.0 model calls, 1.0 tool calls (1.0 searches), 5.0 passages read, 4,062 input tokens, $0.0110 per question, 3.1 s. Gave up on 0%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: The passages do not say what test system Behler and Parrinello used in their original demonstration. They describe the Behler-Parrinello approach: the total energy is decomposed into atomic contributions, each predicted from local atom-centered descriptors [W4312043350#015][W2988055229#031]. They also cover later uses of it, such as JAX MD training a Behler-Parrinello network on DFT data for 64-atom silicon configurations [W2991697224#016]. That silicon example is JAX MD's own demonstration, not the original paper's test system.
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: The original Behler–Parrinello cutoff function is a piece-wise cosine: fc(Rij) = 0.5 [cos(π Rij / Rc) + 1] for Rij ≤ Rc, and 0 for Rij > Rc [W2025444507#004]. It gives zero value and slope at separations beyond Rc [W2025444507#004]. The ANI-1 paper writes the same form as 0.5 × cos(π Rij / RC) + 0.5 for Rij ≤ RC [W2541404351#007]. The Behler–Parrinello formula in the passage is garbled by text extraction, so the π and the exact bracket placement come from reading it alongside the ANI-1 version.
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: correct (The answer gives the same cosine cutoff, 0.5[cos(πR/Rc)+1] for R ≤ Rc and 0 beyond, matching the reference; the extra remarks about the ANI-1 form and text extraction do not contradict it.)
- support: supported (Each claim matches the passages: the cosine cutoff form with 0.5 and cos terms for Rij ≤ Rc and 0 beyond, zero value and slope beyond Rc, the ANI-1 form, and the note that the BP formula is garbled (π missing and brackets unclear).)

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: In a high-dimensional neural network potential, the total energy E is the sum of atomic contributions, E = sum_i Ei, as in empirical potentials [W2025444507#003]. Each Ei is the output of an atomic (sub)network that takes the symmetry-function description of atom i's local environment as input [W2025444507#003][W2541404351#007]. In the original formulation the subnets have identical structure and weights, which keeps the total energy invariant when two atoms are interchanged [W2025444507#003]. In the ANI model, atomic-number-specific NNPs produce the Ei, which are summed to give the total energy ET [W2541404351#007]. In general, Ei can come from one or several NNs, for example one per element [W4312043350#015].
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states that total energy is the sum of atomic energies, each output by an atomic neural network from the local environment (symmetry functions), matching the reference; the cutoff is only implicit but this is a minor omission.)
- support: supported (Every claim is directly stated in the cited passages (sum of atomic contributions, symmetry-function inputs, identical subnets for interchange invariance, ANI atomic-number-specific NNPs, one or multiple NNs per element).)

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP's internal features are equivariant under the 3D Euclidean group E(3) (rotation, inversion and translation). It is described as an equivariant neural network, and such networks use only E(3)-equivariant operations, so they can act directly on non-invariant geometric inputs such as displacement vectors [W4319162181#003]. The passages do not describe NequIP's specific construction (e.g., its layers or tensor products). They only give the general recipe for equivariant features: each feature transforms under the irreducible representations of the symmetry group, so m_L(Q·r) = D_L(Q) m_L(r) for all Q in O(3) [W4406405186#025][W4406405186#002]. Translation invariance is ensured by using interatomic displacement vectors [W4406405186#025].
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: partial (It correctly names E(3) and mentions features transforming under irreps of O(3), but it explicitly says it does not describe NequIP's construction and omits the tensor products with spherical harmonics of relative position vectors.)
- support: supported (Each claim matches the cited passages: equivariant networks use only E(3)-equivariant operations and can act on displacement vectors, NequIP is presented as an equivariant model, the O(3) equivariance equation is given, and translation invariance comes from using displacement vectors.)

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: The passages describe how Behler-Parrinello networks handle rotational symmetry, but none of them mention NequIP, so the comparison cannot be made from them. Behler-Parrinello maps the coordinates of each atom's neighbors (distances and angles) to roto-translationally invariant symmetry-function features, and the energy computed from those features is therefore invariant [W2988055229#031]. These symmetry functions are rotation-invariant and contain no directional information, so forces must be obtained by differentiating the energy [W2976347420#003]. The symmetry functions are also described as hand-crafted or largely ad hoc [W2963373387#003][W2742127985#002].
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: answerable: true

answer: The passages support only a partial answer, and they give no NequIP-specific architectural details. They say that SchNet and NequIP are both graph neural network (GNN) MLIPs that use implicit AEFs, meaning learned features or embeddings of atoms and bonds rather than hand-crafted descriptors [W4407925765#013]. They also say that both can be treated as GNN-IP models with two-body message-passing functions over edges within a cutoff radius rc [W4391631778#024]. The difference is that NequIP is equivariant, while SchNet is invariant [W4391631778#024]. The passages do not describe other shared components, such as filters, interaction blocks, or radial basis expansions.
- reference: Several design choices come from SchNet. The initial atom features are a trainable embedding of the atomic number (one-hot encoded). Atoms then pass through a stack of interaction blocks that do continuous convolutions over neighbors within a cutoff. In those convolutions the learnable filter weights are an MLP of the interatomic distance expanded in a radial basis: Gaussians in SchNet, Bessel functions with an envelope in NequIP. The output is per-atom energies summed to a total energy, and forces are its negative gradient. The difference is that NequIP also multiplies the radial part by spherical harmonics of the bond direction. If only l = 0 (scalar) features are kept, NequIP reduces to a SchNet-style invariant network.
- correctness: partial (The answer correctly identifies shared learned atom embeddings, message passing over neighbors within a cutoff, and the equivariant vs. invariant difference, but it omits the radial-basis MLP filters, per-atom energies summed with forces as gradients, and the l=0 reduction, and it explicitly says these are not covered.)
- support: supported (Each claim traces to the cited passages: both models are implicit-AEF GNNs (learned rather than handcrafted features), both fit the two-body message-passing GNN-IP framework within rc, and NequIP is equivariant while SchNet is not. Calling SchNet 'invariant' is a small inference, but it follows from the passage.)

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: Only partly. The simplified NequIP architecture in Figure 2a appears to list an Embedding step first, followed by three interaction blocks and an output block. The forward path starts from atomic numbers and atomic positions and computes the energy [W4391631778#007]. The passages do not describe what the embedding step computes. They only say that edge features derived from atomic positions are inputs to the message function in the convolution block [W4391631778#007].
- reference: It embeds each atom's chemical species. The atomic number Z_i, one-hot encoded, goes through a trainable self-interaction (linear) layer. This gives the initial per-atom features, which are scalar (l = 0) only. The embedding follows SchNet. Higher-order tensor features first appear in the interaction blocks.
- correctness: partial (It correctly identifies embedding as the first step starting from atomic numbers, but it explicitly says it cannot describe what the embedding computes, missing the one-hot encoding, linear self-interaction layer, and scalar-only features.)
- support: supported (All claims (figure block order, forward path from atomic numbers/positions to energy, no description of embedding computation, edge features as message function inputs) match the cited passage.)

**q009** (lookup): What datasets is Nequip tested on?
- answer: The passages describe NequIP being run on several datasets, but they give no complete list.

- **DPA-2 pre-training datasets:** NequIP was trained single-task on these datasets and compared with GemNet-OC, EquiformerV2, Allegro, MACE and DPA-2 [W4405574099#044]. OC2M is named explicitly. Because of memory limits, NequIP was trained on four random subsets of OC2M in sequence [W4405574099#057].
- **MD17:** NequIP is cited as a neural-network force field with reported parameter counts on the MD17 datasets, using 1k and 10k training points [W4315631504#032].
- **MPtrj (indirect):** SevenNet, which is based on the NequIP architecture, was fitted to the MPtrj data [W4416191329#019]. This is a derived model rather than NequIP itself.

The other datasets in the DPA-2 pre-training set are not named in these passages.

{"answerable": true, "answer": "Partial answer. In DPA-2, NequIP was trained single-task on the DPA-2 pre-training datasets and compared with GemNet-OC, EquiformerV2, Allegro, MACE and DPA-2 [W4405574099#044]
- reference: 1) MD-17 small organic molecules, both the original DFT version and the revised MD-17 (rMD17). 2) Small molecules at quantum-chemical accuracy: aspirin at CCSD; benzene, malonaldehyde, toluene and
   ethanol at CCSD(T).
3) Periodic systems:
   - liquid water and ice
   - a chemical reaction at a solid/gas interface (formate decomposition on a copper surface)
   - amorphous lithium phosphate (Li4P2O7)
   - a lithium superionic conductor (Li6.75P3S11, "LiPS")
- correctness: partial (The answer correctly names MD17 but omits rMD17, the CCSD/CCSD(T) molecules and all the periodic systems (water, formate/Cu, Li4P2O7, LiPS), and instead lists DPA-2/OC2M and MPtrj datasets that are not in the reference.)
- support: partial (Most claims are supported (NequIP single-task comparison, OC2M split into four subsets, MD17 parameter counts, SevenNet built on NequIP and fitted to MPtrj), but the closing claim that other DPA-2 pre-training datasets are not named is not supported: [W4405574099#057] also names the Sn and Drug datasets, and [W4405574099#044] names ANI-1x.)

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: NequIP is benchmarked on both original and revised MD-17 against published leading MLIPs. It significantly outperforms invariant GNN-IPs (SchNet, DimeNet), shallow neural networks (ANI), and kernel-based methods (GAP, FCHL19/GPR, sGDML) [W4225405705#010]. It is also compared to ACE, SpookyNet, GemNet, and other equivariant networks (PaiNN, NewtonNet, UNiTE) [W4225405705#010]. The paper reports that NequIP outperforms all of these methods [W4225405705#011].
- reference: Invariant GNN potentials: SchNet and DimeNet. A shallow neural network: ANI. Kernel methods: GAP, FCHL19/GPR and sGDML. Other methods: ACE, SpookyNet and GemNet. Other equivariant networks: PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are restricted to l_max = 1. Results for ACE, GAP and ANI on revised MD-17 are taken from another paper (Kovács et al.), not retrained by the authors. NequIP reports the best accuracy of all of them.
- correctness: correct (The answer lists all the reference's compared models (SchNet, DimeNet, ANI, GAP, FCHL19/GPR, sGDML, ACE, SpookyNet, GemNet, PaiNN, NewtonNet, UNiTE) and says NequIP outperforms them; it omits only minor details such as the l_max=1 note and the source of ACE/GAP/ANI results.)
- support: supported (All claims, including benchmarking on both datasets, the named comparison groups, and the overall claim that NequIP outperforms all other methods, appear in the cited passages.)

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet first computes the interatomic distance dij = ∥ri − rj∥, which makes the filter rotationally invariant [W2726670313#009]. It then expands this distance in radial basis functions ek(ri − rj) = exp(−γ∥dij − μk∥²), with centers 0 Å ≤ μk ≤ 30 Å every 0.1 Å and γ = 10 Å [W2726670313#009]. The expansion adds non-linearity, so the initial filters are less correlated and training is faster [W2726670313#009]. The expanded distances are then fed into two dense layers with softplus activations, which compute the filter weight W(ri − rj) [W2726670313#009].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: partial (The Gaussian expansion on a uniform grid of centers and the decorrelation benefit match the reference, but the answer gives γ = 10 Å and a 30 Å grid extent, while the reference says γ and the spacing are both 0.1 Å.)
- support: supported (Every claim (distance-based rotational invariance, RBF expansion with stated centers and γ, less correlated filters and faster training, two dense softplus layers computing W) is stated in the passage.)

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses a shifted softplus, ssp(x) = ln(0.5e^x + 0.5), as the activation function throughout the network [W2726670313#010][W2778051509#006]. The shift makes ssp(0) = 0 and improves convergence, and the function has infinite order of continuity [W2778051509#006]. This matters for force fields because forces are obtained by differentiating the energy with respect to atom positions, so the model must be at least twice differentiable to allow gradient descent on the force loss [W2726670313#010]. The smooth activation gives smooth potential energy surfaces, force fields and second derivatives, which are needed for training with forces and for calculating vibrational modes [W2778051509#006]. More generally, activation functions such as ReLU are excluded for neural network potentials because activations must be smooth to avoid discontinuities in the forces [W3093149769#039].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (The answer states the shifted softplus with the same formula, notes ssp(0)=0 and better convergence, and explains that infinite differentiability gives smooth energy surfaces, forces and second derivatives for force training and vibrational modes, matching the reference.)
- support: supported (Every claim, including the ssp definition, shift benefits, infinite continuity, twice-differentiability, vibrational modes, and the ReLU exclusion, is stated in the cited passages.)

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: Ordinary convolutional layers use a filter tensor defined on a regular grid, as with image pixels, audio or video frames. Atoms sit at arbitrary positions rather than on a grid, so such a filter tensor is not applicable [W2778051509#006][W2726670313#006]. SchNet therefore uses continuous-filter convolutions (cfconv), in which a filter-generating neural network maps atom positions to filter values [W2778051509#006][W2726670313#006]. Re-sampling onto a grid is a possible workaround, but choosing an interpolation scheme is a challenge and may require many grid points [W2726670313#006].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (The answer states that atoms are at arbitrary positions rather than on a regular grid, so fixed filter tensors don't apply, and that SchNet uses continuous-filter convolutions with a filter-generating network; the extra detail about grid resampling is consistent.)
- support: supported (Every claim is stated in the cited passages: regular-grid filter tensors, atoms at arbitrary positions, cfconv with a filter-generating network mapping positions to filter values, and the re-sampling workaround with its interpolation and grid-point drawbacks.)

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of rcut = 5 Å for the Materials Project formation-energy task. Two examples that would have contained isolated atoms with this cutoff were discarded from the data set [W2778051509#014].
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer gives the 5 Å cutoff on Materials Project and notes that two structures with isolated atoms were discarded, matching the reference; it omits only the QM9/MD17 no-cutoff aside.)
- support: supported (The passage states that rcut = 5 Å was set and that two examples that would include isolated atoms with this setting were discarded from the data set.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: The passages do not say how SchNet ensures its predicted forces conserve energy. They only say that SchNet was trained and evaluated on energies and forces for MD17 and ISO17, with and without force information in training [W2726670313#014][W2726670313#015]. They also note that MD17 was introduced for predicting energy-conserving force fields with GDML [W2726670313#014]. Separately, another paper says that forces not obtained as gradients of the total potential energy are not guaranteed to conserve energy [W4225405705#004], but the passages never state that SchNet derives its forces this way.
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: SchNet's filters see only the interatomic distance to each neighbor. They are radial convolution filters, which makes the features rotation invariant [W3093149769#042]. Other work likewise says SchNet uses only pairwise distances [W2788775653#008]. NequIP's filters see the full relative position vector. Each filter is a learnable radial function R(r_ij) times spherical harmonics of the unit vector, F(r_ij) = R(r_ij)Y(l)_m(r_ij hat), so they also see direction [W4225405705#006]. NequIP's features are therefore geometric tensors (scalars, vectors and higher-order tensors) that transform equivariantly under rotation and parity, not just invariant scalars [W4225405705#006]. Keeping only the 0 ⊗ 0 → 0 interaction reduces NequIP to a conventional invariant GNN over scalar features, similar to SchNet [W4225405705#008].
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: correct (The answer matches the reference on every key point: SchNet filters see only distances and give invariant scalar features, NequIP filters also use direction via spherical harmonics and give equivariant geometric tensors, and restricting to scalars reduces NequIP to a SchNet-like invariant network.)
- support: supported (Each claim matches the cited passages: SchNet's radial filters and pairwise-distance use, NequIP's R(r)·Y filter form with direction dependence, equivariant geometric tensor features, and the 0⊗0→0 reduction to a SchNet-like invariant GNN.)

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: Partly. The passages do not say which kernel method the SchNet paper compared against on MD17. One passage mentions GDML and sGDML only in the context of the FCHL paper's own comparisons, not the SchNet paper's [W3003486042#028].

On NequIP, the NequIP paper reports that it significantly outperforms kernel-based approaches such as GAP, FCHL19/GPR and sGDML on MD-17. It also outperforms invariant GNN-IPs such as SchNet and DimeNet, and shallow neural networks such as ANI [W4225405705#010].
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: partial (The NequIP part matches the reference (outperforms GAP, FCHL19, sGDML), but the answer declines to identify GDML as the kernel method SchNet compared against, which is a key fact in the reference.)
- support: supported (The FCHL passage only mentions GDML/sGDML in the FCHL paper's own comparisons, and the NequIP passage states the outperformance of GAP, FCHL19/GPR, sGDML, SchNet, DimeNet and ANI on MD-17.)

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: None of the passages is from the SchNet paper, so they cannot say which properties SchNet considers a poor fit for atomic-contribution models. The passages describe the Behler-Parrinello approach: total energy is a sum of atomic contributions E = sum_i E_i, which gives permutation invariance and lets the model handle varying system sizes [W3093149769#038][W2988055229#031]. One passage notes that transferability across system sizes needs sufficient sampling of local environments and corrections for long-range effects [W3093149769#038]. SchNet appears only in a list of MLIP names [W4407925765#005].
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: The passages only partly answer this. CHARMM36m is a refinement of CHARMM36 that gives improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. This suggests CHARMM36 was less accurate for those ensembles, but the passages do not describe the specific deficiency (for example, how the ensembles were wrong) or how it was corrected.
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (It correctly says CHARMM36m improved backbone ensembles for intrinsically disordered proteins, but it omits the specific problem (overstabilized compact and left-handed helical structures) and does not mention that folded-protein accuracy was kept.)
- support: supported (The passage states that CHARMM36m refines CHARMM36 with improved accuracy for backbone conformational ensembles of intrinsically disordered peptides and proteins; the inference that CHARMM36 was less accurate follows, and the answer correctly notes the passage gives no specifics.)

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The passages do not say which force field terms were changed from CHARMM36 to CHARMM36m. The CHARMM36m abstract describes it only as a refinement of CHARMM36 with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. The other passages cover different topics. One describes CHARMM36 versus CHARMM22/CMAP [W2109154308#000]. Another describes a later salt-bridge modification, CHARMM36m-SBFIX, built on CHARMM36m [W4289550218#000].
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: The passages do not mention RFdiffusion or the experimental success rate of designing protein binders with it. The related passages cover other topics: PeSTo's interface-prediction recovery rates [W4366279959#006], DynamicBind's docking success rates [W4391542588#005], and success rates of alternative-conformation prediction methods for membrane transporters [W4393559298#028].
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: The passages do not give a dropout rate for SchNet. The SchNet passage lists its training setup: ADAM optimizer, 32 molecules per mini-batch, initial learning rate 10^-3 with exponential decay of 0.96 every 100,000 steps, and an exponential moving average over weights with decay 0.99 [W2726670313#012]. Dropout is not mentioned there. The other passages mention dropout only for other models or in general, not for SchNet.
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: DiffTRe does not differentiate through the MD simulation for time-independent observables. It combines automatic differentiation with MD reweighting schemes based on thermodynamic perturbation theory [W3168247670#001][W3168247670#003]. Direct AD backpropagates through the whole trajectory generation, whereas DiffTRe only differentiates through the potential energy computation of decorrelated states [W3168247670#011]. What this buys it:
- No exploding gradients. DiffTRe gradients keep constant magnitude regardless of simulation length, while direct AD gradients grow exponentially with it [W3168247670#011][W3168247670#003].
- Speed. Gradient computation is about 2 orders of magnitude faster [W3168247670#003]. In the toy example the measured speed-up was 486 for gradient computation and 3.7 overall per update when a new reference trajectory is sampled, though these values depend on the setup [W3168247670#011].
- Memory. Requirements are comparable to the adjoint method, and direct reverse-mode AD is typically intractable beyond about a hundred particles and a few hundred time steps [W3168247670#003].
- Reuse of trajectories. Previously generated trajectories can be re-used, which cuts wall-clock time per parameter update [W3168247670#011].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: correct (The answer matches all key points of the reference: it avoids differentiating through the simulation, uses AD with reweighting, avoids exploding gradients, gives ~2 orders of magnitude faster gradients, and has memory comparable to the adjoint method; extra details are consistent.)
- support: supported (Every claim, including the speed-up numbers, memory comparison, exploding gradients and trajectory reuse, is stated in the cited passages.)

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: Each retained state S_i from the reference trajectory (generated with reference potential parameters θ̂) gets a weight equal to the ratio of its state probabilities under the current potential θ and the reference potential, normalized over all states: w_i = [p_θ(S_i)/p_θ̂(S_i)] / sum_j [p_θ(S_j)/p_θ̂(S_j)] [W3168247670#005]. In the canonical ensemble the probabilities are Boltzmann, p_θ(S_i) ~ exp(−βH(S_i)), where H is the sum of potential and kinetic energy, and β = 1/(kB T) [W3168247670#005]. The kinetic energy cancels in the ratio, so w_i = exp(−β(U_θ(S_i) − U_θ̂(S_i))) / sum_j exp(−β(U_θ(S_j) − U_θ̂(S_j))) [W3168247670#005]. For θ = θ̂, this gives w_i = 1/N [W3168247670#005].
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (The answer gives the same normalized Boltzmann-ratio weights with only potential energy, explains that the kinetic energy cancels in the ratio, and notes w_i = 1/N when θ = θ̂.)
- support: supported (Each claim (weight formula, Boltzmann probabilities with H as potential plus kinetic energy, β=1/(kBT), kinetic energy cancelling, and w_i=1/N for θ=θ̂) is stated in the cited passage's Eqs. 3-4 and surrounding text.)

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe keeps reweighting the saved reference trajectory, computing a gradient and updating θ each time, for as long as the statistical error from reweighting is acceptably small, meaning Neff is larger than a predefined N̄eff. As soon as Neff < N̄eff, it samples a new reference trajectory using the current θ as the new ˆθ [W3168247670#007]. At least one θ update per trajectory is guaranteed because initially Neff = N [W3168247670#007].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (The answer states that a new trajectory is sampled with the current parameters once Neff falls below a threshold, matching the reference. It omits the exact Neff formula and the restart from the last state, but its other claims do not contradict the reference.)
- support: supported (Every claim in the answer matches the cited passage, including the reweighting loop, the Neff threshold, resampling with the current θ as the new ˆθ, and the one-update guarantee from initial Neff = N.)

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The diamond DimeNet++ potential was trained on the experimental elastic stiffness tensor C of diamond, which has three distinct moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa [W3168247670#013]. The loss also assumes a stress-free state (σ = 0) at zero strain [W3168247670#013]. The experimental density (3512 kg/m3) and temperature (298.15 K) set the simulation conditions [W3168247670#013]. This matches the paper's statement that diamond was trained from its experimental stiffness tensor [W3168247670#004].
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer states the experimental elastic stiffness tensor with C11=1079, C12=124, C44=578 GPa and the stress-free zero-strain target, matching the reference; extra details on density and temperature do not contradict it.)
- support: supported (All claims (stiffness moduli, stress-free assumption in the loss, density and temperature setting simulation conditions, and the intro statement) are stated in the cited passages.)

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: The learned CG water model got the self-diffusion coefficient D wrong. It predicted D = 10.91 μm2/ms, much larger than the experimental D̃ = 2.2 μm2/ms [W3168247670#017]. By contrast, the tetrahedral order parameter q ≈ 0.569 matched the experimental 0.576 [W3168247670#017]. The passage attributes the error to CG models having smoother PESs, which accelerate dynamical processes compared to atomistic models. It also notes that CG water diffusion coefficients decrease as the number of interaction sites increases [W3168247670#017].
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (The answer identifies the self-diffusion coefficient (10.91 vs 2.2 μm²/ms), attributes it to smoother CG potential energy surfaces speeding up dynamics, and notes the tetrahedral order parameter matched, all consistent with the reference.)
- support: supported (All claims (D values, q values, smoother PES explanation, diffusion decreasing with more interaction sites) are stated in the cited passage.)

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: The passages do not say whether DiffTRe can fit a potential directly to a measured diffusion coefficient. In the DiffTRe coarse-grained water study, the self-diffusion coefficient D was a held-out observable, not a training target. The targets there were the oxygen RDF, ADF and pressure [W3168247670#017]. The learned model predicted D = 10.91 μm2/ms against an experimental 2.2 μm2/ms, so matching the target observables did not give a correct D [W3168247670#017]. A separate differentiable-simulation paper refined a potential using density and IR spectrum targets. It used diffusion coefficient error only to pick the final model, not as a fitting target [W4406553977#018].
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: The SchNet passages confirm that its C20 force field was trained on DFT (PBE+vdW-TS) reference data [W2778051509#019]. The DiffTRe authors see the main obstacle of this bottom-up approach as the limited availability of highly precise and sufficiently broad data sets. For larger systems such as macromolecules, quantum mechanics computations will remain intractable, which prevents ab initio data set generation altogether [W3168247670#003]. Instead, DiffTRe takes a top-down approach and trains NN potentials on experimental data. Its test cases use the experimental stiffness tensor for diamond, and pressure plus radial and angular distribution functions for coarse-grained water [W3168247670#003].
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: correct (It identifies the limitation as scarce precise, broad quantum data sets, and says DiffTRe trains top-down on experimental data, which matches the reference. It omits the accuracy cap from the reference method, but that is a minor gap, and the extra detail on diamond and water is consistent.)
- support: supported (All claims, including the SchNet C20 PBE+vdW-TS training data and the DiffTRe obstacle, top-down approach and test cases, are stated in the cited passages.)

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: The passages do not mention DiffTRe or its diamond model, so they do not say which empirical potential it started from (originally built for another element). They do say that early neural-network-potential studies of carbon allotropes covered the graphite–diamond coexistence line and diamond nucleation in graphite [W3189164715#120]. They also say that the Behler–Parrinello approach was first applied to bulk silicon [W2968923792#056]. Neither passage ties either element to DiffTRe, so I can't say which paper used the same element as a test system.
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: The passages do not say which graph neural network DiffTRe uses, because none of them mention DiffTRe. They only cover NequIP. On MD-17, NequIP significantly outperforms invariant GNN-IPs such as SchNet and DimeNet [W4225405705#010]. It also outperforms other equivariant networks, including PaiNN and NewtonNet, which are lmax = 1-only versions of equivariant networks, as well as ACE, SpookyNet, GemNet and UNiTE [W4225405705#010][W4225405705#011]. The passages do not connect any of this to DiffTRe's model.
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: Uprior is a constant potential encoding a-priori known properties of the system (e.g. the Pauli exclusion principle) [W3168247670#008]. Since DiffTRe has no pre-computed data set, the prior controls trajectory generation at the start of optimization [W3168247670#008][W3168247670#010]. It also makes the model learn only the difference between Uprior and the optimal potential, acting as a physics-informed initialization that speeds convergence [W3168247670#008]. It is not a Bayesian prior that biases the learnable parameters in the small-data regime: if it contradicts the data, Umodel θ corrects for it during optimization [W3168247670#008].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: correct (The answer covers the same key points as the reference: the prior encodes known physics, controls early trajectory generation, acts as a physics-informed starting point so the network learns a correction, and is overridden by the model if the data contradicts it.)
- support: supported (All claims (constant potential encoding known properties, trajectory generation control, learning the difference/initialization, not Bayesian and corrected by Umodel θ) are stated in the cited passages.)

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The passages do not give the total GPU hours for training the DiffTRe diamond potential. They say only that a DimeNet++ model was trained for an atomistic diamond model from its experimental stiffness tensor [W3168247670#004], and that DiffTRe cuts gradient-computation effort by around 2 orders of magnitude compared to backpropagation through the simulation [W3168247670#003]. No training time or GPU-hour figure for the diamond case appears.
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.

