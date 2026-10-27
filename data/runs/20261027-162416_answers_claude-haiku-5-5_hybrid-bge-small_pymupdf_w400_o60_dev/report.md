# Answer eval: claude-haiku-5-5

- **Generator:** `{"name": "claude", "provider": "anthropic", "model": "claude-haiku-5-5", "prompt": "answer-v1"}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1"}`
- **Retrieval:** hybrid, top 5 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 487184e30344)
- **Cost:** generator $0.018, judge $0.241

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.70 [0.55, 0.84] | 28 |
| Supported by its citations | 1.00 [1.00, 1.00] | 9 |
| Cites your evidence | 0.72 [0.52, 0.88] | 25 |
| Evidence was retrieved | 0.67 [0.48, 0.85] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 27 |
| Declines when unanswerable | 1.00 [1.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.07 [0.00, 0.17] | 29 |

Correct when the evidence was retrieved: 0.91 (n=17)

Correct when no evidence was retrieved: 0.39 (n=9)

## Effort per question (mean)

1.0 model calls, 1.0 tool calls (1.0 searches), 5.0 passages read, 3,661 input tokens, $0.0006 per question, 2.6 s. Gave up on 0%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: The passages do not say which test system Behler and Parrinello used in their original demonstration. They mention only later uses: the JAX-MD paper fits a Behler-Parrinello network to DFT data for 64 silicon atoms from a different study [W2991697224#016], and another review notes that Behler-Parrinello networks have mainly been used for the same molecular system to run MD simulations [W2988055229#031]. Neither is identified as the original test system.
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: The cutoff function is fc(Rij) = 0.5 × [cos(… Rij/Rc) + 1] for Rij ≤ Rc, and 0 for Rij > Rc [W2025444507#004]. The text extraction garbles the cosine argument, so the exact argument is not fully legible in the passage. The function yields zero value and slope at separations larger than Rc [W2025444507#004][W2025444507#005]. The paper used a cutoff of 6 Å [W2025444507#005].
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: correct (The answer gives the cosine cutoff 0.5[cos(·Rij/Rc)+1] for R≤Rc and 0 beyond Rc, matching the reference; the garbled argument is only a text-extraction issue, and the added details about zero slope and the 6 Å cutoff do not contradict the reference.)
- support: None (judge returned no valid verdict: Checking each claim:

1. The cutoff function form fc(Rij) = 0.5 × [cos(… Rij/Rc) + 1] for Rij ≤ Rc and 0 for Rij > Rc. The passage shows "0:5 h cos Rij Rc 1 i for Rij Rc; 0 for Rij > Rc". The garbled )

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: In a high-dimensional neural network potential, the total energy E of the system is represented as a sum of atomic contributions Ei, E = sum over i of Ei [W2025444507#003][W4312043350#015]. Each atom's contribution is produced by a subnet Si, a standard NN fed with symmetry function values describing that atom's local environment, and summing these contributions yields the total energy [W2025444507#003]. The subnets are constrained to be identical so the total energy stays invariant to interchanging two atoms of the same type [W2025444507#003][W2025444507#004]. This decomposition is the second-generation key step described for HDNNPs [W3141927472#000].]
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states that total energy is the sum of atomic energies, each from an atomic NN using that atom's local environment (via symmetry functions), matching the reference; the extra details on identical subnets are consistent.)
- support: None (judge returned no valid verdict: The last claim says the decomposition is "the second-generation key step described for HDNNPs." The abstract says HDNNPs form the second generation and rest on three key steps, the first of which is t)

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP's internal features are equivariant under the 3D Euclidean group E(3), which covers rotation, reflection (inversion), and translation [W4319162181#003][W4225405705#005]. Each atom's features are geometric tensors (scalars, vectors, and higher-order tensors), formally a direct sum of irreducible representations of O(3), indexed by rotation order l and parity p [W4225405705#006][W4319162181#004]. The network builds on Tensor-Field Network layers, implemented in e3nn [W4225405705#006]. Its convolution filters are products of learnable radial functions and spherical harmonics, F(r_ij) = R(r_ij) Y_m^(l)(r̂_ij), so that all learnable weights sit in the rotationally invariant radial function [W4225405705#006]. Tensor products of features, which are bilinear and respect the irreps, are another key operation [W4319162181#004].

{"answerable": true, "answer": "NequIP's internal features are equivariant under the 3D Euclidean group E(3), i.e. rotations, reflections and translations [W4319162181#003][W4225405705#005]. They are built as direct sums of irreducible representations of O(3), indexed by rotation order l and parity p, so each atom carries scalar, vector and higher-order tensor features [W4225405705#006][W4319162181#004]. The layers build on Tensor-Field Network layers
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: correct (The answer states E(3) symmetry, features as geometric tensors indexed by O(3) irreps (with l and parity), and tensor products with spherical harmonics of relative position vectors, which matches all key facts of the reference.)
- support: None (judge returned no valid verdict: {"verdict":"supported","reason":"Every claim matches the cited passages: E(3) equivariance, direct sums of O(3) irreps indexed by l and p, TFN layers implemented in e3nn, radial-times-spherical-harmon)

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: BP symmetry functions enforce rotational invariance through hand-crafted descriptors: atom-centered symmetry functions turn each local environment into numeric vectors that are rotationally and translationally invariant [W3000291311#028]. NequIP instead uses E(3)-equivariant graph neural networks, with equivariant convolutions based on spherical harmonics and Clebsch-Gordan transforms for point clouds [W3126679164#003]. Its features are organized by rotation order l, and the paper reports that l = 2 models learned with little data [W4225405705#021]. The passages do not give a full account of how NequIP's equivariance is implemented.
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: partial (It correctly says BP uses hand-crafted invariant descriptors and NequIP uses E(3)-equivariant networks with spherical harmonics and Clebsch-Gordan, but it never says that NequIP's features carry vector/tensor information through message passing, that only the final energy is invariant, or that the features are learned.)
- support: None (judge returned no valid verdict: Claim 1: BP/ACSF gives rotationally and translationally invariant numeric vectors. This is supported by W3000291311#028.

Claim 2: NequIP uses equivariant convolutions based on SH and CG transforms fo)

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: The passages give only a partial answer. The one shared feature they name is invariant convolutions over scalar features. When the NequIP authors turn off all interactions with l > 0, the network becomes "a conventional invariant GNN-IP, involving only invariant convolutions over scalar features in a SchNet-style fashion" [W4225405705#019]. The passages do not say that NequIP's full model uses SchNet's continuous-filter convolutions, atom embeddings, or atom-wise energy contributions [W2778051509#003]. Its equivariant tensor features, which the authors credit for its data efficiency, have no SchNet counterpart in these passages [W4225405705#019].
- reference: Several design choices come from SchNet. The initial atom features are a trainable embedding of the atomic number (one-hot encoded). Atoms then pass through a stack of interaction blocks that do continuous convolutions over neighbors within a cutoff. In those convolutions the learnable filter weights are an MLP of the interatomic distance expanded in a radial basis: Gaussians in SchNet, Bessel functions with an envelope in NequIP. The output is per-atom energies summed to a total energy, and forces are its negative gradient. The difference is that NequIP also multiplies the radial part by spherical harmonics of the bond direction. If only l = 0 (scalar) features are kept, NequIP reduces to a SchNet-style invariant network.
- correctness: partial (It correctly captures that NequIP restricted to l=0 reduces to a SchNet-style invariant network, but it misses the specific shared features (one-hot atomic number embedding, continuous convolutions within a cutoff, radial-basis MLP filters, summed per-atom energies with forces as negative gradient) and explicitly says they aren't supported.)
- support: None (judge returned no valid verdict: {"verdict": "supported", "reason": "Each claim matches the pass)

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: The passages do not describe the first step in detail. Figure 2a of the NequIP schematic lists an Embedding stage before the interaction blocks, and the forward path takes atomic numbers and atomic positions as inputs to compute energy [W4391631778#007][W4391631778#008]. The passages do not say what the embedding computes. They also note that the first interaction block omits the communication routines used in the others [W4391631778#007][W4391631778#008].
- reference: It embeds each atom's chemical species. The atomic number Z_i, one-hot encoded, goes through a trainable self-interaction (linear) layer. This gives the initial per-atom features, which are scalar (l = 0) only. The embedding follows SchNet. Higher-order tensor features first appear in the interaction blocks.
- correctness: incorrect (The answer says the passages do not describe what the embedding computes, and it gives none of the reference's key facts (one-hot atomic number, trainable linear self-interaction layer, scalar-only initial features), so it effectively declines to answer.)
- support: supported (Each claim matches the passages: Embedding appears in the Figure 2a text before the interaction blocks, the inputs are atomic numbers and positions, the embedding's computation is not described, and communication routines are omitted from the first interaction block.)

**q009** (lookup): What datasets is Nequip tested on?
- answer: NequIP was tested on several datasets, depending on the paper:

- **In the NequIP paper:** MD-17, revised MD-17 (rMD17), the Molecules@CCSD/CCSD(T) set (aspirin, benzene, malondaldehyde, toluene, ethanol), and a liquid water and ice dataset [W4225405705#023]. It was also applied to a formate-on-Cu catalytic surface dataset of 2,500 structures [W4225405705#015], and to a water data set from ref. 50 [W4225405705#037].
- **In the DPA-2 comparison:** NequIP was trained on the OC2M, Sn, and Drug datasets, among others [W4405574099#057]. The passage notes that NequIP could not finish data processing for OC2M on a machine with 155 GB of memory, so the OC2M data was split into subsets [W4405574099#057].
- **In the scaling study:** NequIP was trained on the M3GNet dataset [W4389132751#033].
- reference: 1) MD-17 small organic molecules, both the original DFT version and the revised MD-17 (rMD17). 2) Small molecules at quantum-chemical accuracy: aspirin at CCSD; benzene, malonaldehyde, toluene and
   ethanol at CCSD(T).
3) Periodic systems:
   - liquid water and ice
   - a chemical reaction at a solid/gas interface (formate decomposition on a copper surface)
   - amorphous lithium phosphate (Li4P2O7)
   - a lithium superionic conductor (Li6.75P3S11, "LiPS")
- correctness: partial (It correctly lists MD-17, rMD17, the CCSD/CCSD(T) molecules, water/ice and formate on Cu, but omits amorphous Li4P2O7 and the LiPS superionic conductor, and adds datasets from other papers (OC2M, Sn, Drug, M3GNet) that are not part of the reference.)
- support: None (judge returned no valid verdict: Checking each claim:

1. NequIP paper datasets (MD-17, rMD17, Molecules@CCSD/CCSD(T), liquid water and ice) are supported by #023. The list of molecules matches.
2. The formate-on-Cu dataset of 2,500 )

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: NequIP is compared against several groups of models on MD-17. Invariant GNN potentials include SchNet and DimeNet, and shallow neural networks include ANI. Kernel-based methods include GAP, FCHL19/GPR, and sGDML [W4225405705#010]. The paper also compares against ACE, SpookyNet, and GemNet, plus equivariant networks PaiNN, NewtonNet, and UNiTE [W4225405705#010]. It notes that PaiNN and NewtonNet are lmax = 1-only versions [W4225405705#010][W4225405705#011].
- reference: Invariant GNN potentials: SchNet and DimeNet. A shallow neural network: ANI. Kernel methods: GAP, FCHL19/GPR and sGDML. Other methods: ACE, SpookyNet and GemNet. Other equivariant networks: PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are restricted to l_max = 1. Results for ACE, GAP and ANI on revised MD-17 are taken from another paper (Kovács et al.), not retrained by the authors. NequIP reports the best accuracy of all of them.
- correctness: partial (The answer lists all the correct compared models and notes the PaiNN/NewtonNet l_max=1 restriction, but omits that ACE, GAP and ANI results were taken from Kovács et al. and that NequIP achieved the best accuracy.)
- support: supported (All listed model groups and the lmax = 1-only note for PaiNN and NewtonNet are stated in the cited passages.)

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet makes the filter rotationally invariant by using the interatomic distance d_ij = ||r_i - r_j|| as the filter network's input [W2726670313#009]. Rather than feeding the raw distance, it expands it with radial basis functions e_k(r_i - r_j) = exp(-gamma*||d_ij - mu_k||^2), with centers mu_k from 0 Å to 30 Å every 0.1 Å and gamma = 10 Å, which avoids a highly correlated initial filter and a training plateau [W2726670313#009]. The expanded distances are then fed into two dense layers with softplus activations to compute the filter weight W(r_i - r_j) [W2726670313#009]. One related paper describes the filter network more generally as taking the vector from atom i to neighbor j, but the distance-expansion step is specified in the first paper [W2778051509#007][W2726670313#009].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: partial (The answer correctly describes the Gaussian expansion of the distance with centers on a 0.1 Å grid and the decorrelation benefit, but it states a 30 Å upper bound and gamma = 10 Å, whereas the reference gives a cutoff-based range and gamma = 0.1 Å.)
- support: None (judge returned no valid verdict: The answer's claims all appear in the cited passages.

- Rotational invariance from the distance d_ij = ||r_i - r_j|| as filter-network input: stated in W2726670313#009.
- The radial basis expansion, )

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses a shifted softplus, ssp(x) = ln(0.5e^x + 0.5), as its non-linearity throughout the network [W2726670313#010][W2726670313#007]. It matters for force fields because the model must be at least twice differentiable so that gradient descent on the force loss is possible, and this smooth activation yields a smooth potential energy surface [W2726670313#010]. The shifting ensures ssp(0) = 0 and improves convergence, and the function has infinite order of continuity, similar to ELUs [W2726670313#010]. Forces are obtained by differentiating the energy model with respect to atom positions, which gives an energy-conserving force field by construction [W2726670313#010].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (Identifies the shifted softplus ln(0.5e^x+0.5), notes ssp(0)=0 and improved convergence, and links the infinite differentiability to a smooth energy surface and to the twice-differentiability needed for force training. It does not mention vibrational modes, but that is a minor omission.)
- support: supported (Every claim in the answer is stated directly in the cited passages W2726670313#010 and #007.)

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: Ordinary convolutional layers rely on a discrete grid, such as image pixels, where a filter tensor can be defined on the same grid. Atoms in a molecule are not located on a regular grid but can sit at arbitrary positions, so a filter tensor is not applicable [W2778051509#006]. The unevenly spaced atom positions cannot be handled this way, and re-sampling onto a grid requires an interpolation scheme that is hard to choose and may need many grid points [W2726670313#006]. SchNet therefore uses continuous-filter convolutions, where a filter-generating network maps atom positions to filter values [W2778051509#006][W2726670313#006].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (The answer states that atoms are at arbitrary positions rather than on a regular grid, so a fixed filter tensor is inapplicable, and that SchNet uses continuous-filter convolutions with a filter-generating network mapping positions to filter values, matching the reference.)
- support: supported (Every claim in the answer is stated in the cited passages.)

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of r_cut = 5 Å when learning formation energies of bulk crystals from the Materials Project data. The authors note that this setting caused them to discard two examples that would include isolated atoms [W2778051509#014].
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer gives the same 5 Å cutoff on Materials Project data and the same detail that two structures with isolated atoms were discarded; the missing note about QM9/MD17 is minor.)
- support: supported (The passage states rcut = 5 Å for Materials Project formation energies and that two examples with isolated atoms were discarded at this setting.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: {"answerable": true, "answer": "The passages state that SchNet is designed to reflect physical laws including "energy-conservation of the predicted force fields" [W2726670313#007]. They do not explain the mechanism that enforces this. The excerpts only say that SchNet was trained with energies and forces combined, which improved accuracy, and they do not say how that training guarantees conservation [W2778051509#018]. The mechanism is therefore not stated in the provided passages."}
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: incorrect (The answer does not give the mechanism (forces as the negative gradient of the predicted energy with respect to positions) and says it is not stated, whereas the reference explicitly provides it.)
- support: supported (The energy-conservation design claim is in W2726670313#007, and the claims about combined energy+force training improving accuracy without any stated conservation mechanism match W2778051509#018.)

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: The passages do not describe NequIP, so I can only answer for SchNet. SchNet's filter-generating network takes each neighbor's relative position, r_j - r_i, relative to the central atom, and outputs filter values for the feature bank [W2778051509#006]. A review describes these inputs as roto-translationally invariant interatomic distances [W2988055229#033]. Each learned filter represents the effect of an interaction on a given feature of the central atom [W2778051509#006].
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: The SchNet paper compared against gradient domain machine learning (GDML), a kernel method, on MD17, alongside DTNN [W2778051509#017].

NequIP's own paper reports that it significantly outperforms kernel-based approaches such as GAP, FCHL19/GPR, and sGDML on MD-17 [W4225405705#010]. Its introduction describes it more cautiously as competitive with kernel-based approaches on small molecular data sets, which typically achieve better accuracy than neural network potentials there [W4225405705#002]. The NequIP paper does not name GDML itself, so its results against GDML are not stated directly.
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: correct (The answer identifies GDML as the SchNet comparison and says NequIP outperforms kernel methods including sGDML, GAP and FCHL19, matching the reference; the extra caveats and the omitted data-efficiency note don't contradict it.)
- support: None (judge returned no valid verdict: )

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: According to the SchNet paper, the decomposition of the energy into atomic contributions is a poor fit for the electronic spatial extent ⟨R2⟩ and the polarizability α, where its predictions fall noticeably short in accuracy [W2778051509#013]. The paper attributes this most likely to the atomic-contribution decomposition not being appropriate for these properties, and notes that Gilmer et al.'s set2set variant avoids this issue by obtaining a global representation [W2778051509#013]. The passages do not state that the Behler-Parrinello potential itself is a poor fit for any property.
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: correct (The answer identifies the electronic spatial extent <R^2> and polarizability as the poor-fit properties and attributes it to the atom-wise decomposition, matching the reference; extra detail about set2set is plausible and not contradictory.)
- support: None (judge returned no valid verdict: Checking each claim against the passage:

1. SchNet's predictions of α and ⟨R2⟩ fall noticeably short in accuracy. The passage says this directly.
2. The shortfall is attributed "most likely" to the a)

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: The passages don't state the specific flaw in CHARMM36 directly. They say CHARMM36m is a refinement of CHARMM36 with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. This suggests the original force field was less accurate for intrinsically disordered systems, but the passages do not say so explicitly.
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (It correctly says CHARMM36m improves accuracy for intrinsically disordered proteins and peptides, but it omits the specific flaw (overstabilized compact and left-handed helical structures) and does not mention that accuracy for folded proteins was kept.)
- support: supported (The passage says CHARMM36m refines CHARMM36 with improved accuracy for backbone conformational ensembles of intrinsically disordered peptides and proteins, and the answer's inference about the original force field is explicitly hedged as not stated.)

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The passages don't specify which parts of the force field were changed to create CHARMM36m. The only CHARMM36m passage says it is a refinement of CHARMM36 with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. That describes the goal, not the specific parameter changes. The other passages discuss CHARMM36 relative to CHARMM22/CMAP, not the CHARMM36-to-CHARMM36m refinement [W2109154308#000].
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (The answer declines to say which parts were changed, while the reference gives specifics (a refit backbone CMAP correction and a modified TIP3P water with stronger Lennard-Jones on the hydrogens).)
- support: supported (All claims match the passages: CHARMM36m is described as a refinement with improved IDP backbone ensembles, no parameter changes are given, and the other passage compares C36 with CHARMM22/CMAP.)

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: The provided passages do not mention RFdiffusion or report any experimental success rate for protein binder design. The passages cover DIFFFORCE antibody design [W4399553795#022], DynamicBind's success rate of 0.33 for ligand docking [W4391542588#005], and other unrelated topics, so the question cannot be answered from them.
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: The passages do not state a dropout rate for training SchNet. They describe the optimizer, learning rates, batch sizes, and learning rate decay for SchNet [W2778051509#011][W2726670313#012][W3159653252#028], but none mention dropout. The GELU passage discusses dropout only in general terms, not as used for SchNet [W2899663614#002].
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: DiffTRe does not backpropagate through the MD simulation. It bypasses that differentiation for time-independent observables by using reweighting, which gives an alternative end-to-end differentiable path to the gradient [W3168247670#001][W3168247670#006]. Direct automatic differentiation backpropagates through the whole trajectory generation, whereas DiffTRe differentiates only through the potential energy computation of the decorrelated, subsampled states [W3168247670#012].

This buys a large gradient-computation speed-up, which the authors report as around 2 orders of magnitude. Leveraging thermodynamic perturbation theory also helps avoid exploding gradients [W3168247670#001]. The toy example gave measured speed-ups in line with the paper's theoretical estimates [W3168247670#012]. The method must still manage the effective sample size, and a new reference trajectory is needed once it drops below a threshold [W3168247670#006].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: correct (Matches the reference: no differentiation through the simulation, reweighting with thermodynamic perturbation theory, avoids exploding gradients, and gives ~2 orders of magnitude speed-up; omits the memory comparison to the adjoint method, but this is a minor omission.)
- support: None (judge returned no valid verdict: )

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: {"answerable": true, "answer": "In DiffTRe, the weight of each retained state S_i is the Boltzmann-type ratio of the perturbed to reference state probabilities, p_θ(S_i)/p_θ̂(S_i), normalized over all retained states [W3168247670#005]. Under the canonical ensemble, p_θ(S_i) ~ exp(-βH(S_i)), where H is the sum of potential and kinetic energy [W3168247670#005]. Because the kinetic energy is the same under both potentials, it cancels in the ratio, so each weight becomes w_i = exp(-β(U_θ(S_i) - U_θ̂(S_i))) divided by the sum of the same term over all states [W3168247670#005]. Only the potential energies of the saved states therefore need to be recomputed when θ changes [W3168247670#006]. For θ = θ̂ the weights reduce to 1/N [W3168247670#005].
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (The answer matches the reference: normalized Boltzmann ratio exp(-β(U_θ - U_ref)), kinetic energy cancels because it is the same under both potentials, and weights reduce to 1/N when θ equals the reference.)
- support: None (judge returned no valid verdict: The answer's claims all trace to the cited passages:

- Weights are the ratio p_θ/p_θ̂ normalized over states: Eq. 3 in #005.
- Boltzmann form with the Hamiltonian as the sum of potential and kinetic )

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe keeps reusing the stored reference trajectory for successive parameter updates, reweighting its decorrelated states each time. A new reference trajectory is simulated once the effective sample size falls below a predefined threshold, i.e. when Neff < N̄eff [W3168247670#007]. This is the point at which a new trajectory must be sampled, starting from the last sampled state S_N and using the current θ as the new reference [W3168247670#006][W3168247670#007].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (Matches the reference: a new trajectory is simulated when the effective sample size falls below a threshold, starting from the last state with the current parameters; the omitted entropy formula for N_eff is a minor detail.)
- support: supported (All claims (reuse of stored decorrelated states with reweighting, new trajectory when Neff < N̄eff, starting from last state S_N with current θ as new reference) are stated in the cited passages.)

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The DiffTRe diamond potential (a DimeNet++ model) was trained on diamond's experimental elastic stiffness tensor C, which has three distinct stiffness moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa (Voigt notation). [W3168247670#004][W3168247670#013] The training also used the experimental stress-free state assumption and the experimental density (3512 kg/m3) and temperature (298.15 K) to set the simulation conditions. [W3168247670#013]
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer gives the same elastic stiffness tensor values (C11=1079, C12=124, C44=578 GPa) and mentions the stress-free state; the extra detail on density and temperature does not contradict the reference.)
- support: None (judge returned no valid verdict: The answer says the model was trained on the experimental stiffness tensor with C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa in Voigt notation. Passage 013 states this directly, and passage 004 con)

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: DiffTRe's coarse-grained water model got the self-diffusion coefficient wrong. It predicted D = 10.91 μm²/ms, larger than the experimental value of D̃ = 2.2 μm²/ms [W3168247670#017].

The paper attributes this mainly to the coarse-grained representation. Due to smoother potential energy surfaces, CG models exhibit accelerated dynamics compared with atomistic models [W3168247670#017]. The authors also suggest that the model may act effectively as a single-site model early in training, and that learning 3-body interactions makes it more like multi-site CG models, which have lower diffusion coefficients [W3168247670#017]. The paper does not state this as a confirmed cause.
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (The answer identifies the self-diffusion coefficient with 10.91 vs 2.2 μm²/ms and attributes the error to smoother potential energy surfaces in CG models that accelerate dynamics, matching the reference; the extra details do not contradict it.)
- support: None (judge returned no valid verdict: The answer's claims match the passage. The values D = 10.91 and D̃ = 2.2 μm²/ms are both stated. The passage also gives the smoother-PES explanation, and says the diffusion coefficient decreases over )

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: **Answer: No, not with DiffTRe as described.** The DiffTRe paper states that its reweighting scheme makes the method invariant to the sequence of states in the trajectory, so dynamical properties cannot be used as target observables [W3168247670#019]. A diffusion coefficient is a dynamical property, so it falls outside DiffTRe's scope.

A different method can fit to diffusion. A separate differentiable molecular simulation study used the self-diffusion coefficient of Lennard-Jones particles, computed via the Green-Kubo formula, as a fitting target and optimized the potential parameters with its gradient [W4406553977#010]. That work is not DiffTRe, though.
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: correct (The answer says no, and gives the same reason as the reference: reweighting ignores the order of states in the trajectory, so dynamical properties like diffusion coefficients cannot be targets. The extra mention of another method is not contradictory.)
- support: None (judge returned no valid verdict: The answer's claims are all stated in the cited passages.

- **DiffTRe and dynamical properties:** W3168247670#019 says "The reweighting scheme renders DiffTRe invariant to the sequence of states in t)

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: The passages don't state a single "main limitation," but the DiffTRe authors point to two related problems with bottom-up training on quantum mechanical data: DFT accuracy can be insufficient, and generating a quantum mechanical data set can be computationally intractable [W3168247670#020]. Instead, DiffTRe learns NN potentials from experimental data, using top-down training on observables from experiments [W3168247670#019][W3168247670#020]. The SchNet C20 model was trained on 20k DFT reference calculations [W2778051509#019].
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: correct (The answer says bottom-up DFT training is limited by reference accuracy and by the availability or tractability of quantum data, and that DiffTRe trains top-down on experimental observables, matching the reference.)
- support: None (judge returned no valid verdict: Checking each claim:

1. The passages don't state a single "main limitation," but DiffTRe authors point to two related problems with bottom-up training: DFT accuracy insufficient, QM data set generati)

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: DiffTRe's diamond model starts from the Stillinger-Weber potential, which was originally parametrized for silicon. The authors rescaled its length and energy scales for carbon [W3168247670#013].

A neural network potential paper that used silicon as its test system is the JAX MD paper. It fits Behler-Parrinello and graph neural network models to DFT energies and forces for silicon in different crystalline phases [W2991697224#016]. A review also states that the Beh
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: None (judge returned no valid verdict: {"verdict":"partial","reason":"The Stillinger-Weber potential for silicon, rescaled for carbon, is correct. For the neural network paper, the answer names the JAX MD paper rather than the original Beh)
- support: None (judge returned no valid verdict: The answer is cut off mid-sentence ("A review also states that the Beh"), so the final claim is incomplete and not assessable. Its first two paragraphs can still be checked.

Claim 1: DiffTRe's diamon)

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: DiffTRe's examples use DimeNet++, which the paper calls a state-of-the-art graph neural network potential, for the diamond stiffness-tensor case and for the coarse-grained water case [W3168247670#004]. The passages do not directly compare NequIP with DimeNet++ on MD-17. They do report that NequIP outperforms all other methods it was tested against on the revised MD-17 set, including sGDML, FCHL19/GPR, ACE, GAP, ANI, PaiNN and NewtonNet, though PaiNN and NewtonNet are described as lmax = 1-only versions [W4225405705#011]. So the MD-17 comparison with the DimeNet++ family is not stated in the provided text.
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: partial (The answer correctly identifies DimeNet++ for diamond and water, but it says the NequIP vs. DimeNet-family comparison is not stated, whereas the reference says NequIP significantly outperforms invariant GNN potentials such as SchNet and DimeNet on MD-17.)
- support: None (judge returned no valid verdict: {"verdict":"sup)

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: In DiffTRe, the prior potential U_prior is a constant potential that approximates a-priori known properties of the system, such as the Pauli exclusion principle [W3168247670#008]. It is not a Bayesian prior that biases the learnable parameters in the small-data regime [W3168247670#008]. Instead, it serves to control trajectory generation at the start of optimization, and it acts as a physics-informed initialization that speeds up convergence [W3168247670#008][W3168247670#010]. If the prior contradicts the data, the learned model term corrects for it during optimization [W3168247670#008].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: correct (The answer covers the key points: it is not a Bayesian prior, it controls trajectory generation early in training, acts as a physics-informed starting point, and the network overrides it if the data contradicts it; the Pauli exclusion example is consistent with a repulsive term.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

1. U_prior is a constant potential approximating a-priori known properties such as the Pauli exclusion principle. #008 states this directly.
2. It is not a B)

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The passages do not state the total GPU hours used to train the DiffTRe diamond potential. The diamond section [W3168247670#013] describes the DimeNet++ model, the loss, the simulation setup (1000 carbon atoms, 10 ps equilibration, 60 ps production), but gives no GPU hour figure. The other passages cover unrelated models (DTNN, MoleculeNet, and MLIP inference speeds).
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.

