# Answer eval: claude-sonnet-5-5

- **Generator:** `{"name": "claude", "provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "answer-v1"}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1"}`
- **Retrieval:** hybrid, top 8 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 9e6de1d92dea)
- **Cost:** generator $0.458, judge $0.273

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.83 [0.71, 0.93] | 29 |
| Supported by its citations | 1.00 [1.00, 1.00] | 7 |
| Cites your evidence | 0.77 [0.62, 0.92] | 26 |
| Evidence was retrieved | 0.78 [0.63, 0.93] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 27 |
| Declines when unanswerable | 1.00 [1.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.07 [0.00, 0.17] | 29 |

Correct when the evidence was retrieved: 0.88 (n=21)

Correct when no evidence was retrieved: 0.83 (n=6)

## Effort per question (mean)

1.0 model calls, 1.0 tool calls (1.0 searches), 8.0 passages read, 5,700 input tokens, $0.0143 per question, 3.0 s. Gave up on 0%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: The passages do not say which test system Behler and Parrinello used for their original demonstration. They describe the architecture and cite the 2007 Phys. Rev. Lett. paper [W4392553098#017], but give no details of its test system. The only silicon example (64 Si atoms in different crystalline phases) is from a JAX, M.D. tutorial, not from Behler and Parrinello's own work [W2991697224#016].
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: The original cutoff function is fc(Rij) = 0.5 [cos(Rij/Rc) + 1] for Rij ≤ Rc, and 0 for Rij > Rc [W2025444507#004]. The passage text appears to have lost a symbol (presumably a multiplying constant) inside the cosine argument, so I can only give the form as extracted. Beyond the cutoff radius Rc the function has zero value and slope, and the Letter used Rc = 6 Å [W2025444507#004][W2025444507#005].
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: partial (The answer identifies a cosine cutoff with the 0.5[cos(...)+1] form and zero beyond Rc, but it writes cos(Rij/Rc) without the pi factor, so the stated formula is wrong, even though it notes a symbol may be missing.)
- support: None (judge returned no valid verdict: The answer's claims all trace to the cited passages. The passage gives the cutoff as "fcRij 8< : 0:5 h cos Rij Rc 1 i for Rij Rc; 0 for Rij > Rc", and the answer's rendering of it matches. The answer')

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: In a high-dimensional neural network potential the total energy E is the sum of atomic energy contributions, E = sum_i Ei [W2025444507#003][W4312043350#015]. Each Ei is predicted by an atomic NN (subnet) from symmetry-function descriptors of atom i's local environment [W2025444507#003][W2025444507#004]. The subnets share the same structure and weights, so the total energy is invariant when two atoms are interchanged [W2025444507#003]. Because the energy is a sum over atoms, the same network can also be applied to systems with different numbers of atoms [W3093149769#038].
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states that the total energy is the sum of atomic energies, each predicted by an atomic NN from the local environment of the atom, matching the reference; the extra details (symmetry functions, shared weights) are consistent with HDNNPs.)
- support: None (judge returned no valid verdict: Checking each claim:

1. E = sum_i Ei: supported by W2025444507#003 and W4312043350#015.
2. Each Ei is predicted by an atomic NN (subnet) from symmetry-function descriptors of atom i's local environme)

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP's internal features are equivariant under E(3), the group of rotations, reflections (inversion) and translations in 3D. This is achieved by using only E(3)-equivariant operations [W4319162181#003][W4225405705#005]. The features are geometric tensors forming a direct sum of irreducible representations (irreps) of O(3), indexed by rotation order l ≥ 0 and parity p ∈ (1, −1) [W4225405705#006][W4319162181#004]. They are built on Tensor-Field Network layers, with convolution filters F(r_ij) = R(r_ij)Y_m^(l)(r̂_ij), a learnable radial function times spherical harmonics, which are equivariant under SO(3) [W4225405705#006]. The key operation is the tensor product of representations, which combines tensors of different irreps in a symmetry-valid way using Wigner 3j symbols [W4319162181#004]. Translation invariance comes from filters acting on relative distance vectors [W4225405705#006].
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: correct (The answer states E(3), features as geometric tensors indexed by O(3) irreps, and tensor products with spherical harmonics of relative position vectors, matching the reference, with extra correct detail.)
- support: supported (Every claim in the answer is stated in the cited passages: E(3) definition and equivariant operations, irreps indexed by l and p, TFN-based filters with radial function times spherical harmonics, the tensor product with Wigner 3j symbols, and translation invariance from relative distance vectors.)

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: Behler-Parrinello networks map atomic coordinates to hand-designed, roto-translationally invariant atom-centered symmetry functions (radial and angular), and a dense network then predicts atomic energies from those features [W2988055229#031][W3000291311#028]. NequIP instead uses equivariant convolutions based on spherical harmonics and Clebsch-Gordan transforms [W3126679164#003]. The passages also describe graph neural networks in general as not needing manually crafted features [W3126679164#003]. NequIP's accuracy depends on the rotation order l of its features, and the passages report data-efficiency gains over a Behler-Parrinello network [W4225405705#021]. The passages do not give further detail on how NequIP's internal equivariant operations work.
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: partial (It correctly says BP uses hand-designed invariant symmetry functions and NequIP uses equivariant convolutions (spherical harmonics, Clebsch-Gordan), but it never states that NequIP's features are learned and carry vector/tensor information through message passing, or that only the final energy is invariant.)
- support: None (judge returned no valid verdict: Check claims:

1. BPNN maps coordinates to hand-designed, roto-translationally invariant atom-centered symmetry functions (radial and angular), then dense network predicts atomic energies. W2988055229)

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: The passages support only a partial answer. When NequIP's l > 0 interactions are switched off, it becomes a conventional invariant GNN-IP that uses invariant convolutions over scalar features in a SchNet-style fashion [W4225405705#019]. So the shared element is convolution over scalar (invariant) features, with the full NequIP adding equivariant tensor features on top [W4225405705#019]. NequIP also computes energy from atomic numbers and positions through an embedding, interaction blocks and an output block [W4391631778#007]. SchNet likewise uses atom embeddings, interaction refinements and atom-wise energy contributions [W2778051509#003]. The passages do not explicitly compare the two architectures beyond this, so any further shared features (for example radial basis expansions or filter-generating networks in NequIP) are not stated.
- reference: Several design choices come from SchNet. The initial atom features are a trainable embedding of the atomic number (one-hot encoded). Atoms then pass through a stack of interaction blocks that do continuous convolutions over neighbors within a cutoff. In those convolutions the learnable filter weights are an MLP of the interatomic distance expanded in a radial basis: Gaussians in SchNet, Bessel functions with an envelope in NequIP. The output is per-atom energies summed to a total energy, and forces are its negative gradient. The difference is that NequIP also multiplies the radial part by spherical harmonics of the bond direction. If only l = 0 (scalar) features are kept, NequIP reduces to a SchNet-style invariant network.
- correctness: partial (The answer correctly identifies the invariant scalar-convolution reduction, atom embeddings, interaction blocks, and atom-wise energies, but it omits radial-basis filter MLPs, the cutoff neighbors, and forces as the negative gradient, and says radial basis details are not stated.)
- support: None (judge returned no valid verdict: {"verdict": "supported", "reason": "Each claim matches)

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: The passages only partly answer this. The simplified NequIP architecture in Figure 2a is laid out as an Embedding block, then interaction blocks, then an Output block [W4391631778#007]. So the first listed step is an embedding, applied to the input atomic numbers and positions, which the forward path uses to compute energy [W4391631778#007]. The text does not say what the embedding computes. The passages also do not describe NequIP's own original embedding step beyond this figure.
- reference: It embeds each atom's chemical species. The atomic number Z_i, one-hot encoded, goes through a trainable self-interaction (linear) layer. This gives the initial per-atom features, which are scalar (l = 0) only. The embedding follows SchNet. Higher-order tensor features first appear in the interaction blocks.
- correctness: partial (It correctly identifies the first step as an embedding of atomic numbers, but it does not give the specifics (one-hot encoding, trainable linear self-interaction layer, scalar l=0 features) and says the text doesn't specify them.)
- support: None (judge returned no valid verdict: {"verdict": "partial", "reason": "The Embedding → interaction blocks → Output block order is supported, but the claim that the embedding is applied to both atomic numbers and positions is not; the pas)

**q009** (lookup): What datasets is Nequip tested on?
- answer: In the original NequIP paper, it is tested on original MD-17 (eight small organic molecules), revised MD-17, small molecules at CCSD/CCSD(T) accuracy (aspirin, benzene, malonaldehyde, toluene, ethanol), and liquid water and ice [W4225405705#023]. It is also tested on formate dehydrogenation on a Cu <110> surface [W4225405705#015], and on LiPS and Li4P2O7 (the lithium superionic conductor and amorphous solid systems) [W4225405705#020][W4225405705#002]. Other passages show NequIP used on the M3GNet dataset [W4389132751#033], on 3BPA at 300, 600 and 1,200 K [W4406405186#014], and in DPA-2 comparisons that include OC2M [W4405574099#057].
- reference: 1) MD-17 small organic molecules, both the original DFT version and the revised MD-17 (rMD17). 2) Small molecules at quantum-chemical accuracy: aspirin at CCSD; benzene, malonaldehyde, toluene and
   ethanol at CCSD(T).
3) Periodic systems:
   - liquid water and ice
   - a chemical reaction at a solid/gas interface (formate decomposition on a copper surface)
   - amorphous lithium phosphate (Li4P2O7)
   - a lithium superionic conductor (Li6.75P3S11, "LiPS")
- correctness: correct (The answer covers all reference datasets: MD-17 and rMD17, CCSD/CCSD(T) molecules, water/ice, formate on Cu, LiPS and Li4P2O7. The extra mentions of M3GNet, 3BPA and OC2M come from other papers and do not contradict the reference.)
- support: None (judge returned no valid verdict: )

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: On MD-17 (original and revised), NequIP is compared with invariant GNN-IPs (SchNet, DimeNet), shallow neural networks (ANI), and kernel-based approaches (GAP, FCHL19/GPR, sGDML) [W4225405705#010]. It is also compared with ACE, SpookyNet, GemNet, and other equivariant networks (PaiNN, NewtonNet, UNiTE) [W4225405705#010]. In the learning-curve experiment on aspirin, the baselines shown are sGDML, FCHL19, and PhysNet [W4225405705#020]. The paper reports that NequIP outperforms all other methods [W4225405705#011].
- reference: Invariant GNN potentials: SchNet and DimeNet. A shallow neural network: ANI. Kernel methods: GAP, FCHL19/GPR and sGDML. Other methods: ACE, SpookyNet and GemNet. Other equivariant networks: PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are restricted to l_max = 1. Results for ACE, GAP and ANI on revised MD-17 are taken from another paper (Kovács et al.), not retrained by the authors. NequIP reports the best accuracy of all of them.
- correctness: correct (The answer lists all the reference models (SchNet, DimeNet, ANI, GAP, FCHL19/GPR, sGDML, ACE, SpookyNet, GemNet, PaiNN, NewtonNet, UNiTE) and says NequIP outperforms them; it omits only the minor notes about l_max and the Kovács et al. results, and the extra PhysNet detail does not contradict the reference.)
- support: supported (Every claim in the answer matches the cited passages: the compared methods (#010), the aspirin learning-curve baselines (#020), and the 'outperforms all other methods' statement (#011).)

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet uses the interatomic distance dij = ∥ri − rj∥ as the filter network input, which makes the filters rotationally invariant [W2726670313#009]. The distance is first expanded with radial basis functions ek(ri − rj) = exp(−γ∥dij − μk∥²), with centers 0 Å ≤ μk ≤ 30 Å every 0.1 Å and γ = 10 Å. This extra non-linearity decorrelates the initial filters and speeds up training [W2726670313#009]. The expanded distances then go through two dense layers with softplus activations to give the filter weight W(ri − rj) [W2726670313#009].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: partial (The answer correctly identifies the Gaussian radial basis expansion on a uniform grid that decorrelates filters, but it gives a different gamma (10 Å vs the reference's 0.1 Å) and states the cutoff as 30 Å, which does not match the reference's description.)
- support: supported (All claims (distance input for rotational invariance, RBF expansion parameters, decorrelation and faster training, two dense softplus layers) appear in the cited passage.)

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses a shifted softplus, ssp(x) = ln(0.5e^x + 0.5), as the non-linearity throughout the network [W2726670313#010][W2726670313#007]. This matters because forces are obtained by differentiating the energy model with respect to atom positions, so the model must be at least twice differentiable to allow gradient descent on the force loss. A smooth activation gives a smooth potential energy surface [W2726670313#010]. The shift ensures ssp(0) = 0 and improves convergence. The function resembles ELUs but has infinite order of continuity [W2726670313#010].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (Identifies shifted softplus with the correct formula, notes ssp(0)=0 and improved convergence, and explains that infinite differentiability gives a smooth energy surface and the second derivatives needed for force training; only the vibrational-modes point is omitted, which is minor.)
- support: None (judge returned no valid verdict: Each claim in the answer matches the cited passages. W2726670313#010 states the shifted softplus definition, its use "throughout the network," the need for at least two derivatives for gradient descen)

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: Ordinary convolutional layers use a filter tensor defined on a regular grid, which works for image pixels, video frames or audio [W2726670313#006]. Atoms are not on a regular grid but can sit at arbitrary positions, so a filter-tensor is not applicable [W2778051509#006]. Discretizing would lose the precise atomic locations, which carry essential physical information [W2726670313#001]. A discrete filter also cannot capture subtle positional changes of atoms, giving discontinuous energy predictions [W2726670313#005]. Re-sampling onto a grid is possible, but choosing an interpolation scheme is itself a challenge and may need many grid points [W2726670313#006]. SchNet instead uses continuous-filter convolutions, with a filter-generating neural network that maps atom positions to filter values [W2778051509#006].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (The answer states that atoms are at arbitrary positions rather than on a regular grid, so a filter tensor is not applicable, and that SchNet uses continuous-filter convolutions with a filter-generating network mapping positions to filter values; the extra details do not contradict the reference.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

1. Ordinary convolutional layers use filters on a regular grid, for pixels, video frames or audio. W2726670313#006 says "convolutional layers operate on disc)

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of rcut = 5 Å when predicting formation energies of bulk crystals from the Materials Project. Two examples were discarded because they would have contained isolated atoms at this cutoff. [W2778051509#014]
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer matches the reference: 5 Å cutoff on Materials Project data, with two structures dropped for containing isolated atoms; omitting the QM9/MD17 note is a minor omission.)
- support: supported (The passage states SchNet used rcut = 5 Å on the Materials Project bulk crystal formation energy task and discarded two examples that would include isolated atoms at this cutoff.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: SchNet gets forces by differentiating its energy model with respect to the atom positions: F_i = −∂E/∂r_i. This gives an energy-conserving force field by construction [W2726670313#010]. Since the energy predictions are rotationally invariant, the forces are rotationally equivariant by construction [W2726670313#010]. For the gradient-based force loss, the model must be at least twice differentiable. SchNet therefore uses a shifted softplus non-linearity, ssp(x) = ln(0.5e^x + 0.5), to obtain a smooth potential energy surface [W2726670313#010]. Obtaining forces this way needs a full forward and backward pass through the energy model, so the force model is about twice as deep and takes about twice the computation time [W2726670313#010].
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: correct (The answer states forces are the negative gradient of the energy w.r.t. positions, giving an energy-conserving field and rotational equivariance from invariant energy, matching the reference; extra details on softplus and cost are consistent with SchNet.)
- support: None (judge returned no valid verdict: The passage supports each claim in the answer:

- Forces come from differentiating the energy w.r.t. atom positions, F_i = −∂E/∂r_i. The passage gives this as Eq. 4.
- This gives an energy-conserving )

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: Yes, the passages answer this. SchNet's filter-generating network maps the roto-translationally invariant interatomic distances to filter values [W2988055229#033]. Its features stay as scalars, so the convolution is the invariant 0 ⊗ 0 → 0 interaction [W4225405705#008].

NequIP's filter in the convolution has two parts, a radial function R(r_ab) of the neighbor distance and spherical harmonics Y(l_f)(r̂_ab) of the direction to the neighbor. These are combined with Clebsch-Gordan coefficients, li ⊗ lf → lo, with parity selection rule po = pi·pf [W4225405705#008]. This lets the network build features of higher rotation order l and parity, not only scalars. Dropping every interaction beyond 0 ⊗ 0 → 0 reduces NequIP to a conventional invariant GNN like SchNet [W4225405705#008].

The passages do not explicitly say what information the higher-order features
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: correct (The answer states SchNet filters use only invariant distances yielding scalar features, NequIP filters add direction via spherical harmonics enabling higher-order tensor features with parity, and restricting to 0⊗0→0 reduces NequIP to an SchNet-like invariant network, matching the reference; the truncated final sentence does not contradict it.)
- support: None (judge returned no valid verdict: )

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: SchNet was compared on MD17 against GDML (gradient domain machine learning), a kernel method, and also against DTNN [W2726670313#014][W2778051509#017]. NequIP's paper reports that it significantly outperforms kernel-based approaches such as GAP, FCHL19/GPR and sGDML [W4225405705#010]. It calls the consistent improvements over sGDML and FCHL19/GPR surprising, since kernel methods typically do better than deep neural networks on small training sets [W4225405705#011]. The introduction words this more cautiously, saying NequIP is 'competitive with kernel-based approaches' on small molecular data sets [W4225405705#002]. The passages do not directly compare NequIP with GDML itself.
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: correct (The answer identifies GDML as the kernel method SchNet compared against on MD17, and states that NequIP outperforms kernel methods including sGDML, GAP and FCHL19, matching the reference; the extra details (DTNN, the cautious intro wording) do not contradict it.)
- support: None (judge returned no valid verdict: Checking each claim:

1. SchNet was compared on MD17 against GDML, a kernel method, and DTNN. The passages support the comparison with GDML and DTNN. They do not call GDML a "kernel method" in the tex)

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: The SchNet paper says that decomposing the energy into atomic contributions is not appropriate for the polarizability α and the electronic spatial extent ⟨R2⟩, and SchNet's predictions for these fall noticeably short in accuracy [W2778051509#013]. The passages do not say that the SchNet paper makes this claim about the Behler-Parrinello potential specifically. They only describe that potential as summing atomic energies [W2988055229#031].
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: correct (The answer identifies polarizability α and electronic spatial extent ⟨R²⟩ as the poor-fit properties, matching the reference, and the extra caveat about Behler-Parrinello is not contradictory.)
- support: supported (The SchNet passage says its α and ⟨R2⟩ predictions fall short, most likely because atomic energy decomposition is inappropriate for them, and the second passage describes Behler-Parrinello as summing atomic energies without any SchNet critique, matching the answer's caveats.)

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: CHARMM36m refines CHARMM36 to give improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. The passages do not say specifically what went wrong with CHARMM36 for these systems, only that the refinement improves accuracy for them.
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (It correctly says CHARMM36m improves accuracy for intrinsically disordered proteins and peptides, but it explicitly omits the specific problem (overstabilized compact and left-handed helical structures) and the retained folded-protein accuracy.)
- support: supported (All claims match the abstract, and the caveat about the passage not explaining CHARMM36's shortcomings is accurate.)

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The passages do not say which parts of the force field were changed. The CHARMM36m abstract only says it is a refinement of CHARMM36 with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. It gives no details of the specific parameter changes, such as which terms were modified.
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: The passages do not state an experimental success rate for RFdiffusion binder design. RFdiffusion appears only as a reference entry (Watson et al., Nature 2023) in the DynamicBind reference list [W4391542588#028], and no passage reports results from it.
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: The passages do not give a dropout rate for SchNet. They describe its training setup: Adam optimizer, mini-batches of 32, a learning rate of 10^-3 with exponential decay of 0.96 every 100,000 steps, early stopping on a validation set, and an exponential moving average over weights with decay 0.99 [W2726670313#012][W2778051509#011]. A SpookyNet setup for SchNet on QM7-X uses a learning rate of 10^-4 and a batch size of 10 [W3159653252#028]. None of these mention dropout.
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: Direct AD backpropagates through the whole trajectory generation, whereas DiffTRe differentiates only through the potential energy computation of decorrelated states [W3168247670#012]. It uses a reweighting scheme (thermodynamic perturbation theory) that links the observable ⟨Ok(Uθ)⟩ directly to θ via the weights w, so differentiating through the reweighting replaces the backward pass through the simulation [W3168247670#006][W3168247670#001]. This avoids exploding gradients and gives about 2 orders of magnitude speed-up in gradient computation for time-independent observables, with memory requirements comparable to the adjoint method [W3168247670#003][W3168247670#001]. A trade-off is that dynamical properties cannot be targeted, since the reweighting makes it invariant to the sequence of states [W3168247670#019].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: correct (The answer matches all key points in the reference: it uses reweighting to avoid differentiating through the trajectory, avoids exploding gradients, gives about two orders of magnitude speed-up for time-independent observables, and has memory comparable to the adjoint method. The extra trade-off it mentions is consistent.)
- support: None (judge returned no valid verdict: Checking each claim:

1. Direct AD backpropagates through the whole trajectory, while DiffTRe differentiates only through the potential energy of decorrelated states: supported by #012.

2. Reweightin)

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: DiffTRe reweights decorrelated states from a reference trajectory generated with reference potential parameters ˆθ. Each weight is wi = pθ(Si)/pˆθ(Si), normalized by the sum of the same ratio over all states [W3168247670#005]. In the canonical ensemble the state probabilities are Boltzmann, pθ(Si) ~ exp(−βH(Si)), where H is the sum of potential and kinetic energy. The kinetic energy cancels in the ratio, leaving wi = exp(−β(Uθ(Si) − Uˆθ(Si))) / sum_j exp(−β(Uθ(Sj) − Uˆθ(Sj))) [W3168247670#005]. The passages state only that the kinetic energy cancels. They do not spell out the cancellation further. For θ = ˆθ, wi = 1/N [W3168247670#005].
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (The answer gives the normalized Boltzmann weight w_i = exp(-β(U_θ - U_ref))/sum, explains that the kinetic energy cancels in the ratio, and notes that w_i = 1/N when θ equals the reference, matching the reference.)
- support: None (judge returned no valid verdict: The answer's claims all appear in the passage: reweighting of decorrelated states from a reference trajectory with ˆθ, the weight definition with normalization, Boltzmann probabilities with H as the s)

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe keeps reusing the saved reference trajectory (its decorrelated states and reference energies) for repeated reweighting, gradient computation and parameter updates while the effective sample size Neff is larger than a predefined threshold N̄eff. As soon as Neff < N̄eff, the statistical error from reweighting is too large, so a new reference trajectory is sampled, with the current θ as the new reference ˆθ [W3168247670#007]. The new trajectory starts from the last sampled state SN [W3168247670#006][W3168247670#007]. At least one update is made per trajectory, since Neff = N initially [W3168247670#007].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (The answer states that a new trajectory is simulated when N_eff falls below a threshold, with current parameters, starting from the last state of the old trajectory, matching the reference; it omits the explicit entropy formula but is otherwise consistent.)
- support: supported (Every claim in the answer matches the cited passages, including the reuse of saved states, the Neff threshold, resampling with the current θ, starting from SN, and at least one update per trajectory.)

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The DimeNet++ diamond potential was trained on the experimental elastic stiffness tensor of diamond, which has three distinct moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa [W3168247670#013]. The crystal was also assumed to be stress-free (σ = 0) at zero strain [W3168247670#013]. The simulation used the experimental density (3512 kg/m3) and temperature (298.15 K) [W3168247670#013]. The abstract describes the observables as thermodynamic, structural and mechanical properties [W3168247670#001], but for diamond the passages specify only the stiffness tensor and zero stress as targets [W3168247670#013][W3168247670#004].
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer states the same experimental stiffness tensor (C11 = 1079, C12 = 124, C44 = 578 GPa) and the stress-free state at zero strain; extra details such as density, temperature and DimeNet++ do not contradict the reference.)
- support: None (judge returned no valid verdict: Checking each claim:

1. Trained on the experimental elastic stiffness tensor with C11=1079, C12=124, C44=578 GPa: supported by #013.
2. Stress-free assumption at zero strain: supported by #013.
3. Ex)

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: The learned CG water model got the self-diffusion coefficient D wrong: it predicted D = 10.91 μm2/ms against the experimental 2.2 μm2/ms [W3168247670#017]. The tetrahedral order parameter q (≈0.569 vs. 0.576 experimental) was matched closely [W3168247670#017]. The paper attributes the error to CG models having smoother PESs, which speeds up dynamics compared to atomistic models, and notes that diffusion coefficients decrease as the number of interaction sites increases [W3168247670#017]. A single-site tabulated IBI potential gave an even larger D of 14.15 μm2/ms [W3168247670#017]. The paper also suggests that D fell during optimization because Uθ began as an effectively single-site model and then learned 3-body interactions, which made it more like multi-site CG models [W3168247670#017].
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (The answer identifies self-diffusion coefficient (10.91 vs 2.2 μm²/ms) as wrong, attributes it to smoother PES of CG models speeding dynamics, and notes the tetrahedral order parameter matched; extra details are consistent.)
- support: None (judge returned no valid verdict: The answer's claims all check out against the passage. D = 10.91 vs 2.2 μm2/ms is stated. q ≈ 0.569 vs 0.576 is stated. The attribution to smoother PESs and the decrease of D with more interaction sit)

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: Not with DiffTRe as described in the DiffTRe paper. Its reweighting scheme makes it invariant to the sequence of states in the trajectory, so dynamical properties cannot be used as target observables [W3168247670#019]. In that paper, the self-diffusion coefficient was only a held-out observable that was computed, not a fitting target [W3168247670#017]. A different method, which differentiates through the dynamics, did fit a self-diffusion coefficient. It used a Green-Kubo formula for Lennard-Jones particles and optimized sigma and epsilon from a target diffusion coefficient [W4406553977#010]. That method was also used to pick the final water model by diffusion coefficient error [W4406553977#018].
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: correct (The answer states that DiffTRe's reweighting is invariant to the sequence of states, so dynamical properties like diffusion coefficients cannot be fitting targets, which matches the reference; the extra details about other methods are not contradictory.)
- support: None (judge returned no valid verdict: {"verdict": "supported", "reason": "Each claim matches the cited passages: DiffTR)

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: The DiffTRe authors do not name a single main limitation. They say bottom-up (quantum/DFT) training is a problem for systems where DFT accuracy is insufficient or where generating a quantum mechanical data set is computationally intractable [W3168247670#020]. They also say bottom-up data may be unavailable or not sufficiently accurate [W3168247670#004]. SchNet's C20 force field was trained on DFT data at the PBE+vdW-TS level [W2778051509#019].

Instead, DiffTRe learns neural network potentials top-down from experimental data. Examples are a DimeNet++ model of diamond trained on its experimental stiffness tensor, and a coarse-grained water model trained on pressure plus radial and angular distribution functions [W3168247670#004]. The passages do not say whether the water targets came from experiment or from a high-fidelity simulation.
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: correct (The answer captures that bottom-up DFT training is limited by data availability and reference-method accuracy, and that DiffTRe trains top-down on experimental data, matching the reference; the extra examples are not contradictory.)
- support: None (judge returned no valid verdict: )

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: DiffTRe's diamond model starts from the original Stillinger-Weber potential parametrized for silicon, with its length and energy scales adjusted (σSW = 0.14 nm, εSW = 200 kJ/mol) to reflect the smaller carbon atoms [W3168247670#013]. The neural network potential paper that used silicon as its test system is "Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces" (2007), which built an NN-based many-body potential for bulk silicon [W2025444507#001]. A review passage also describes the Behler-Parrinello approach as originally applied to bulk silicon [W2968923792#056]. The JAX MD paper likewise trains on silicon DFT data, but only as an example task [W2991697224#016].

```json
{"answerable": true, "answer": "DiffTRe's diamond model starts from the original Stillinger-Weber potential parametrized for silicon, with its length and energy scales adjusted for carbon [W3168247670#013]. The neural network potential paper that used silicon as its test system is 'Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces' (2007), which built an NN-based many-body potential for bulk silicon [W2025444507#001]. A review passage also describes the Behler-
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: correct (The answer identifies the Stillinger-Weber potential for silicon rescaled for carbon, and names the Behler-Parrinello 2007 paper (Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces) that used bulk silicon as its test system, matching the reference.)
- support: None (judge returned no valid verdict: {"verdict":"supported","reason":"Each claim matches its cited passage: the Stillinger-Weber prior with adjusted scales for carbon, the 2007 NN potential for bulk silicon, the Behler-Parrinello approac)

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: DiffTRe uses DimeNet++, which it calls a state-of-the-art graph neural network potential, for both the diamond and the coarse-grained water examples [W3168247670#004]. DimeNet++ is the improved variant of DimeNet. The NequIP paper does not mention DimeNet++ and compares only against DimeNet. It reports that NequIP significantly outperforms invariant GNN-IPs such as SchNet and DimeNet on MD-17 [W4225405705#010]. It also reports that NequIP outperforms all other methods on the revised MD-17 data set [W4225405705#011]. The passages contain no direct NequIP vs. DimeNet++ comparison.
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: correct (The answer identifies DimeNet++ for both diamond and coarse-grained water and states that NequIP significantly outperforms invariant GNN potentials such as SchNet and DimeNet on MD-17, matching the reference.)
- support: None (judge returned no valid verdict: {"verdict":"partial","reason":"The)

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: In DiffTRe, Uprior is a constant potential that approximates a-priori known properties of the system (e.g. the Pauli exclusion principle) [W3168247670#008]. It controls trajectory generation at the start of the optimization, since DiffTRe has no pre-computed data set [W3168247670#008][W3168247670#010]. It also reformulates the problem so that Umodel θ learns the difference between Uprior and the optimal potential, which makes it a physics-informed initialization that speeds up convergence [W3168247670#008]. It is not a Bayesian prior that biases the learnable parameters in the small-data regime. If Uprior contradicts the data, Umodel θ corrects for it during optimization [W3168247670#008].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: correct (Matches the reference's key points: the prior is a physics-based potential that controls early trajectory generation, gives a physics-informed starting point where the network learns a correction, and is overridden by the network if the data contradicts it. The 'constant potential' wording is slightly odd but does not contradict the reference.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- Uprior is a constant potential approximating a-priori known properties such as the Pauli exclusion principle: stated in #008.
- It controls trajectory gene)

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The passages do not state the total GPU hours needed to train the DiffTRe diamond potential. They describe the diamond setup: a DimeNet++ potential, 1000 carbon atoms, and trajectories with 10 ps of equilibration plus 60 ps of production [W3168247670#013]. The update steps in the figure axes run to about 700, but no GPU-hour figure is given [W3168247670#013].
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.

