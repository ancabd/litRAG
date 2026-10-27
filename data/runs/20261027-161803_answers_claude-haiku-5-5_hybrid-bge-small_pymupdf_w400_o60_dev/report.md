# Answer eval: claude-haiku-5-5

- **Generator:** `{"name": "claude", "provider": "anthropic", "model": "claude-haiku-5-5", "prompt": "answer-v1"}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1"}`
- **Retrieval:** hybrid, top 8 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 487184e30344)
- **Cost:** generator $0.024, judge $0.246

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.84 [0.72, 0.95] | 29 |
| Supported by its citations | 1.00 [1.00, 1.00] | 11 |
| Cites your evidence | 0.73 [0.54, 0.88] | 26 |
| Evidence was retrieved | 0.74 [0.56, 0.89] | 27 |
| Cites passages it wasn't given (lower is better) | 0.04 [0.00, 0.11] | 27 |
| Declines when unanswerable | 1.00 [1.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.07 [0.00, 0.17] | 29 |

Correct when the evidence was retrieved: 0.97 (n=20)

Correct when no evidence was retrieved: 0.64 (n=7)

## Effort per question (mean)

1.0 model calls, 1.0 tool calls (1.0 searches), 8.0 passages read, 5,700 input tokens, $0.0007 per question, 2.7 s. Gave up on 0%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: The passages do not say which test system Behler and Parrinello used to demonstrate their original neural network potential. They cite the 2007 Behler and Parrinello paper [W4392553098#017] and describe the method as a high-dimensional neural network potential [W3093149769#038], but neither names a test system. The silicon dataset in [W2991697224#016] is used in a later JAX-MD tutorial, not in the original demonstration.
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: The cutoff function is a cosine taper. It is written as fc(Rij) = 0.5 [cos(π Rij/Rc) + 1] for Rij ≤ Rc, and fc(Rij) = 0 for Rij > Rc [W2025444507#004]. The π is missing from the extracted text, so it is inferred from the garbled formula. Beyond Rc the function gives zero value and slope [W2025444507#004][W2025444507#005]. The paper used a cutoff Rc of 6 Å [W2025444507#005].
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: correct (The answer gives the same cosine cutoff formula, 0.5[cos(πR/Rc)+1] for R ≤ Rc and 0 beyond, as the reference; the extra details about the 6 Å cutoff and the inferred π do not contradict it.)
- support: supported (The passages give the garbled cosine cutoff form, state zero value and slope beyond Rc, and report a 6 Å cutoff; the answer openly notes the π was inferred, which fits the garbled text.)

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: In a high-dimensional neural network potential, the total energy E of the system is represented as a sum of atomic contributions Ei, i.e., E = sum over i of Ei [W2025444507#003][W4312043350#015]. Each atomic contribution is predicted by an atom-centered subnet that takes local symmetry-function descriptors as input, and summing these contributions yields the total energy [W2025444507#003][W3093149769#038]. The subnets share identical structure and weights, which keeps the total energy invariant to interchanging atoms of the same type [W2025444507#003][W2025444507#004].
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states that total energy is the sum of atomic energies, each predicted by an atom-centered neural network from local environment descriptors, which matches the reference; the cutoff is only implicit in 'local' but the extra details are consistent.)
- support: None (judge returned no valid verdict: The first claim, that E is a sum of atomic contributions Ei, is stated in W2025444507#003 and W4312043350#015.

The second claim has three parts. Each atom-centered subnet predicts an atomic contribut)

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP's internal features are equivariant to the E(3) group of rotations, reflections, and translations in 3D space, even though its predicted energy is invariant [W4225405705#005]. Each atom's features are geometric objects that form a direct sum of irreducible representations of O(3), indexed by a rotation order l and a parity p [W4225405705#006][W4319162181#004]. The network builds these features with equivariant tensor products, which combine tensors of different irreps while respecting symmetry [W4319162181#004]. Its convolution filters are products of learnable radial functions and spherical harmonics, with all learnable weights in the rotationally invariant radial part [W4225405705#006]. The layers build on Tensor-Field Networks and are implemented in e3nn [W4225405705#006].
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: correct (The answer states E(3) equivariance, features as direct sums of O(3) irreps (with l and parity), and construction via tensor products with spherical harmonic filters of relative positions, matching the reference.)
- support: None (judge returned no valid verdict: Check each claim.

1. Internal features equivariant to E(3), even though energy invariant. The passage says the focus is on equivariance with respect to E(3), and that the network contains internal fe)

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: NequIP and Behler-Parrinello (BP) handle rotational symmetry in fundamentally different ways. BP uses atom-centered symmetry functions built from distances and angles, which are hand-crafted features that make the atomic energies rotationally and translationally invariant [W3000291311#028][W2988055229#031]. NequIP instead uses equivariant convolutions based on spherical harmonics and Clebsch-Gordan transforms, operating on point clouds rather than fixed invariant descriptors [W3126679164#003]. Its features carry rotation order l, and these equivariant features encode rotational symmetry [W3132956480#076]. The passages do not give further detail on how NequIP's final outputs are made invariant.
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: correct (It captures that BP uses hand-crafted invariant symmetry functions while NequIP uses learned equivariant features (spherical harmonics, rotation order l), though it omits the explicit statement that only the final energy is invariant and does not mention message passing.)
- support: None (judge returned no valid verdict: )

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: The passages show only a limited overlap. NequIP is described as an E(3)-equivariant graph neural network interatomic potential [W4391631778#007][W4225405705#019]. In an ablation, the NequIP authors turned off all interactions with l > 0, which made the network "a conventional invariant GNN-IP, involving only invariant convolutions over scalar features in a SchNet-style fashion" [W4225405705#019]. So the shared element is invariant convolution over scalar features, but only in that restricted setting.

The passages do not say that NequIP uses SchNet's continuous-filter convolutions, atom embeddings, or interaction blocks. The equivariant tensor features that NequIP relies on are not a SchNet feature [W4225405705#019].
- reference: Several design choices come from SchNet. The initial atom features are a trainable embedding of the atomic number (one-hot encoded). Atoms then pass through a stack of interaction blocks that do continuous convolutions over neighbors within a cutoff. In those convolutions the learnable filter weights are an MLP of the interatomic distance expanded in a radial basis: Gaussians in SchNet, Bessel functions with an envelope in NequIP. The output is per-atom energies summed to a total energy, and forces are its negative gradient. The difference is that NequIP also multiplies the radial part by spherical harmonics of the bond direction. If only l = 0 (scalar) features are kept, NequIP reduces to a SchNet-style invariant network.
- correctness: partial (It correctly identifies that l=0-only NequIP reduces to a SchNet-style invariant network, but it explicitly says the passages don't support shared atom embeddings, interaction blocks, continuous convolutions, radial-basis MLP filters, or energy/force outputs, so it omits most of the reference's key shared features.)
- support: None (judge returned no valid verdict: )

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: NequIP's forward path begins from the atomic numbers and atomic positions, which it uses to predict the energy [W4391631778#007]. In the simplified architecture diagram, the first stage is an Embedding step, followed by interaction blocks and an output block [W4391631778#007]. The passages do not explain how the embedding is computed.
- reference: It embeds each atom's chemical species. The atomic number Z_i, one-hot encoded, goes through a trainable self-interaction (linear) layer. This gives the initial per-atom features, which are scalar (l = 0) only. The embedding follows SchNet. Higher-order tensor features first appear in the interaction blocks.
- correctness: partial (It correctly identifies the first step as an Embedding step starting from atomic numbers, but it states the passages don't explain the computation and omits the one-hot encoding, the linear self-interaction layer, and the scalar-only initial features.)
- support: supported (All claims (forward path from atomic numbers/positions to energy; Embedding, interaction blocks, output block in the diagram; no embedding details given) are stated in or consistent with the passage.)

**q009** (lookup): What datasets is Nequip tested on?
- answer: NequIP was tested on several datasets, mainly in the original NequIP paper:

- **MD-17** (eight small organic molecules) and **revised MD-17** (recomputed at PBE/def2-SVP) [W4225405705#023]
- **Molecules@CCSD/CCSD(T)**, including aspirin, benzene, malondaldehyde, toluene, and ethanol [W4225405705#023]
- **Liquid water and ice** structures [W4225405705#023][W4225405705#015]
- **Formate dehydrogenation on a Cu surface**, a heterogeneous catalysis test [W4225405705#015]
- **LiPS and Li4P2O7** (lithium superionic conductor and related systems), used for data-efficiency tests [W4225405705#002][W4225405705#020]

Other papers also report NequIP results. The design-space paper tested NequIP networks on the flexible drug-like molecule 3BPA [W4406405186#014]. The scaling-deep-learning paper trained NequIP on the M3GNet dataset [W
- reference: 1) MD-17 small organic molecules, both the original DFT version and the revised MD-17 (rMD17). 2) Small molecules at quantum-chemical accuracy: aspirin at CCSD; benzene, malonaldehyde, toluene and
   ethanol at CCSD(T).
3) Periodic systems:
   - liquid water and ice
   - a chemical reaction at a solid/gas interface (formate decomposition on a copper surface)
   - amorphous lithium phosphate (Li4P2O7)
   - a lithium superionic conductor (Li6.75P3S11, "LiPS")
- correctness: correct (The answer covers all the reference's dataset groups: MD-17 and rMD17, the CCSD/CCSD(T) molecules, water and ice, formate on Cu, and LiPS and Li4P2O7. The extra material on 3BPA and M3GNet does not contradict the reference.)
- support: None (judge returned no valid verdict: )

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: NequIP is compared against several groups of models on MD-17. It is benchmarked against invariant GNN interatomic potentials (SchNet and DimeNet), shallow neural networks (ANI), and kernel-based approaches (GAP, FCHL19/GPR, and sGDML) [W4225405705#010]. It is also compared with ACE, SpookyNet, and GemNet, and with the equivariant networks PaiNN, NewtonNet, and UNiTE [W4225405705#010]. The PaiNN and NewtonNet results are from lmax = 1-only versions of those networks [W4225405705#011].
- reference: Invariant GNN potentials: SchNet and DimeNet. A shallow neural network: ANI. Kernel methods: GAP, FCHL19/GPR and sGDML. Other methods: ACE, SpookyNet and GemNet. Other equivariant networks: PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are restricted to l_max = 1. Results for ACE, GAP and ANI on revised MD-17 are taken from another paper (Kovács et al.), not retrained by the authors. NequIP reports the best accuracy of all of them.
- correctness: correct (The answer lists all the reference's models (SchNet, DimeNet, ANI, GAP, FCHL19/GPR, sGDML, ACE, SpookyNet, GemNet, PaiNN, NewtonNet, UNiTE) and notes the lmax=1 restriction; it omits only the secondary details about Kovács et al. results and NequIP being best.)
- support: supported (All claims (invariant GNNs SchNet/DimeNet, ANI, GAP/FCHL19/GPR/sGDML, ACE/SpookyNet/GemNet, PaiNN/NewtonNet/UNiTE, and lmax=1-only note) are directly stated in the cited passages.)

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet takes the interatomic distance d_ij = ||r_i - r_j|| and expands it with radial basis functions e_k(r_i - r_j) = exp(-gamma ||d_ij - mu_k||^2), with centers mu_k from 0 Å to 30 Å spaced every 0.1 Å and gamma = 10 Å [W2726670313#009]. This expansion adds a non-linearity that makes initial filters less correlated and speeds training, since feeding raw distances would leave the filters highly correlated and cause a training plateau [W2726670313#009]. The expanded distances are then fed into two dense layers with softplus activations to compute the filter weight W(r_i - r_j) [W2726670313#009]. The filter-generating network is thus a function of the distance, which keeps the filters rotationally invariant [W2726670313#009].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: partial (The answer correctly describes the Gaussian expansion and its decorrelating purpose, but it gives gamma = 10 Å where the reference says 0.1 Å, and it sets the cutoff at 30 Å, which the reference does not state.)
- support: supported (Every claim, including the RBF parameters, the correlation and plateau rationale, the two softplus dense layers, and rotational invariance from distance inputs, is stated in the cited passage.)

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses a shifted softplus, ssp(x) = ln(0.5e^x + 0.5), as its non-linearity throughout the network [W2726670313#010][W2726670313#007]. This matters for force fields because forces are obtained by differentiating the energy model with respect to atom positions, so the model must be at least twice differentiable to allow gradient descent on the force loss [W2726670313#010]. The shifting ensures ssp(0) = 0 and improves network convergence, and the function has infinite order of continuity, which yields a smooth potential energy surface [W2726670313#010].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (Identifies the shifted softplus with the correct formula, notes that ssp(0)=0 and convergence improve, and explains that infinite differentiability gives a smooth energy surface and the twice-differentiability needed for force training; it omits vibrational modes, a minor detail.)
- support: supported (Every claim in the answer (shifted softplus definition, use throughout the network, the twice-differentiable requirement for force-loss gradient descent, ssp(0)=0, improved convergence, infinite order of continuity, smooth potential energy surface) is stated in the cited passages.)

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: Ordinary convolutions assume data on a regular grid, but atoms in a molecule do not sit on one. Atoms can be at arbitrary positions, so a fixed filter tensor as used in conventional convolutional layers is not applicable [W2778051509#006]. Unevenly spaced inputs like atom positions cannot simply use the same grid-based filter, so SchNet instead uses continuous filters generated by a neural network that maps positions to filter values [W2726670313#006].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (The answer states atoms are at arbitrary positions rather than on a regular grid, so a fixed filter tensor is inapplicable, and that SchNet uses continuous filters generated by a network from positions, matching the reference.)
- support: None (judge returned no valid verdict: The answer makes three claims, and the passages state each one.

1. Atoms are not on a regular grid but can sit at arbitrary positions, so a filter tensor of the kind used in conventional convolutiona)

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of rcut = 5 Å when learning formation energies of bulk crystals from the Materials Project data [W2778051509#014]. The same passage notes that this setting caused two examples containing isolated atoms to be discarded from the data set [W2778051509#014].
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer states the 5 Å cutoff on Materials Project data and that two structures with isolated atoms were discarded, matching the reference's key facts; omitting the QM9/MD17 note is minor.)
- support: supported (The passage states that rcut = 5 Å was set for formation energies of bulk crystals from the Materials Project and that two examples with isolated atoms under this setting were discarded.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: SchNet does not predict forces directly. It predicts a scalar energy model and obtains forces as the negative gradient of that energy with respect to the atom positions, F_i = -∂E/∂r_i, which yields an energy-conserving force field by construction [W2726670313#010]. Because the energy predictions are rotationally invariant, the resulting force predictions are rotationally equivariant [W2726670313#010]. The network must be at least twice differentiable to allow gradient descent on the force loss, so it uses the shifted softplus activation to keep the potential energy surface smooth [W2726670313#010][W2726670313#007]. The energy and force terms are combined in the training loss, with the force term being the squared difference between the true forces and the negative gradient of the predicted energy [W2726670313#010].
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: correct (The answer states forces are the negative gradient of the predicted energy w.r.t. positions, giving an energy-conserving field, and that rotationally invariant energy yields equivariant forces, matching the reference; extra details on shifted softplus and loss are accurate.)
- support: None (judge returned no valid verdict: The answer's claims map closely onto the cited passages.

- **Forces from energy gradient.** Passage 010 states that SchNet obtains forces by differentiating the energy model with respect to atom posi)

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: SchNet's filters depend only on rotation-invariant interatomic distances. Its filter-generating network maps neighbor distances to filter values [W2778051509#033], and the filter is built from relative atom positions in a way that is roto-translationally invariant [W2988055229#033]. Its convolutions are therefore invariant scalar convolutions over scalar features [W4225405705#
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: partial (The answer correctly says SchNet's filters see only rotation-invariant distances and give scalar features, but it is cut off before saying anything about NequIP using neighbor direction and building equivariant geometric tensor features.)
- support: None (judge returned no valid verdict: {"verdict":"partial","reason":"The passage W2988055229#033 supports that SchNet's filter-generating network maps roto-translationally inv)

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: The SchNet paper compared against gradient domain machine learning (GDML) on MD17, alongside DTNN [W2778051509#017]. GDML is listed among kernel methods in a review of machine learning force fields [W3093149769#014].

NequIP reports beating kernel-based approaches on MD17. Its paper says it "significantly outperforms" kernel-based methods such as GAP, FCHL19/GPR and sGDML [W4225405705#010]. It also states that NequIP "outperforms all other methods" and that its gains over sGDML and FCHL19/GPR are notable because kernel methods usually do better than neural networks on small training sets [W4225405705#011]. The introduction describes NequIP as "competitive with kernel-based approaches" on small molecular datasets, though kernel methods at significant extra cost in training and prediction [W4225405705#002]. The passages do not state NequIP's error relative to GDML specifically.
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: correct (Identifies GDML as SchNet's kernel comparison and says NequIP outperforms kernel methods including sGDML, GAP and FCHL19, matching the reference; it omits that GDML was more data-efficient on small training sets, but the extra detail it gives does not contradict the reference.)
- support: None (judge returned no valid verdict: )

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: The SchNet paper says the atomic-contribution decomposition is a poor fit for the polarizability α and the electronic spatial extent ⟨R²⟩, where its predictions "fall noticeably short in terms of accuracy" [W2778051509#013]. It attributes this to the energy decomposition into atomic contributions being "not appropriate for these properties" [W2778051509#013]. The passages do not say that the Behler-Parrinello potential has this limitation.
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: correct (It names polarizability and electronic spatial extent <R^2> as the poor fits, and attributes this to the atom-wise decomposition, matching the reference; the note about Behler-Parrinello is an extra caveat that does not contradict it.)
- support: supported (All claims, including the quoted phrases and the note that Behler-Parrinello is not mentioned, match the cited passage.)

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: The passages do not state the specific flaw. CHARMM36m was presented as a refinement of the CHARMM36 protein force field with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. This implies CHARMM36 was less accurate for disordered proteins, but the passages do not explicitly say so.
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (The answer correctly says CHARMM36m improved accuracy for intrinsically disordered proteins and implies CHARMM36 was weaker there, but it omits the specific flaw (overstabilized compact and left-handed helical structures) and the retained accuracy for folded proteins.)
- support: supported (The refinement and improved-accuracy claim is stated in the passage, and the inference about CHARMM36 plus the caveat that no flaw is stated are consistent with it.)

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The passages do not specify which parts of the force field were changed to produce CHARMM36m. They say only that CHARMM36m is a refinement of CHARMM36 with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. The passages on CHARMM36 describe its backbone CMAP and chi1/chi2 dihedral parameters, but that comparison is between CHARMM36 and CHARMM22/CMAP, not CHARMM36m [W2109154308#000].
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: The passages do not report an experimental success rate for RFdiffusion in designing protein binders. The only mention of RFdiffusion is a reference-list entry, which gives its title ('De novo design of protein structure and function with RFdiffusion') without any results [W4391542588#028].
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: The passages do not state a dropout rate for training SchNet. The SchNet papers describe other training settings, such as the ADAM optimizer with minibatches of 32 and exponential learning rate decay [W2778051509#011][W2726670313#012], and SpookyNet reports training SchNet with Adam at a learning rate of 10^-4 and batch size 10 [W3159653252#028]. Dropout appears only in general discussions of regularization, not as a SchNet training setting [W3208687975#012][W2899663614#002].
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: Direct reverse-mode automatic differentiation backpropagates through the entire MD trajectory generation, saving all simulator operations and causing excessive memory use and exploding gradients [W3168247670#003]. DiffTRe instead bypasses differentiation through the simulation for time-independent observables by using thermodynamic perturbation theory/reweighting, so it only differentiates through the potential energy computation of decorrelated states from a single reference trajectory [W3168247670#006][W3168247670#012]. This avoids exploding gradients and reduces gradient computation cost by around 2 orders of magnitude, with memory requirements comparable to the adjoint method [W3168247670#001][W3168247670#003]. The paper's rule-of-thumb estimates for the toy example gave speed-ups of about 330 for the gradient computation, in line with measurements [W3168247670#012].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: correct (The answer matches the reference: DiffTRe avoids differentiating through the trajectory by using reweighting/thermodynamic perturbation theory, which avoids exploding gradients, gives about two orders of magnitude faster gradients, and needs memory comparable to the adjoint method.)
- support: None (judge returned no valid verdict: Checking each claim:

1. Direct reverse-mode AD saves all simulator operations, causing excessive memory use and exploding gradients: W3168247670#003 says it saves all operations, causing excessive me)

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: DiffTRe computes each weight as the normalized ratio of state probabilities under the current and reference potentials: wi = pθ(Si)/pθ̂(Si), divided by the sum of the same ratios over all retained states [W3168247670#005]. For a canonical ensemble, pθ(Si) ∼ e^(-βH(Si)), where H is the sum of potential and kinetic energy [W3168247670#005]. This gives wi = e^(-β(Uθ(Si) - Uθ̂(Si))) normalized over all states [W3168247670#005].

The kinetic energy drops out because it is inside H and is treated the same under both potentials, so it cancels in the ratio of Boltzmann factors [W3168247670#005]. Only the potential energy difference remains. For θ = θ̂, all weights equal 1/N, which recovers the plain time average [W3168247670#005].
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (The answer gives the same normalized Boltzmann weight w_i ∝ exp(-β(Uθ - Uθ̂)), explains that kinetic energy cancels in the ratio, and notes the weights are 1/N when θ equals the reference.)
- support: None (judge returned no valid verdict: The passage supports each main claim. Eq. (3) gives wi as the ratio pθ(Si)/pθ̂(Si) normalized by the sum over states. The passage states that pθ(Si) ∼ e^(-βH(Si)) and that H is the sum of potential an)

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe keeps reusing the current reference trajectory's decorrelated states while the effective sample size stays acceptable. It stops and samples a new reference trajectory, starting from the last sampled state S_N and using the current parameters θ as the new reference, once Neff falls below the predefined threshold N̄eff [W3168247670#006][W3168247670#007]. Because Neff is initially N, at least one θ update is always made per reference trajectory [W3168247670#007].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (The answer states that a new trajectory is simulated when the effective sample size falls below a threshold, starting from the last state of the old trajectory with the current parameters, which matches the reference; it omits the formula but adds no contradictions.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

1. "Keeps reusing the current reference trajectory's decorrelated states while Neff stays acceptable." Passage 007 says the procedure repeats "as long as the)

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The DiffTRe diamond potential (a DimeNet++ model) was trained on the experimental elastic stiffness tensor of diamond. Only three distinct stiffness moduli were used: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa (Voigt notation), along with the assumption of a stress-free state [W3168247670#013]. The experimental density (3512 kg/m3) and temperature (298.15 K) were used to set the simulation conditions [W3168247670#013].
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer matches the reference: experimental elastic stiffness tensor with C11=1079, C12=124, C44=578 GPa and a stress-free state; extra details on density and temperature are not contradictory.)
- support: supported (All claims (DimeNet++, three moduli with values, stress-free assumption, density 3512 kg/m3, temperature 298.15 K) are stated in the passage.)

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: DiffTRe's CG water model got the self-diffusion coefficient wrong. It predicted D = 10.91 μm²/ms, versus the experimental D̃ = 2.2 μm²/ms, so it was too large [W3168247670#017]. The tetrahedral order parameter, the other held-out property, matched the experimental value closely (q ≈ 0.569 vs. 0.576) [W3168247670#017].

The paper attributes the overestimate to the nature of coarse-grained models: their smoother potential energy surfaces give accelerated dynamics compared to atomistic models [W3168247670#017]. It also notes that diffusion coefficients in CG water models decrease with more interaction sites [W3168247670#017]. The authors suggest, tentatively, that the model acts like a single-site model early in optimization and becomes more like a multi-site model as it learns 3-body interactions, though this is framed as a possibility rather than a demonstrated cause [W3168247670#017]. A single-site tabulated potential with the same setup gave D = 14.15 μm²/ms, which is also too large [W3168247670#017].
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (The answer identifies the self-diffusion coefficient (10.91 vs 2.2 μm²/ms) as too fast, attributes it to the smoother potential energy surfaces of CG models, and notes the tetrahedral order parameter matched, all consistent with the reference.)
- support: None (judge returned no valid verdict: The answer's claims all appear in the passage:
- D = 10.91 vs. 2.2 μm²/ms, with the model too large: stated.
- q ≈ 0.569 vs. 0.576, a close match: stated, and q is a held-out observable.
- Smoother PE)

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: No, not with DiffTRe as described. The DiffTRe paper states that its reweighting scheme makes it invariant to the sequence of states, so "dynamical properties cannot be employed as target observables" [W3168247670#019]. In the DiffTRe study, the self-diffusion coefficient was only a held-out check on the learned model, not a fitting target [W3168247670#017].

A different, differentiable molecular simulation approach does fit diffusion coefficients. It computes the diffusion coefficient via the Green-Kubo formula and optimizes Lennard-Jones parameters against a target diffusion value [W4406553977#010]. That method is not DiffTRe, so the passages do not show DiffTRe fitting a measured diffusion coefficient.
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: correct (The answer says No and gives the same reason as the reference: reweighting is invariant to state order, so dynamical properties like diffusion can't be targets. The extra details about held-out validation and other methods don't contradict the reference.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

1. DiffTRe's reweighting makes it invariant to the sequence of states, so dynamical properties cannot be target observables. This is stated in W3168247670#01)

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: The passages don't directly compare SchNet's C20 training with DiffTRe, but the DiffTRe authors do describe the limits of DFT-based (bottom-up) training. They note that experimental data helps "for systems in which DFT accuracy is insufficient or generation of a quantum mechanical data set is computationally intractable" [W3168247670#020]. Instead, DiffTRe learns NN potentials from experimental data, such as the experimental stiffness tensor of diamond and pressure and radial and angular distrib
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: correct (It identifies the limitation as DFT accuracy being insufficient or quantum data sets being intractable to generate, and says DiffTRe trains on experimental data (e.g., diamond stiffness tensor, RDFs), which matches the reference's top-down approach.)
- support: None (judge returned no valid verdict: {"verd)

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: DiffTRe's diamond model starts from the Stillinger-Weber potential, which was originally parametrized for silicon. The authors adjusted its length and energy scales for carbon's smaller atoms [W3168247670#013].

The neural network potential paper that used silicon as its test system is "Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces" (2007), which applies its many-body NN potential to bulk silicon [W2025444507#001]. A survey also says the Behler-Parrinello approach was originally applied to bulk silicon [W2968923792#056]. The JAX MD paper also trains neural network potentials on silicon data, but it is a software tutorial rather than the source of the test system [W2991697224#016].
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: correct (It identifies the Stillinger-Weber potential parametrized for silicon and rescaled for carbon, and names the Behler-Parrinello 2007 paper (Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces) as the silicon test system, matching the reference.)
- support: None (judge returned no valid verdict: )

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: DiffTRe uses DimeNet++ as its learnable potential in the diamond and coarse-grained water examples [W3168247670#004]. More generally, its model is a graph neural network acting on the atomic graph, with an optional prior added to it [W3168247670#008].

On MD-17, NequIP significantly outperforms invariant GNN interatomic potentials such as SchNet and DimeNet [W4225405705#010], and it outperforms all other methods compared [W4225405705#011]. The passages do not report DimeNet++ MD-17 results or state directly that DimeNet++ belongs to the same family, so the comparison with DimeNet++ specifically cannot be confirmed.
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: correct (The answer identifies DimeNet++ for diamond and coarse-grained water and says NequIP significantly outperforms invariant GNN potentials such as SchNet and DimeNet on MD-17, matching the reference; the added caveat about DimeNet++ is not contradictory.)
- support: supported (Every claim, including the caveat about DimeNet++ lacking MD-17 results, matches the cited passages.)

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: In DiffTRe, the prior potential U_prior is not a Bayesian prior on the learnable parameters. Its role is to control trajectory generation at the start of optimization, since DiffTRe does not rely on pre-computed data sets [W3168247670#008]. It also acts as a physics-informed initialization that speeds convergence, and it reformulates training as learning the difference between U_prior and the optimal potential [W3168247670#008][W3168247670#010]. If the prior contradicts the data, the model potential corrects for it during optimization [W3168247670#008].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: correct (The answer matches the reference's key points: it is not a Bayesian prior, it controls early trajectory generation, it serves as a physics-informed starting point where the network learns a correction, and the model overrides it if the data contradicts it. It omits the specific examples, which are only illustrative.)
- support: supported (Every claim in the answer is stated in the cited passages: not a Bayesian prior, trajectory generation control at the start, physics-informed initialization speeding convergence, reformulation as learning the difference, and the model potential correcting a contradictory prior.)

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The passages do not state the total GPU hours needed to train the DiffTRe diamond potential. The diamond section describes the DimeNet++ model, the loss function, the 1000-atom simulation box, and the trajectory lengths (10 ps equilibration and 60 ps production per trajectory) [W3168247670#013], but gives no GPU-hour figure. The other passages report training times for different models, not this one.
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.

