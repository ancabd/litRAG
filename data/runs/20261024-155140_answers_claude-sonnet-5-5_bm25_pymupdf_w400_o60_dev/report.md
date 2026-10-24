# Answer eval: claude-sonnet-5-5

- **Generator:** `{"name": "claude", "provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "answer-v1"}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1"}`
- **Retrieval:** bm25, top 8 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 bc8e68a22fcc)
- **Cost:** generator $0.000, judge $0.000

_No reference answer, so correctness isn't judged: q007, q008, q009, q010._

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.58 [0.38, 0.77] | 24 |
| Supported by its citations | 1.00 [1.00, 1.00] | 9 |
| Cites your evidence | 0.74 [0.53, 0.89] | 19 |
| Evidence was retrieved | 0.63 [0.44, 0.81] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 20 |
| Declines when unanswerable | 1.00 [1.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.31 [0.14, 0.48] | 29 |

Correct when the evidence was retrieved: 0.78 (n=16)

Correct when no evidence was retrieved: 0.17 (n=6)

## Effort per question (mean)

1.0 model calls, 1.0 tool calls (1.0 searches), 8.0 passages read, 6,186 input tokens, 0.0 s. Gave up on 0%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: The passages do not say what test system Behler and Parrinello used in their original paper. They describe the method: atomic energy decomposition with local descriptors [W4312043350#015], and symmetry-function-based networks [W2988055229#031][W2541404351#007]. They also say Behler-Parrinello networks have mainly been used to predict the same molecular system so that MD simulations can run [W2988055229#031]. The only demonstration of a Behler-Parrinello network in the passages is the JAX MD study, which fits 64-atom silicon DFT data [W2991697224#016]. That study is not the original Behler-Parrinello demonstration.
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: The original Behler–Parrinello cutoff function is piecewise: fc(Rij) = 0.5[cos(π Rij / Rc) + 1] for Rij ≤ Rc, and 0 for Rij > Rc [W2025444507#004]. The π is garbled in the extracted text of that passage, but the ANI-1 passage gives the same form as 0.5 × cos(π Rij / RC) + 0.5 for Rij ≤ RC [W2541404351#007]. Beyond Rc the function has zero value and zero slope [W2025444507#004]. The original paper used Rc = 6 Å [W2025444507#005].
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: correct (The answer gives the same cosine cutoff, 0.5[cos(πR/Rc)+1] for R ≤ Rc and 0 beyond, matching the reference; the extra details (zero slope, Rc = 6 Å) do not contradict it.)
- support: None (judge returned no valid verdict: Checking each claim:

1. The original BP cutoff is piecewise, 0.5[cos(π Rij/Rc)+1] for Rij ≤ Rc, and 0 beyond. Passage 004 shows "0:5 h cos Rij Rc 1 i for Rij Rc; 0 for Rij > Rc". The π is garbled, an)

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: In a high-dimensional neural network potential, the total energy E is the sum of atomic contributions, E = sum_i E_i [W2025444507#003]. Each E_i comes from an atomic (sub)network whose input is a descriptor of atom i's local chemical environment, such as symmetry functions or an atomic environment vector [W2025444507#003][W2541404351#007][W4312043350#015]. All subnets share the same structure and weights for atoms of the same type, which keeps the total energy invariant when two atoms are interchanged [W2025444507#003]. The sum also lets the potential be applied to systems of different sizes [W2541404351#007][W2025444507#003].
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states that total energy is the sum of atomic energies from atomic networks using local environment descriptors, matching the reference, and adds correct extra detail such as weight sharing per element.)
- support: None (judge returned no valid verdict: The claims check out against the passages:

- E = sum_i E_i is stated in W2025444507#003.
- Each E_i comes from an atomic subnet fed a descriptor of the local environment, such as symmetry functions o)

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP's internal features are equivariant to E(3), the group of rotations, reflections and translations in 3D space [W4225405705#005]. Its internal features are geometric tensors (scalars, vectors and higher-order tensors) that are equivariant to rotation and reflection [W4225405705#005]. They are built from equivariant operations only, so the network's transformation properties are preserved by construction [W4225405705#005][W4319162181#003]. Atoms exchange information via filters that are also geometric tensors of increasing order [W4225405705#005]. The passages do not detail the specific construction, such as tensor products or spherical harmonics, for NequIP itself.
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: partial (It correctly identifies E(3) and geometric tensor features, but it omits the key construction details (irreps of O(3), tensor products with spherical harmonics of relative position vectors) and says the passages do not detail them.)
- support: None (judge returned no valid verdict: Checking each claim:

1. "NequIP's internal features are equivariant to E(3), the group of rotations, reflections and translations": W4225405705 says "we focus on equivariance with respect to E(3)", a)

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: The passages describe how Behler-Parrinello networks handle rotational symmetry, but none of them mention NequIP, so the comparison cannot be made from them. Behler-Parrinello maps coordinates to roto-translationally invariant features, built from radial (distance) and angular (angle) symmetry functions of neighbors, and feeds these into a dense network [W2988055229#031][W3000291311#028]. The passages also describe these symmetry functions as hand-crafted and largely ad hoc, so they require human intervention [W2742127985#002][W2963373387#003]. The input fingerprints are rotation-invariant and carry no directional information, so forces are obtained by differentiating the energy [W2976347420#003].
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: The passages only describe shared features at a general level. Both NequIP and SchNet are implicit-AEF MLIPs: they learn atomic features (embeddings) rather than using predefined descriptors, and both are graph neural network approaches [W4407925765#013]. Both fit the GNN-IP message-passing framework, in which a stack of message-passing layers updates node features by combining messages from neighboring nodes and edges, followed by a readout layer that predicts atomic energies [W4391631778#006]. Both use only two-body message-passing functions within a cutoff radius [W4391631778#024]. The passages do not give a detailed comparison of other specific architectural components. They also state that, unlike SchNet, NequIP is an equivariant GNN-IP [W4391631778#024].
- support: None (judge returned no valid verdict: {)

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: The passages only partly answer this. The simplified NequIP architecture in Figure 2a starts with an Embedding block, followed by interaction blocks and an output block [W4391631778#007]. The forward path takes atomic numbers {Zi} and atomic positions {ri} as input and predicts the energy [W4391631778#007]. The passages do not describe what the embedding computes, and the figure labels are the only mention of it.
- support: supported (The Embedding → interaction blocks → output block order comes from the figure labels, the forward-path inputs and energy output come from the caption, and the passage does not explain what the embedding computes.)

**q009** (lookup): What datasets is Nequip tested on?
- answer: The passages show NequIP being run on several datasets, but they don't give one complete list.

- **DPA-2 pre-training datasets:** NequIP was trained single-task on these datasets, with a batch size of 1 for 1 million steps [W4405574099#044]. The OC2M dataset is named explicitly: Allegro and NequIP could not finish data processing on it in one piece, so it was split into 4 subsets trained sequentially [W4405574099#057]. The other dataset names are not given in these passages.
- **MD17 datasets:** NequIP appears among neural-network force fields trained on MD17 with 1k training points, and in a comparison at 10k training points on the same datasets [W4315631504#032].
- **3BPA:** NequIP networks were trained at 300 K and tested at 300, 600 and 1,200 K on configurations of the flexible drug-like molecule 3-(benzyloxy)pyridin-2-amine (3BPA) [W4406405186#014].


{"answerable": true, "answer": "The passages show NequIP used on several datasets, but not a single complete list. In the DPA-2 work it was trained single-task on the pre-training datasets (batch size 1, 1M steps) [W4405574099#044], including OC2M, which had to be split into 4 subsets for NequIP and Allegro
- support: None (judge returned no valid verdict: )

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: On MD-17 (original and revised), NequIP is compared with invariant GNN-IPs (SchNet and DimeNet), shallow neural networks (ANI), and kernel-based approaches (GAP, FCHL19/GPR, sGDML) [W4225405705#010]. It is also compared with ACE, SpookyNet, GemNet, and other equivariant networks (PaiNN, NewtonNet, UNiTE) [W4225405705#010]. The paper reports that NequIP outperforms all of these methods [W4225405705#011].
- support: supported (Both the list of compared methods (#010) and the claim that NequIP outperforms all other methods (#011) are stated in the cited passages.)

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet first computes the interatomic distance dij = ∥ri − rj∥, which makes the filter rotationally invariant [W2726670313#009]. It then expands this distance with radial basis functions ek(ri − rj) = exp(−γ∥dij − μk∥²), with centers 0 Å ≤ μk ≤ 30 Å every 0.1 Å and γ = 10 Å. The expansion adds non-linearity, so the initial filters are less correlated and training is faster [W2726670313#009]. The expanded distances are fed into two dense layers with softplus activations to compute the filter weight W(ri − rj) [W2726670313#009].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: None (judge returned no valid verdict: )
- support: None (judge returned no valid verdict: The passage supports every claim in the answer. It says rotational invariance comes from using interatomic distances dij = ∥ri − rj∥ as input to the filter network. It gives the radial basis expansion)

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses a shifted softplus, ssp(x) = ln(0.5e^x + 0.5), as the activation function throughout the network [W2726670313#010][W2778051509#006]. The shift ensures ssp(0) = 0 and improves convergence, and the function has infinite order of continuity [W2778051509#006]. This matters for force fields because forces are obtained by differentiating the energy model with respect to atom positions, so the model must be at least twice differentiable for gradient descent on the force loss. The smooth activation gives a smooth potential energy surface [W2726670313#010]. It also gives smooth force fields and second derivatives, which are needed for training with forces and for calculating vibrational modes [W2778051509#006]. More generally, activation functions for neural network potentials must be smooth to avoid discontinuities in the forces, which rules out ReLU [W3093149769#039].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (The answer matches the reference: shifted softplus ln(0.5e^x+0.5), ssp(0)=0, better convergence, infinite differentiability yielding smooth energy surface, smooth forces, and second derivatives for force training and vibrational modes.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- The shifted softplus formula and its use throughout the network are in both W2726670313 and W2778051509.
- The shift ensuring ssp(0)=0, improved convergenc)

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: Ordinary convolutional layers use a filter tensor defined on a regular grid, as with image pixels, video frames or audio. Atoms sit at arbitrary positions rather than on a grid, so such a filter tensor is not applicable [W2778051509#006][W2726670313#006]. Re-sampling onto a grid is possible, but choosing an interpolation scheme is hard and may need many grid points [W2726670313#006]. Discretizing would also lose the precise atom locations, which carry essential physical information [W2726670313#001]. A discrete filter cannot capture subtle positional changes, which gives discontinuous energy predictions [W2726670313#005]. SchNet therefore uses continuous-filter convolutions, in which a filter-generating neural network maps positions to filter values [W2778051509#006][W2726670313#006].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (The answer states that atoms sit at arbitrary positions rather than on a regular grid, so a fixed filter tensor is inapplicable, and that SchNet uses continuous-filter convolutions with a filter-generating network mapping positions to filter values; the added detail does not contradict the reference.)
- support: supported (Every claim in the answer is stated in the cited passages: grid-based filters (W2778051509#006, W2726670313#006), re-sampling difficulty (W2726670313#006), loss of precise atom locations (W2726670313#001), discrete filters giving discontinuous energy predictions (W2726670313#005), and the filter-generating network in SchNet.)

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of rcut = 5 Å when predicting formation energies of bulk crystals from the Materials Project. Two examples that would have contained isolated atoms with this cutoff were discarded from the data set [W2778051509#014].
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer gives the 5 Å cutoff, Materials Project data, and the dropping of two structures with isolated atoms, matching the reference; the QM9/MD17 note is a parenthetical omission.)
- support: supported (The passage states that SchNet used rcut = 5 Å on Materials Project formation energies and discarded two examples that would include isolated atoms with that setting.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: The passages do not explicitly describe SchNet's mechanism for energy-conserving forces. They say SchNet is designed to reflect a smooth energy prediction with respect to atom positions and energy-conservation of the predicted force fields [W2726670313#007]. They also say that models with discontinuities in their predicted potential energy surface, such as those using discrete binning or one-hot bond types, cannot be trained with forces in this way [W2726670313#011]. Separately, another paper notes that forces are guaranteed to conserve energy when obtained as gradients of the total potential energy [W4225405705#004], but the passages never state that SchNet computes its forces this way.
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: SchNet's filters see only the interatomic distances to neighbors. They are generated by a network that maps the roto-translationally invariant distances to filter values, and only radial filters are used [W2988055229#033][W3093149769#042]. The features therefore stay scalar and rotation-invariant [W4225405705#003]. NequIP's filters use the relative position vector, factored into a learnable radial function of the distance times spherical harmonics of the unit vector: F(r_ij) = R(r_ij)Y(l)_m(r̂_ij) [W4225405705#006]. This lets angular information enter the filters, and atom features become equivariant geometric tensors (scalars, vectors, higher-order tensors) rather than just invariant scalars [W4225405705#003][W4225405705#006]. Keeping only the 0 ⊗ 0 → 0 interaction reduces NequIP to a conventional invariant, SchNet-like convolution over scalar features [W4225405705#008].
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: correct (The answer matches the reference: SchNet filters see only distances, giving invariant scalar features; NequIP filters use direction (spherical harmonics), giving equivariant geometric tensor features, and restricting to scalars reduces it to a SchNet-like network.)
- support: supported (Each claim matches the cited passages: SchNet's distance-only radial filters and invariance, NequIP's filter F = R(r)Y with equivariant tensor features, and the 0⊗0→0 reduction to a SchNet-like invariant convolution.)

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: The passages do not include the SchNet paper itself, so they do not say which kernel method it compared against on MD17. They do cover NequIP against kernel methods: it significantly outperforms kernel-based approaches such as GAP, FCHL19/GPR and sGDML on MD-17 [W4225405705#010]. The NewtonNet table is consistent with this for sGDML. NequIP's force MAE is lower than sGDML's on aspirin (0.348 vs 0.68), naphthalene, salicylic acid and toluene, but higher on ethanol (0.208 vs 0.33 is lower, while FCHL19 gets 0.136) and malonaldehyde (0.337 vs 0.41 is lower, while FCHL19 gets 0.245) [W3189651386#010]. NequIP is therefore not uniformly best against every kernel method in that table.
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: The passages do not include the SchNet paper, so they do not say for which properties the atomic-contribution decomposition is a poor fit. They describe the Behler-Parrinello decomposition into atomic energies [W2988055229#031][W3093149769#038], but none of them states SchNet's own caveat about it.
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: The passages only partly answer this. CHARMM36m is described as a refinement of CHARMM36 with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. This implies CHARMM36 was less accurate for those ensembles, but the passages do not describe the specific deficiency (for example, what went wrong in the original model).
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (It correctly says CHARMM36m improves ensembles for intrinsically disordered proteins, but it omits the specific problem (overstabilized compact and left-handed helical structures) and the preservation of folded-protein accuracy.)
- support: supported (The passage states CHARMM36m refines CHARMM36 with improved accuracy for backbone conformational ensembles of intrinsically disordered peptides and proteins, and gives no detail on the original model's deficiency, as the answer says.)

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The passages do not say which parts of the force field were changed from CHARMM36 to CHARMM36m. The CHARMM36m abstract says only that it is a refinement of CHARMM36 with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. It does not list the specific parameters that were modified.
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: The passages do not mention RFdiffusion or its experimental success rate for designing protein binders. They cover unrelated topics: DynamicBind docking success rates, PeSTo interface prediction, machine learning force fields, and others.
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: The passages do not state a dropout rate for SchNet. The SchNet passage gives only other training details: ADAM optimizer, 32 molecules per mini-batch, an initial learning rate of 10^-3 with exponential decay, a 1,000-example validation set for early stopping, and an exponential moving average over weights with decay rate 0.99 [W2726670313#012]. The other dropout rates mentioned (0.01, 0.5, keep probability 0.7) belong to different models [W4393094737#015][W2899663614#006][W2899663614#010].
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: Backpropagating through an MD simulation (direct reverse-mode AD or the adjoint method) pushes the gradient through the entire trajectory generation [W3168247670#003]. DiffTRe instead uses thermodynamic perturbation theory and reweighting to bypass differentiation through the simulation for time-independent observables [W3168247670#001]. It differentiates only through the potential energy computation of decorrelated states [W3168247670#011]. This avoids exploding gradients, since DiffTRe gradient magnitudes stay constant with simulation length while direct AD gradients grow exponentially [W3168247670#011]. It also gives about 2 orders of magnitude speed-up in gradient computation [W3168247670#001], with memory requirements comparable to the adjoint method [W3168247670#003]. Direct AD, by contrast, is typically intractable beyond about a hundred particles and a few hundred time steps [W3168247670#003]. Previously generated trajectories can also be re-used, which cuts wall-clock time per update [W3168247670#011]. The cost is that dynamical properties cannot be used as target observables, because the reweighting makes DiffTRe invariant to the sequence of states [W3168247670#019].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: correct (The answer captures the key facts: DiffTRe bypasses differentiating through the trajectory by using reweighting (thermodynamic perturbation theory) for time-independent observables, avoids exploding gradients, gives ~2 orders of magnitude speedup, and has memory comparable to the adjoint method; the extra details are consistent.)
- support: None (judge returned no valid verdict: Checking each claim:

1. Backpropagating through MD (direct AD or adjoint) pushes the gradient through the entire trajectory: supported by #003 ("both approaches backpropagate the gradient through the)

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: Each weight is the ratio of a state's probability under the current potential θ to its probability under the reference potential θ̂, normalized over all N states: wi = [pθ(Si)/pθ̂(Si)] / Σj [pθ(Sj)/pθ̂(Sj)] [W3168247670#005]. Assuming a canonical ensemble, state probabilities are Boltzmann, pθ(Si) ~ exp(−βH(Si)), where H is the sum of potential and kinetic energy and β = 1/(kB T) [W3168247670#005]. Substituting this into the ratio makes the kinetic energy cancel, so wi = exp(−β(Uθ(Si) − Uθ̂(Si))) / Σj exp(−β(Uθ(Sj) − Uθ̂(Sj))) [W3168247670#005]. The passage states that the kinetic energy cancels but does not spell out the algebra. Since the kinetic-energy term is the same in the numerator and denominator of each ratio, it appears to drop out, but that reasoning is my inference rather than something the passage says. When θ = θ̂, wi = 1/N [W3168247670#005].
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (The answer gives the normalized Boltzmann-ratio weights with only potential energy, explains that kinetic energy cancels since it is identical under both potentials, and notes w_i = 1/N when θ = θ̂, matching the reference.)
- support: supported (Every claim, including the weight formula, Boltzmann probabilities, the energy-difference form after the kinetic energy cancels, and wi=1/N for θ=θ̂, appears in the passage, and the answer correctly flags its own algebra explanation as inference.)

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe keeps reweighting the saved decorrelated states, computing gradients and updating θ, for as long as the effective sample size Neff stays at or above a predefined threshold N̄eff. When Neff < N̄eff, the statistical error from reweighting is no longer acceptably small, so a new reference trajectory is sampled using the current θ as the new ˆθ [W3168247670#007]. It starts from the last sampled state SN [W3168247670#006]. At least one θ update per reference trajectory is guaranteed, because initially Neff = N [W3168247670#007].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (Matches the reference: new trajectory is sampled when effective sample size falls below the threshold, using current parameters and starting from the last state of the old trajectory; extra detail is consistent.)
- support: None (judge returned no valid verdict: The answer's claims all appear in the cited passages:
- The loop of reweighting, gradient computation and updating repeats while Neff exceeds N̄eff. This is in #007.
- When Neff < N̄eff, a new traject)

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The DiffTRe diamond potential (a DimeNet++ model) was trained on the experimental elastic stiffness tensor of diamond [W3168247670#013]. Because of crystal symmetry, this tensor has three distinct moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. The crystal was also assumed to be stress-free (σ = 0) at zero strain [W3168247670#013]. The simulation used the experimental density (3512 kg/m3) and temperature (298.15 K) [W3168247670#013].
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer matches the reference on the experimental elastic stiffness tensor, the three moduli values (C11=1079, C12=124, C44=578 GPa), and the stress-free target at zero strain; the extra details (DimeNet++, density, temperature) do not contradict it.)
- support: supported (All claims (DimeNet++ trained on experimental stiffness tensor, three moduli with values, stress-free assumption at zero strain, density 3512 kg/m3 and 298.15 K) are stated in the cited passage.)

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: The held-out property DiffTRe's coarse-grained water model got wrong was the self-diffusion coefficient D. The model predicted D = 10.91 μm2/ms, versus the experimental D̃ = 2.2 μm2/ms [W3168247670#017]. The paper attributes this to coarse-graining: smoother PESs make CG models exhibit accelerated dynamical processes compared to atomistic models, and diffusion coefficients decrease with more interaction sites in CG water models [W3168247670#017]. The other held-out property, the tetrahedral order parameter q ≈ 0.569, closely matched the experimental 0.576 [W3168247670#017].
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (The answer identifies the self-diffusion coefficient (10.91 vs 2.2 μm²/ms), attributes the error to smoother potential energy surfaces in CG models accelerating dynamics, and notes the tetrahedral order parameter matched, all consistent with the reference.)
- support: supported (Every claim (D = 10.91 vs 2.2, the smoother-PES and interaction-site explanation, q ≈ 0.569 vs 0.576) is stated in the cited passage.)

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: The passages do not show DiffTRe being used to fit a diffusion coefficient. In the DiffTRe paper, the targets were oxygen RDF, ADF and pressure, and the self-diffusion coefficient D was only a held-out observable [W3168247670#017]. The learned model overestimated D (10.91 vs. 2.2 μm2/ms experimental) [W3168247670#017]. DiffTRe differentiates only through the potential energy computation of decorrelated states, not through the whole trajectory [W3168247670#012]. The passages do not say whether this suffices for a dynamical property like D. A different differentiable-simulation method did fit diffusion coefficients, using gradients of the Green-Kubo diffusion coefficient for Lennard-Jones particles and combined density and IR fitting for water [W4406553977#010][W4406553977#018]. That work does not describe DiffTRe, so it does not answer your question.
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: The SchNet passage says its C20 force field was trained on reference data from DFT (PBE+vdW-TS) calculations [W2778051509#019]. The DiffTRe authors see the main obstacle to this bottom-up learning as the limited availability of highly precise and sufficiently broad data sets. For larger systems such as macromolecules, quantum mechanics computations will stay intractable, which prevents ab initio data set generation altogether [W3168247670#003]. Instead, DiffTRe takes a top-down approach and trains neural network potentials on experimental data. The test cases are DimeNet++ for diamond, trained on its experimental stiffness tensor, and DimeNet++ for coarse-grained water, trained on pressure and on radial and angular distribution functions [W3168247670#003].
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: correct (Matches the reference: bottom-up DFT training is limited by availability of precise, broad data sets, and DiffTRe instead trains top-down on experimental data; the extra detail on intractable QM for large systems and the test cases does not contradict it.)
- support: None (judge returned no valid verdict: The answer's claims are mostly supported. The SchNet passage says the C20 reference data came from DFT at the PBE level with the TS van der Waals correction, and that SchNet was trained at the PBE+vdW)

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: The passages do not say which empirical potential DiffTRe's diamond model starts from, and DiffTRe is not mentioned at all. They do show that carbon (including diamond) has been studied with neural-network potentials: early ML-driven studies of graphite–diamond coexistence and diamond nucleation in graphite used a neural-network potential following ref 66 [W3189164715#120]. The passages do not identify a specific neural network potential paper that used diamond/carbon as its test system. The Behler–Parrinello approach was originally applied to bulk silicon [W2968923792#056], but nothing links that to the question's element.
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: The passages do not say which graph neural network DiffTRe uses as its learnable potential, because none of them mention DiffTRe. They do describe how NequIP compares with other models on MD-17. NequIP significantly outperforms invariant GNN-IPs such as SchNet and DimeNet, shallow neural networks such as ANI, and kernel-based approaches such as GAP, FCHL19/GPR and sGDML [W4225405705#010]. On the revised MD-17 data set it outperforms all other compared methods, including the equivariant networks PaiNN, NewtonNet and UNiTE [W4225405705#010][W4225405705#011]. Without a passage naming DiffTRe's model, I cannot say how that comparison applies to the family DiffTRe uses.
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: In DiffTRe, Uprior is a constant potential encoding a-priori known properties of the system, and it is not a Bayesian prior that biases the learnable parameters in the small data regime [W3168247670#008]. Its first role is to control trajectory generation at the start of the optimization [W3168247670#008][W3168247670#010]. Its second role is to reformulate the problem so that Umodel θ learns the difference between Uprior and the optimal potential, which gives a physics-informed initialization that speeds up convergence [W3168247670#008]. If Uprior contradicts the data, Umodel θ corrects for it during optimization [W3168247670#008].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: correct (The answer captures the key points: the prior potential controls trajectory generation early in training, gives a physics-informed starting point with the network learning a correction, and the network overrides it if the data contradicts it. It omits only the example forms (repulsive LJ or Stillinger-Weber), which are illustrative.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

1. Uprior is a constant potential encoding a-priori known properties: passage 008 says "a constant potential approximating a-priori known properties". Suppor)

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The passages do not say how many GPU hours it took to train the DiffTRe diamond potential. They describe training DimeNet++ for diamond from its experimental stiffness tensor [W3168247670#004], and they say DiffTRe cuts the computational effort of gradient computations by around 2 orders of magnitude compared to backpropagation through the simulation [W3168247670#003]. Neither passage gives a total training time in GPU hours.
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.

