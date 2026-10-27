# Answer eval: claude-haiku-5-5

- **Generator:** `{"name": "agent", "provider": "anthropic", "model": "claude-haiku-5-5", "prompt": "agent-v2", "tools": ["search", "read_around", "open_paper"], "max_turns": 8, "token_budget": 100000}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1"}`
- **Retrieval:** hybrid, top 5 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 487184e30344)
- **Cost:** generator $0.051, judge $0.277

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.88 [0.77, 0.96] | 28 |
| Supported by its citations | 1.00 [1.00, 1.00] | 8 |
| Cites your evidence | 0.69 [0.50, 0.88] | 26 |
| Evidence was retrieved | 0.70 [0.52, 0.85] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 28 |
| Declines when unanswerable | 0.33 [0.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.03 [0.00, 0.14] | 29 |

Correct when the evidence was retrieved: 0.95 (n=19)

Correct when no evidence was retrieved: 0.86 (n=7)

## Effort per question (mean)

2.8 model calls, 2.7 tool calls (2.6 searches), 10.9 passages read, 17,606 input tokens, $0.0016 per question, 5.1 s. Gave up on 3%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: Behler and Parrinello demonstrated their neural network potential on bulk silicon. Their 2007 paper states that "the high accuracy of the method is demonstrated for bulk silicon and compared with empirical potentials and DFT" [W2025444507#000], and that they "apply our ideas to the construction of an NN-based many-body potential for bulk silicon" [W2025444507#001]. The potential was also tested in a metadynamics simulation of a 64-atom bulk silicon cell [W2025444507#010].
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: correct (The answer identifies bulk silicon as the test system and notes comparison with DFT (plus empirical potentials), consistent with the reference; extra detail about metadynamics on a 64-atom cell is not contradictory.)
- support: supported (Both quotes appear verbatim in the cited passages, and the Fig. 4 caption in #010 describes a metadynamics simulation of a 64-atom bulk silicon cell comparing NN and DFT energies.)
- steps: search "Behler Parrinello neural network potential test system" (5 passages, 5 new); search "Generalized neural-network representation of high-dimensional potential-energy surfaces silicon" (5 passages, 5 new); answer

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: The original high-dimensional neural network potential (Behler and Parrinello, 2007) uses a cosine cutoff: fc(Rij) = 0.5 × [cos(π Rij / Rc) + 1] for Rij ≤ Rc, and fc(Rij) = 0 for Rij > Rc. This gives zero value and slope at the cutoff radius Rc [W2025444507#004]. The paper's own cutoff is Rc = 6 Å [W2025444507#005]. The formula is reconstructed from a garbled text extraction, but later papers quote the same form [W3000291311#028].
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: correct (The answer gives the same cosine cutoff, 0.5[cos(πR/Rc)+1] for R ≤ Rc and 0 beyond, as the reference; the extra details (zero value and slope at Rc, Rc = 6 Å) are consistent with it.)
- support: None (judge returned no valid verdict: Checking each claim:

1. The cosine cutoff formula: the garbled text in W2025444507#004 shows "0.5 [cos(Rij/Rc)+1] for Rij ≤ Rc; 0 for Rij > Rc", and the π is missing. The answer reconstructs it and s)
- steps: search "cutoff function high-dimensional neural network potential" (5 passages, 5 new); search "Behler-Parrinello neural network potential symmetry functions cutoff" (5 passages, 5 new); answer

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: The total energy in a high-dimensional neural network potential (HDNNP) is expressed as a sum of atomic contributions: E = Σ_i E_i, where E_i is the energy of atom i predicted by a neural network (subnet) from that atom's local environment [W2025444507#003][W4312043350#015]. The subnets share the same structure and weight parameters for atoms of the same element, which makes the total energy invariant to interchanging atoms of the same type [W2025444507#003]. Because of this decomposition, the same network can be applied to systems with different numbers of atoms [W3093149769#038].
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states that total energy is the sum of atomic energies, each predicted by a neural network from the atom's local environment, matching the reference; the added details about weight sharing and transferability are correct, and the cutoff is only implicit in 'local environment'.)
- support: supported (All three claims are stated in the cited passages: the sum of atomic contributions from local environments (W2025444507, W4312043350), identical subnet structure and weights ensuring invariance to interchanging atoms (W2025444507), and applicability to varying system sizes (W3093149769).)

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP is E(3)-equivariant, meaning it respects translations, rotations and reflections in 3D space. Its internal features are geometric tensors, each atom carrying scalar, vector and higher-order tensor features. Formally, these features are direct sums of irreducible representations of O(3), indexed by a rotation order l = 0, 1, 2, ... and a parity p = ±1 [W4225405705#005][W4225405705#006]. They are built with convolutions based on Tensor-Field Networks, implemented with e3nn. The convolution filters are products of a learnable radial function of the interatomic distance and spherical harmonics of the unit separation vector, so all learnable weights sit in the radial function [W4225405705#006][W4225405705#011]. Only the final predicted energy is invariant, while the internal features are equivariant [W4225405705#005].
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: correct (The answer states E(3) equivariance, features as geometric tensors indexed by O(3) irreps (l and parity), and construction via tensor-product convolutions with spherical harmonics of relative position vectors, matching the reference.)
- support: supported (Every claim in the answer (E(3) equivariance, geometric tensor features, O(3) irreps indexed by l and p, TFN/e3nn convolutions, radial function times spherical harmonics filters with all learnable weights in the radial function, invariant energy output with equivariant internal features) is stated in the cited passages.)
- steps: search "NequIP E(3)-equivariant features built from irreducible representations spherical harmonics" (5 passages, 5 new); search "NequIP equivariant neural network interatomic potentials" (5 passages, 5 new); answer

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: Behler-Parrinello networks enforce rotational invariance by construction through hand-designed descriptors. Their atom-centred symmetry functions are built from interatomic distances and angles, so the features are invariant to rotation and translation, and a dense network maps them to atomic energies [W2988055229#031][W3000291311#028]. NequIP instead uses E(3)-equivariant convolutions on geometric tensors, not scalar invariants alone [W4225405705#000]. Its internal features transform equivariantly under rotation, which lets it act directly on non-invariant inputs such as displacement vectors while keeping the predicted energy invariant [W4319162181#003]. Forces and other vector quantities are therefore equivariant, not just invariant [W4319162181#003][W4406405186#025].
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: correct (The answer matches the reference: BP uses hand-designed invariant descriptors (distances and angles), while NequIP uses equivariant features on geometric tensors with an invariant final energy. It does not mention message passing or learned features explicitly, but nothing it says contradicts the reference.)
- support: None (judge returned no valid verdict: Checking each claim:

1. BP networks use hand-designed descriptors with rotational invariance by construction, built from distances and angles, with a dense network mapping to atomic energies. W298805)
- steps: search "NequIP E(3)-equivariant rotational symmetry" (5 passages, 5 new); search "Behler-Parrinello symmetry functions rotation invariance" (5 passages, 5 new); answer

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: Both models share several design features. Both predict total energy as a sum of atomic energies, with forces obtained as the negative gradient of that energy, which gives energy conservation [W4225405705#005][W2726670313#010]. Both build a rotationally invariant energy [W4225405705#005][W2726670313#007]. Both embed atomic numbers into initial per-atom features [W4225405705#011][W2726670313#008], and both refine them through a series of interaction blocks [W4225405705#011][W2726670313#008]. Both also use a radial filter that depends on interatomic distance: NequIP's radial function R(r) [W4225405705#011], and SchNet's continuous filter generated from atom positions [W2726670313#006].

NequIP goes beyond SchNet in using equivariant tensor features of higher order, not only scalars [W4225405705#000].
- reference: Several design choices come from SchNet. The initial atom features are a trainable embedding of the atomic number (one-hot encoded). Atoms then pass through a stack of interaction blocks that do continuous convolutions over neighbors within a cutoff. In those convolutions the learnable filter weights are an MLP of the interatomic distance expanded in a radial basis: Gaussians in SchNet, Bessel functions with an envelope in NequIP. The output is per-atom energies summed to a total energy, and forces are its negative gradient. The difference is that NequIP also multiplies the radial part by spherical harmonics of the bond direction. If only l = 0 (scalar) features are kept, NequIP reduces to a SchNet-style invariant network.
- correctness: partial (The answer matches the reference on atomic-number embedding, interaction blocks, distance-dependent radial filters, summed atomic energies and forces as the negative gradient. It omits the cutoff-based neighbor convolutions, the radial-basis MLP details (Gaussians vs Bessel with envelope), the spherical harmonics of the bond direction, and the reduction to SchNet at l=0, and it is vague about the radial filter.)
- support: None (judge returned no valid verdict: )
- steps: search "NequIP equivariant neural network interatomic potentials" (5 passages, 5 new); search "SchNet continuous-filter convolutional neural network" (5 passages, 5 new); search "SchNet atom-wise energy contributions summed, forces as negative gradient of energy, interatomic distances expansion" (3 passages, 3 new); answer

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: In NequIP, the first step is an embedding: the initial feature is generated by a trainable embedding that operates on the atomic number Zi, represented as a one-hot encoding, implemented via a trainable self-interaction layer [W4225405705#009]. This is followed by a series of interaction blocks and then an output block [W4225405705#009].
- reference: It embeds each atom's chemical species. The atomic number Z_i, one-hot encoded, goes through a trainable self-interaction (linear) layer. This gives the initial per-atom features, which are scalar (l = 0) only. The embedding follows SchNet. Higher-order tensor features first appear in the interaction blocks.
- correctness: correct (The answer correctly states that the first step embeds the one-hot atomic number Z_i through a trainable self-interaction layer; it omits the scalar-only (l=0) and SchNet details, which are secondary, and nothing it says contradicts the reference.)
- support: supported (Both the embedding description (trainable, atomic number Zi as one-hot, trainable self-interaction layer) and the sequence of embedding, interaction blocks, then output block are stated directly in the passage.)
- steps: search "NequIP architecture first step embedding atomic species" (5 passages, 5 new); search "NequIP E(3)-equivariant neural network interatomic potential" (5 passages, 5 new); answer

**q009** (lookup): What datasets is Nequip tested on?
- answer: NequIP was tested on the original MD-17 and revised MD-17 sets of small organic molecules, and on the Molecules@CCSD/CCSD(T) set (aspirin, benzene, malondaldehyde, toluene, ethanol) [W4225405705#015][W4225405705#012][W4225405705#023]. It was also tested on a joint liquid water and ice dataset [W4225405705#012], on formate dehydrogenation on a Cu(110) surface [W4225405705#015], and on LiPS and Li4P2O7 systems [W4225405705#019].
- reference: 1) MD-17 small organic molecules, both the original DFT version and the revised MD-17 (rMD17). 2) Small molecules at quantum-chemical accuracy: aspirin at CCSD; benzene, malonaldehyde, toluene and
   ethanol at CCSD(T).
3) Periodic systems:
   - liquid water and ice
   - a chemical reaction at a solid/gas interface (formate decomposition on a copper surface)
   - amorphous lithium phosphate (Li4P2O7)
   - a lithium superionic conductor (Li6.75P3S11, "LiPS")
- correctness: correct (The answer covers all the reference datasets: MD-17 and rMD17, the CCSD/CCSD(T) molecules, water/ice, formate on Cu, LiPS and Li4P2O7. Its extra detail, Cu(110), does not contradict the reference.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- Original MD-17 and revised MD-17: W4225405705#023 describes both data sets under "Reference Data Sets", and for each it says 950 training configurations we)

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: In the original MD-17 comparison (Table I), NequIP is compared against FCHL19, UNiTE, GAP, ANI, ACE and GemNet-(T/Q) [W4225405705#013]. The table also notes that the UNiTE numbers are its "direct-learning" results, and GemNet uses the best of its T/Q versions [W4225405705#013]. The paper's text on the original MD-17 results also refers to PaiNN and NewtonNet, which are described as lmax = 1-only versions of equivariant networks [W4225405705#011]. The separate revised MD-17 table compares sGDML and GemNet-(T/Q) [W4225405705#014].
- reference: Invariant GNN potentials: SchNet and DimeNet. A shallow neural network: ANI. Kernel methods: GAP, FCHL19/GPR and sGDML. Other methods: ACE, SpookyNet and GemNet. Other equivariant networks: PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are restricted to l_max = 1. Results for ACE, GAP and ANI on revised MD-17 are taken from another paper (Kovács et al.), not retrained by the authors. NequIP reports the best accuracy of all of them.
- correctness: partial (The answer names several correct baselines (FCHL19, UNiTE, GAP, ANI, ACE, GemNet, PaiNN, NewtonNet, and the lmax=1 note), but omits SchNet, DimeNet, sGDML (placing it only in the revised table), and SpookyNet. It also leaves out that NequIP is best, and that the ACE, GAP and ANI results were taken from Kovács et al.)
- support: None (judge returned no valid verdict: )
- steps: search "NequIP MD17 comparison with other models" (5 passages, 5 new); search "NequIP E(3)-equivariant interatomic potentials molecular dynamics benchmark" (5 passages, 5 new); search "MD17 results table NequIP sGDML DeepPot-SE GAP FCHL SchNet energy force MAE" (5 passages, 4 new); search "Energy and force MAE for molecules on the MD-17 data set, table, sGDML, SchNet, PhysNet, Cormorant, ANI, GAP, FCHL19, DeepMD" (5 passages, 1 new); answer

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet first takes the interatomic distance d_ij = ||r_i − r_j|| as the input to its filter-generating network, which keeps the filters rotationally invariant [W2726670313#009]. It does not feed the raw scalar in directly. Instead, it expands the distance with radial basis functions e_k(r_i − r_j) = exp(−γ‖d_ij − μ_k‖²), with centers μ_k spaced every 0.1 Å between 0 and 30 Å and γ = 10 Å⁻² [W2726670313#009]. The expanded distances then pass through two dense layers with softplus activations to produce the filter weights W(r_i − r_j) [W2726670313#009]. The expansion is there to avoid a plateau early in training: the raw filters would be highly correlated, while the extra non-linearity makes the initial filters less correlated [W2726670313#009].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: None (judge returned no valid verdict: )
- support: None (judge returned no valid verdict: The passage supports almost every claim: distances as input for rotational invariance, the radial basis expansion with centers every 0.1 Å from 0 to 30 Å, two dense layers with softplus, and the plate)

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses the shifted softplus, ssp(x) = ln(0.5e^x + 0.5), as its non-linearity throughout the network [W2726670313#010]. It matters for force fields because SchNet predicts forces as the negative gradient of the learned energy with respect to atom positions, so the model must be at least twice differentiable to train on forces [W2726670313#010]. The shifted softplus gives a smooth potential energy surface, and it has infinite order of continuity, unlike ReLU-type functions [W2726670313#010]. The PhysNet paper makes the same point: max(0, x) is not differentiable at zero, which causes problems when continuous derivatives of the network output are needed [W2923693308#007].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (Correctly names the shifted softplus with the right formula and explains that its smoothness and infinite differentiability give a smooth energy surface and the second derivatives needed for force training; it omits the ssp(0)=0 and convergence point and vibrational modes, but these are minor.)
- support: None (judge returned no valid verdict: )
- steps: search "SchNet activation function shifted softplus" (5 passages, 5 new); search "SchNet activation function smooth continuous derivatives force field" (5 passages, 3 new); answer

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: Ordinary convolutions need a regular grid, and atoms in a molecule do not sit on one. Image convolutions rely on a filter tensor applied to pixels at fixed spacing. Atoms can be at arbitrary positions, so such a filter is not applicable, and resampling onto a grid needs an interpolation scheme that is hard to choose and may need many grid points [W2726670313#006][W2778051509#006]. SchNet therefore uses continuous-filter convolutions, where a neural network generates filter values from the interatomic positions [W2726670313#006].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (The answer states that atoms are at arbitrary positions rather than on a regular grid, so a fixed filter tensor can't be applied, and that SchNet uses continuous-filter convolutions with a network generating filters from relative positions, matching the reference; the interpolation point is extra and consistent.)
- support: supported (Every claim (grid requirement, filter tensor inapplicable to arbitrary atom positions, resampling and interpolation difficulty, neural-network-generated continuous filters) is stated in the cited passages.)
- steps: search "SchNet continuous-filter convolutional layers instead of image convolutions" (5 passages, 5 new); search "atoms not on a grid, molecular structures continuous convolution" (5 passages, 3 new); answer

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of r_cut = 5 Å when learning formation energies of bulk crystals from the Materials Project data [W2778051509#014].
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer gives the 5 Å cutoff on Materials Project data, matching the reference's key fact; omitting the dropped structures and the QM9/MD17 note is only missing minor detail.)
- support: supported (The passage states that for formation energies on Materials Project bulk crystals, SchNet used a distance cutoff rcut = 5 Å.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: SchNet predicts a single energy and obtains forces by differentiating that energy with respect to the atomic positions: the force on atom i is the negative gradient of the predicted energy, F̂_i = −∂Ê/∂r_i. Because the forces come from the energy model itself, they are energy-conserving by construction, a point the authors credit to Chmiela et al. [W2726670313#010]. Since the energy is rotationally invariant, the forces that follow from it are rotationally equivariant [W2726670313#010][W2726670313#007]. The network must be at least twice differentiable for this to work, which is why it uses the smooth shifted softplus activation [W2726670313#010]. The cost is that a force prediction needs a full forward and backward pass through the energy model, making it about twice as deep and computationally expensive [W2726670313#010].
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: correct (The answer states that forces are the negative gradient of the predicted energy with respect to atomic positions, and that rotational invariance of the energy gives equivariant forces, matching the reference; the extra details about differentiability and cost do not contradict it.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- Forces are the negative gradient of the energy, F̂_i = −∂Ê/∂r_i. Passage 010 states this.
- Forces are energy-conserving by construction, credited to Chmie)
- steps: search "SchNet forces conserve energy gradient of energy with respect to atomic positions" (5 passages, 5 new); search "SchNet continuous-filter convolutional neural network interatomic potentials forces as negative gradient" (5 passages, 2 new); answer

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: SchNet's filters see only interatomic distance. Each filter is generated from radial basis expansions of ‖r_i − r_j‖, which makes it rotationally invariant [W2726670313#009][W2778051509#006]. Because of this, the features it builds are scalar, and angular information comes only indirectly, through stacking interaction blocks that build many-body representations [W2726670313#009].

NequIP's filters see both distance and direction. Each filter is a learnable radial function R(r_ij) multiplied by spherical harmonics Y^(l)(r̂_ij) of the unit bond vector, and all learnable weights sit in the radial part [W4225405705#006]. Because the filters carry these angular harmonics, its features are equivariant tensors of different rotation orders l (scalars, vectors, higher-order tensors) rather than only invariant scalars [W4225405705#006]. This is what lets NequIP represent directional, vector- and tensor-valued quantities at each atom.
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: correct (Matches the reference: SchNet filters use only distances (radial basis), giving invariant scalar features; NequIP filters use distance and direction via spherical harmonics, giving equivariant tensor features. The answer omits the scalar-only reduction to SchNet, but this is a minor omission.)
- support: None (judge returned no valid verdict: )
- steps: search "SchNet continuous-filter convolution interatomic distances filter-generating network" (5 passages, 5 new); search "NequIP E(3)-equivariant convolution neighbor vectors spherical harmonics filters" (5 passages, 5 new); answer

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: The SchNet paper compared against GDML (gradient domain machine learning) on MD17, alongside the DTNN neural network [W2726670313#012][W2778051509#017]. A later paper describes GDML as a kernel-based method [W3003486042#028].

NequIP outperforms the kernel methods it was compared with. On the revised MD-17 data set, it "outperforms all other methods," including sGDML and FCHL19/GPR, which the NequIP paper notes are kernel methods that typically do better than deep networks on small training sets [W4225405705#011]. The passages I found do not state NequIP's numbers against GDML specifically.
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: correct (Correctly identifies GDML as SchNet's kernel comparison and states NequIP outperforms kernel methods including sGDML and FCHL19; omits GAP and the data-efficiency note but nothing contradicts the reference.)
- support: None (judge returned no valid verdict: )
- steps: search "SchNet MD17 comparison kernel method" (5 passages, 5 new); search "NequIP MD17 kernel methods comparison accuracy" (5 passages, 5 new); answer

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: The SchNet paper says the atomic-contribution decomposition is a poor fit for the polarizability α and the electronic spatial extent ⟨R²⟩. Its predictions for these two properties fall noticeably short in accuracy, which it attributes to the decomposition into atomic contributions not being appropriate for them [W2778051509#013]. The passage does not mention Behler-Parrinello directly, and it describes the atomic-contribution approach as a good choice for the other properties it tested [W2778051509#013].
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: correct (The answer identifies polarizability α and electronic spatial extent ⟨R²⟩ as the poorly fit properties, with the same attribution to atom-wise decomposition as the reference.)
- support: None (judge returned no valid verdict: The passage says SchNet's predictions of α and ⟨R²⟩ fall noticeably short in accuracy, "most likely due to" the decomposition of the energy into atomic contributions, which is "not appropriate for the)
- steps: search "SchNet atomic contributions poor fit properties Behler-Parrinello" (5 passages, 5 new); search "atom-wise contributions not suitable for extensive properties total energy" (5 passages, 5 new); answer

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: CHARMM36m was designed to improve the accuracy of polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins, so CHARMM36 was lacking in that respect [W2555870966#000]. The passages do not state the flaw explicitly, but a force-field comparison reports that the CHARMM36 ensemble for disordered peptides had a high population of left-handed α-helix, which is inconsistent with measured scalar couplings [W2234602429#000]. That is the closest concrete example I found.
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (It correctly says CHARMM36m targets disordered proteins and cites excess left-handed helix, but it omits the overly compact structures and the retention of accuracy for folded proteins, and it hedges that the flaw is not explicitly stated.)
- support: None (judge returned no valid verdict: The answer makes three claims. First, CHARMM36m was designed to improve backbone conformational ensembles for IDPs. W2555870966 says this directly. Second, CHARMM36 was therefore lacking in that respe)
- steps: search "CHARMM36m improved force field intrinsically disordered proteins overly compact" (5 passages, 5 new); search "CHARMM36m refinement of CHARMM36 protein force field" (5 passages, 4 new); search "CHARMM36 overly compact disordered peptides too collapsed, overstabilized helical structure, modified backbone CMAP" (1 passage, 0 new); read_around "W2555870966#000" (1 passage, 0 new); search "CHARMM36 simulations of intrinsically disordered proteins collapse, too compact dimensions compared with SAXS" (5 passages, 3 new); search "CHARMM36m addresses overly compact conformations of unfolded and disordered proteins in CHARMM36" (5 passages, 3 new); answer

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The provided papers only partly answer this. The CHARMM36m paper is described as a refinement of CHARMM36 with improved accuracy in generating backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. The corpus does not contain the full CHARMM36m paper (only its abstract), so I could not find which specific parameters (for example, CMAP backbone terms, side-chain dihedrals, or Lennard-Jones terms) were changed. The CHARMM36 NMR validation paper does say that CHARMM36 differs from CHARMM22/CMAP through changes in the internal parameters of the peptide backbone (via CMAP) and the χ1 and χ2 dihedrals [W2109154308#000], but that describes CHARMM36 relative to CHARMM22/CMAP, not CHARMM36m relative to CHARMM36. The full list of changes would need the CHARMM36m paper's methods section.
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (The answer declines to say what changed between CHARMM36 and CHARMM36m and does not identify the refit backbone CMAP or the modified TIP3P water Lennard-Jones terms on hydrogens, which are the reference's main points.)
- support: None (judge returned no valid verdict: The answer's claims check out against the passages:

1. CHARMM36m is a refinement of CHARMM36 with improved backbone conformational ensembles for IDPs. The W2555870966 abstract states this directly.
2)
- steps: search "CHARMM36m improved force field for intrinsically disordered proteins modified CHARMM36 changes" (5 passages, 5 new); search "CHARMM36m reparametrization backbone torsion CMAP modification Lennard-Jones tuning" (5 passages, 3 new); search "CHARMM36m modified CMAP backbone phi psi and Lennard-Jones well depth water-protein interactions scaled" (1 passage, 0 new); open_paper "W2555870966" (1 section); search "CHARMM36m refinement changes to CMAP and nonbonded Lennard-Jones parameters for protein backbone and side chains" (8 passages, 4 new); search "CHARMM36m versus CHARMM36 differences: modified backbone CMAP, side chain dihedral, water model TIP3P modified" (6 passages, 3 new); answer

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: I could not find the RFdiffusion paper itself in the collection, so I cannot give its experimental success rate for protein binder design. Across three searches, the only passages that mention RFdiffusion are a reference list entry and a related-work mention of Watson et al. (2022), which says RoseTTAFold was repurposed to generate protein-binder backbones "with successful experimental validation" [W4393118201#005]. That passage gives no rate. The collection does not contain the figure you are asking for.
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.
- steps: search "RFdiffusion experimental success rate protein binder design" (5 passages, 5 new); search "RFdiffusion de novo binders experimentally validated success rate percent of designs bind" (5 passages, 4 new); search "RFdiffusion binder design experiments biolayer interferometry hit rate" (5 passages, 3 new); answer

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: The passages I found do not state a dropout rate for SchNet. The SchNet papers describe the optimizer, learning rates, batch sizes and loss weighting, but none mention dropout. For example, the 2018 SchNet paper says models were trained with mini-batch SGD using ADAM on minibatches of 32 examples, with exponential learning-rate decay [W2778051509#011], and the 2017 paper uses an initial learning rate of 10⁻³ and an EMA of weights with decay 0.99 [W2726670313#012]. I could not find a dropout value in either paper, so I can't answer this from the collection.
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.
- steps: search "SchNet training dropout rate" (5 passages, 5 new); search "SchNet dropout" (10 passages, 7 new); search "dropout rate hyperparameter training details network" (5 passages, 5 new); search "dropout rate hyperparameter training details network" (5 passages, 2 new); answer

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: DiffTRe avoids differentiating through the MD trajectory. It uses thermodynamic reweighting, so the gradient of a time-independent observable flows through the reweighting weights and the potential energy of saved, decorrelated states, not through the simulation's integration steps [W3168247670#001][W3168247670#003]. Direct reverse-mode autodiff through the simulation stores the whole trajectory and suffers exploding gradients, while DiffTRe's gradients keep constant magnitude regardless of simulation length [W3168247670#011].

This buys about two orders of magnitude faster gradient computation than backpropagating through the simulation, and its memory needs are comparable to the adjoint method [W3168247670#003]. The caveat is that it applies to time-independent observables only. Dynamical properties such as diffusion coefficients still require differentiating through the trajectory, typically with the adjoint method [W4406553977#003].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: correct (The answer matches all key facts of the reference: no differentiation through the simulation, reweighting with autodiff, avoids exploding gradients, ~two orders of magnitude faster, memory comparable to the adjoint method, and time-independent observables only.)
- support: None (judge returned no valid verdict: )
- steps: search "DiffTRe differentiable trajectory reweighting" (5 passages, 5 new); search "backpropagation through molecular dynamics simulation memory cost chaotic gradients" (5 passages, 5 new); answer

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: In DiffTRe, each retained state S_i gets a weight w_i that is the Boltzmann probability ratio p_θ(S_i)/p_θ̂(S_i), normalized over all retained states. In the canonical ensemble this becomes w_i = exp(−β(U_θ(S_i) − U_θ̂(S_i))) divided by the sum of the same exponential over all states j [W3168247670#005]. Here θ̂ is the reference potential used to generate the trajectory, and β = 1/(k_B T). The weights are then used to compute reweighted observables and the loss [W3168247670#007].

The kinetic energy drops out because the state probabilities are Boltzmann factors of the full Hamiltonian H = U + K. When the ratio p_θ/p_θ̂ is taken, the kinetic energy term is identical for both potentials and cancels, leaving only the potential energy difference [W3168247670#005]. Only the potential energies therefore need to be recomputed for the current parameters θ, and the momenta do not need to be stored.
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (Matches the reference: normalized Boltzmann weights exp(-β(U_θ - U_ref)) with kinetic energy cancelling in the ratio; the omitted 'all weights 1/N at θ=ref' detail is minor.)
- support: None (judge returned no valid verdict: )
- steps: search "DiffTRe reweighting weights computed potential energy difference kinetic energy" (5 passages, 5 new); search "differentiable trajectory reweighting reweighting factor exp(-beta Delta U)" (5 passages, 4 new); answer

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe keeps reweighting and updating θ from the same reference trajectory until the effective sample size drops below a predefined threshold, N_eff < N̄_eff. At that point a new reference trajectory is sampled with the current θ as the new reference potential, starting from the last generated state [W3168247670#006][W3168247670#007].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (The answer states that a new trajectory is simulated when the effective sample size falls below a threshold, using the current parameters and starting from the last state, which matches the reference; it omits the exact N_eff formula, but that is only a minor detail.)
- support: supported (Passages 006 and 007 state that reweighting, gradient computation and updating repeat until N_eff < N̄_eff, then a new reference trajectory is sampled with the current θ as the new reference, starting from the last generated state S_N.)
- steps: search "DiffTRe differentiable trajectory reweighting when to simulate new trajectory" (5 passages, 5 new); search "DiffTRe reuse trajectory reweighting threshold effective sample size new simulation" (5 passages, 0 new); answer

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The DiffTRe diamond potential was trained on diamond's experimental elastic stiffness tensor. The loss uses three distinct stiffness moduli, C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa (Voigt notation), plus a stress-free state (σ = 0) at zero strain [W3168247670#013]. The experimental density (3512 kg/m³) and temperature (298.15 K) were used to set the simulation conditions [W3168247670#013].
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer matches the reference on the experimental elastic stiffness tensor, the three moduli (C11=1079, C12=124, C44=578 GPa) and the stress-free state at zero strain; the added density and temperature details do not contradict it.)
- support: supported (All claims (stiffness moduli values, stress-free state, density 3512 kg/m³, temperature 298.15 K setting simulation conditions) are stated in the cited passage.)
- steps: search "DiffTRe diamond potential trained on experimental data" (5 passages, 5 new); search "differentiable trajectory reweighting diamond structure experimental data" (5 passages, 4 new); answer

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: DiffTRe's coarse-grained water model got the self-diffusion coefficient wrong. It predicted D = 10.91 μm²/ms, while the experimental value is 2.2 μm²/ms, so it overestimates diffusion [W3168247670#017]. The paper attributes this to the smoother potential energy surfaces of coarse-grained models, which accelerate dynamical processes compared with atomistic models [W3168247670#017]. It also notes that the reweighting scheme makes DiffTRe invariant to the sequence of states, so dynamical properties cannot be used as training targets [W3168247670#019]. The tetrahedral order parameter, by contrast, matched experiment closely [W3168247670#017].
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (The answer identifies the self-diffusion coefficient with matching values (10.91 vs 2.2 μm²/ms), gives the smoother energy surface explanation, and notes the tetrahedral order parameter matched; the extra detail about reweighting is not contradictory.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

1. D = 10.91 vs. experimental 2.2 μm²/ms, an overestimate. Stated in #017. Supported.
2. The paper attributes this to smoother PESs of CG models accelerating)
- steps: search "DiffTRe coarse-grained water model held-out property" (5 passages, 5 new); search "differentiable trajectory reweighting coarse-grained water transferability failure" (5 passages, 3 new); answer

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: DiffTRe is not designed for this. The paper limits the method to time-independent observables: it "avoids exploding gradients" for "the common use case of time-independent observables" [W3168247670#003], and the abstract says it "bypasses differentiation through the MD simulation for time-independent observables" [W3168247670#001]. The training targets were thermodynamic, structural and mechanical properties such as pressure, RDF/ADF and the stiffness tensor [W3168247670#001][W3168247670#017].

In the coarse-grained water example, the self-diffusion coefficient was only a held-out check, not a fitting target. The learned model predicted D = 10.91 μm²/ms against an experimental 2.2 μm²/ms [W3168247670#017]. So the paper does not show DiffTRe fitting a potential to a measured diffusion coefficient. Doing so would go beyond what the paper establishes.
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: correct (The answer says DiffTRe is limited to time-independent observables and that diffusion was not a fitting target, which matches the reference's 'No'. It omits the reweighting-ignores-time-order explanation, but the key conclusion is the same.)
- support: None (judge returned no valid verdict: )
- steps: search "DiffTRe differentiable trajectory reweighting diffusion coefficient" (5 passages, 5 new); search "differentiable trajectory reweighting fitting potential to experimental observables" (5 passages, 3 new); search "diffusion coefficient observable top-down learning potential" (5 passages, 4 new); search "time-dependent observables not supported reweighting dynamic properties limitation" (5 passages, 1 new); answer

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: The DiffTRe paper does not mention SchNet's C20 force field by name, so I can't confirm that detail from it. On the rest, the authors argue that bottom-up potentials trained on DFT data are capped by the quality of that data: "inherently limiting model accuracy to the quality imposed by the underlying data-generating simulation" [W3168247670#002]. They also say the main obstacle is the "limited availability of highly precise and sufficiently broad data sets," and that quantum-mechanical data for larger systems such as macromolecules is intractable [W3168247670#002].

Instead, they train on experimental data using top-down learning with DiffTRe, which fits neural network potentials to experimental observables such as thermodynamic, structural and mechanical properties [W3168247670#001]. Their examples include a DimeNet++ model for diamond fitted to its experimental elastic stiffness tensor and a coarse-grained water model [W3168247670#013][W3168247670#001].
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: correct (The answer states both limitations (limited availability of precise, broad data sets, and accuracy capped by the reference data) and says DiffTRe trains top-down on experimental observables; the caveat about SchNet C20 not being named does not contradict the reference.)
- support: None (judge returned no valid verdict: The answer's claims are supported by the cited passages.

- **Quote on limited accuracy:** "inherently limiting model accuracy to the quality imposed by the underlying data-generating simulation" appe)
- steps: search "DiffTRe differentiable trajectory reweighting coarse-grained or SchNet C20 force field limitation of DFT training" (5 passages, 5 new); search "training machine learning potentials on experimental data instead of DFT reference energies" (5 passages, 5 new); search "SchNet carbon C20 fullerene neural network potential trained on DFT" (5 passages, 3 new); answer

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: DiffTRe's diamond model starts from the Stillinger-Weber potential, which was parametrized for silicon; the DiffTRe authors rescaled its length and energy scales for carbon [W3168247670#013]. The neural network potential paper that used silicon as its test system is "Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces" (2007), which applies its NN-based many-body potential to bulk silicon [W2025444507#001]. I did not check the author list for that paper, so the attribution to Behler–Parrinello is from memory, not from the passages.
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: correct (Identifies Stillinger-Weber for silicon rescaled for carbon, and the Behler-Parrinello 2007 paper (Generalized Neural-Network Representation...) with bulk silicon as test system, matching the reference.)
- support: None (judge returned no valid verdict: Claims:
1. DiffTRe's diamond model starts from the Stillinger-Weber potential parametrized for silicon, with length and energy scales adjusted for carbon. Supported by W3168247670#013.
2. The NN poten)
- steps: search "DiffTRe diamond empirical potential silicon" (5 passages, 5 new); search "differentiable trajectory reweighting diamond Tersoff potential" (5 passages, 5 new); search "neural network potential silicon test system" (5 passages, 5 new); search "machine learning interatomic potential applied to bulk silicon benchmark" (5 passages, 5 new); answer

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: 
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: incorrect (declined to answer although the corpus has the answer)
- steps: search "DiffTRe learnable potential graph neural network" (5 passages, 5 new); search "NequIP MD-17 comparison accuracy" (5 passages, 5 new); search "DimeNet++ MD17 comparison NequIP energy force MAE" (5 passages, 4 new); search "DimeNet++ MD17 benchmark results" (5 passages, 3 new); answer

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: In DiffTRe, the prior potential U_prior is a constant potential that approximates a-priori known properties of the system, such as the Pauli exclusion principle. It is added to the learnable model potential, and it is not a Bayesian prior: it does not impose a bias on the learnable parameters in the small-data regime. If it contradicts the data, the model potential corrects for it during optimization [W3168247670#008]. Its practical roles are to control trajectory generation at the start of optimization and to act as a physics-informed initialization that speeds up training convergence [W3168247670#008].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: correct (The answer captures the key points: a physics-based potential added to the NN, not a Bayesian prior, controlling early trajectory generation, acting as a physics-informed starting point, and being overridden by the data when they conflict.)
- support: None (judge returned no valid verdict: The answer's claims all appear in the passage. U_prior is described as a constant potential approximating a-priori known properties such as the Pauli exclusion principle. It is added to the model pote)
- steps: search "DiffTRe prior potential not a Bayesian prior" (5 passages, 5 new); search "differentiable trajectory reweighting prior potential" (5 passages, 5 new); answer

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The DiffTRe paper (W3168247670) does not state a total GPU-hour figure for training the diamond DimeNet++ potential. Its diamond section reports only that the training loss and wall-clock time per update are shown in Supplementary Fig. 5 a [W3168247670#015], with no total given. The Methods and Supplementary text I could reach do not give a total either. The only GPU-hour figures in the retrieved passages belong to other papers (DTNN, GemNet), so they do not answer the question.
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.
- steps: search "DiffTRe diamond potential GPU hours training" (5 passages, 5 new); search "DimeNet++ diamond experimental stiffness training time GPU hours" (5 passages, 4 new); search "wall-clock time per update training loss diamond total GPU hours Supplementary" (5 passages, 4 new); search "computational resources GPU hours total training DiffTRe" (5 passages, 3 new); search "GPU hours Nvidia training took hours diamond DimeNet++ 1000 carbon atoms" (10 passages, 3 new); search "Supplementary Method diamond simulation details hardware optimization runtime hours" (5 passages, 0 new); search "training required single GPU for hours total computational effort" (5 passages, 1 new); give_up

