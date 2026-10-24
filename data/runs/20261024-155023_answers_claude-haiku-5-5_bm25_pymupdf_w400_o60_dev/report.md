# Answer eval: claude-haiku-5-5

- **Generator:** `{"name": "claude", "provider": "anthropic", "model": "claude-haiku-5-5", "prompt": "answer-v1"}`
- **Judge:** `{"provider": "anthropic", "model": "claude-haiku-5-5", "prompt": "judge-v1"}`
- **Retrieval:** bm25, top 8 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 bc8e68a22fcc)
- **Cost:** generator $0.000, judge $0.012

_No reference answer, so correctness isn't judged: q007, q008, q009, q010._

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.57 [0.38, 0.75] | 20 |
| Supported by its citations | 0.75 [0.25, 1.00] | 4 |
| Cites your evidence | 0.70 [0.48, 0.87] | 23 |
| Evidence was retrieved | 0.63 [0.44, 0.81] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 25 |
| Declines when unanswerable | 1.00 [1.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.14 [0.03, 0.28] | 29 |

Correct when the evidence was retrieved: 0.83 (n=12)

Correct when no evidence was retrieved: 0.17 (n=6)

## Effort per question (mean)

1.0 model calls, 1.0 tool calls (1.0 searches), 8.0 passages read, 6,186 input tokens, 0.0 s. Gave up on 0%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: The passages do not say which test system Behler and Parrinello used to demonstrate their original neural network potential. They describe the method's energy decomposition into atomic contributions [W4312043350#015] and its atom-centered features [W2988055229#031], but not their validation system. A silicon example appears in a different paper, where a Behler-Parrinello network was trained on DFT data for 64 silicon atoms at three temperatures [W2991697224#016]. That is not the original demonstration, so it cannot answer the question.
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: The original high-dimensional neural network potential (Behler and Parrinello, 2007) uses a piece-wise cosine cutoff. It is fc(Rij) = 0.5[cos(π Rij/Rc) + 1] for Rij ≤ Rc, and 0 for Rij > Rc [W2025444507#004]. The cutoff is written in the same form in the ANI paper, as 0.5 × cos(π Rij/RC) + 0.5 for Rij ≤ RC [W2541404351#007]. The passage text is garbled, so the exact form is reconstructed from the surrounding description.

{"answerable": true, "answer": "The original high-dimensional neural network potential (Behler and Parrinello, 2007) uses a piece-wise cosine cutoff: fc(Rij) = 0.5[cos(π Rij/Rc) + 1] for Rij
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: correct (The answer gives the same cosine cutoff, f_c(R) = 0.5[cos(πR/R_c) + 1] for R ≤ R_c and 0 beyond, that the reference states; the extra ANI remark and the garbled-passage note do not contradict it.)
- support: None (judge returned no valid verdict: )

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: In a high-dimensional neural network potential, the total energy E of the system is represented as a sum of atomic contributions Ei, E = sum over i of Ei [W2025444507#003][W4312043350#015]. Each atomic contribution Ei is produced by a subnet that takes the atom's symmetry function values as input, and summing these contributions yields the total energy [W2025444507#003][W2025444507#005]. This decomposition is also what makes the total energy invariant to interchanging atoms of the same type, since the subnets share identical structure and weights [W2025444507#003][W2025444507#004]. In ANI, the same relation holds, with ET computed as the sum of the atomic outputs Ei [W2541404351#007].
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states the core fact that the total energy is the sum of atomic energies, each produced by an atomic subnet from the atom's local environment (symmetry function inputs), matching the reference, with extra correct detail about invariance and ANI.)
- support: None (judge returned no valid verdict: )

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP's internal features are equivariant to rotations and reflections, so the relevant group is O(3). The network's output energy is invariant under translations, reflections, and rotations [W4225405705#005]. NequIP is described as an E(3)-equivariant model whose internal features are equivariant with respect to the 3D Euclidean group, built using only E(3)-equivariant operations [W4319162181#003].

The internal features are geometric tensors (scalars, vectors, and higher-order tensors), and atoms exchange information through filters that are themselves geometric tensors of increasing order [W4225405705#005]. The passages do not give further detail on how these t
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: None (judge returned no valid verdict: {"verdict": "partial", "reason": "The answer names O(3) as the relevant group, which conflicts)
- support: None (judge returned no valid verdict: )

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: The passages do not mention NequIP, so I cannot say how it handles rotational symmetry. They do describe the Behler-Parrinello approach: atom-centered symmetry functions map coordinates to roto-translationally invariant features, which are fed to a dense network that outputs atomic energies [W2988055229#031][W3000291311#028]. Other passages describe Deep Potential methods that use local reference frames with symmetry-preserving coordinates [W2742127985#002][W2963373387#003], but none compares them with NequIP.
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: NequIP and SchNet share several features, according to the passages:

- **Graph neural network message passing with learned features:** Both are GNN interatomic potentials built from stacked message-passing layers with message and update functions [W4391631778#006]. Both are also implicit, learned-feature (deep learning) MLIPs [W4407925765#013].
- **Two-body message passing with a cutoff:** Both use only two-body message-passing functions, assuming edges lie within the cutoff radius rc [W4391631778#024].
- **Interaction blocks and radial cutoff:** NequIP's
- support: None (judge returned no valid verdict: {"verdict":)

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: The passages do not explicitly describe NequIP's first computational step. The simplified architecture in Figure 2 places an "Embedding" block before the three interaction blocks, and the forward path takes atomic numbers and atomic positions as inputs to predict energy [W4391631778#007]. The first interaction block also omits the communication routines used in the later blocks [W4391631778#007][W4391631778#008]. The passages do not say what the embedding computes. The "first step" text in [W4406405186#018] refers to the ACE framework's one-particle basis, not NequIP.
- support: None (judge returned no valid verdict: )

**q009** (lookup): What datasets is Nequip tested on?
- answer: The passages name several datasets NequIP was run on, but they don't give a complete list.

- **3BPA (flexible drug-like molecule):** NequIP networks were trained at 300 K and tested at 300 K, 600 K and 1,200 K, using the nequip code base [W4406405186#014].
- **DPA-2 pre-training datasets:** NequIP was trained on these with single-task training, with a batch size of 1 for 1 million steps, and its test RMSEs are reported in a table [W4405574099#044]. Among these, the OC2M, Sn and Drug datasets are named. For OC2M, NequIP could not finish data processing on a 155 GB machine, so the dataset was split into 4 subsets [W4405574099#057].
- **MD17:** A different paper cites NequIP parameter-set sizes for neural
- support: None (judge returned no valid verdict: )

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: The original NequIP paper compares NequIP on MD-17 with several groups of models:

- **Invariant GNN-IPs:** SchNet and DimeNet [W4225405705#010]
- **Shallow neural networks:** ANI [W4225405705#010]
- **Kernel-based approaches:** GAP, FCHL19/GPR, and sGDML [W4225405705#010]
- **Other methods:** ACE, SpookyNet, and GemNet [W4225405705#010]
- **Other equivariant neural networks:** PaiNN, NewtonNet, and UNiTE [W4225405705#010]

The paper notes that PaiNN and NewtonNet are lmax = 1-only versions of equivariant networks [W4225405705#010].
- support: None (judge returned no valid verdict: {"verdict": "supported", "reason": "Every model named in the answer's groups (SchNet, DimeNet, ANI, GAP, FCHL19/GPR, sGDML, ACE, SpookyNet, GemNet, PaiNN, NewtonN)

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet takes the interatomic distance d_ij = ||r_i - r_j|| as the filter network input to keep the filters rotationally invariant [W2726670313#009]. It does not feed the raw distance directly: it expands the distance with radial basis functions e_k(r_i - r_j) = exp(-gamma||d_ij - mu_k||^2), with centers 0 Å ≤ mu_k ≤ 30 Å spaced every 0.1 Å and gamma = 10 Å, which adds a non-linearity that decorrelates the initial filters and speeds training [W2726670313#009]. The expanded distances are then fed into two dense layers with softplus activations to compute the filter weight W(r_i - r_j) [W2726670313#009]. The later SchNet paper describes the same filter-generating network as taking the vector from atom i to neighbor j, which is constrained to respect known invariances [W2778051509#007].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: None (judge returned no valid verdict: )
- support: None (judge returned no valid verdict: )

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses a shifted softplus, ssp(x) = ln(0.5e^x + 0.5), as its non-linearity throughout the network. The shift ensures ssp(0) = 0 and improves convergence [W2726670313#010][W2778051509#006]. It matters for force fields because SchNet's forces are obtained by differentiating the energy with respect to atom positions, so the model must be at least twice differentiable to allow gradient descent on the force loss [W2726670313#010]. The function has infinite order of continuity, which gives smooth potential energy surfaces, force fields, and second derivatives [W2778051509#006]. By contrast, the passages note that ReLU-type activations are excluded for this reason, because non-smooth activations cause discontinuities in the forces [W3093149769#039].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (The answer gives the same shifted softplus, ln(0.5e^x + 0.5), with ssp(0)=0 and improved convergence, and explains the smooth, infinitely differentiable energy surface that gives smooth forces and second derivatives, matching the reference.)
- support: None (judge returned no valid verdict: )

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: Ordinary convolutional layers assume the data lie on a regular grid, as image pixels do, but atoms in molecules are not on a grid and can be located at arbitrary positions, so a conventional filter tensor is not applicable [W2778051509#006][W2726670313#006]. Unevenly spaced inputs like atom positions cannot be handled by a grid filter, and re-sampling onto a grid requires an interpolation scheme that is itself a challenge and may need many grid points [W2726670313#006]. The atoms' precise locations carry essential physical information that would be lost if discretized [W2726670313#001]. SchNet therefore uses continuous filters generated by a filter-generating network that maps atom positions to filter values [W2778051509#006][W2726670313#006]. A discrete filter also cannot capture subtle positional changes, leading to discontinuous energy predictions [W2726670313#005].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (It captures the reference's key points: atoms sit at arbitrary positions rather than on a grid, so fixed filters don't apply, and SchNet uses continuous filters produced by a filter-generating network from positional information. The extra detail on interpolation and discontinuities doesn't contradict the reference.)
- support: None (judge returned no valid verdict: )

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of rcut = 5 Å when learning formation energies of bulk crystals from the Materials Project data [W2778051509#014].
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer gives the 5 Å cutoff on Materials Project data, matching the key fact of the reference; it omits the detail about dropping two structures and the QM9/MD17 note, but those are extra detail rather than contradictions.)
- support: supported (The cited passage states that for formation energy prediction on bulk crystals from the Materials Project, 'We set the distance cutoff rcut = 5Å.')

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: The passages say SchNet is designed to reflect energy conservation of its predicted force fields [W2726670313#007], but they do not explicitly describe the mechanism. The only related point is that forces obtained as gradients of the total potential energy are conserved by construction, whereas directly predicted forces are not [W4225405705#004]. That contrast is about other models, so the passages do not confirm that SchNet uses this gradient approach.
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: incorrect (The answer claims the passages do not describe SchNet's mechanism and does not state that forces are the negative gradient of the predicted energy, which is the key fact in the reference answer.)
- support: supported (The answer's claims match the cited passages: SchNet is stated to reflect energy conservation of its force fields, the gradient-based conservation point appears only in the contrast with other models (Townshend et al.), and the passages do not describe SchNet's mechanism.)

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: SchNet's continuous filters see only interatomic distances. Its filters are radial and rotation-invariant, so the features it builds are scalar and invariant [W3093149769#042][W2988055229#033][W2788775653#008]. Angular information is not used directly; it is only captured in SchNet's setting by pairwise distances [W2788775653#008].

NequIP's filters see the full relative position vector. Each filter is a learnable radial function times a spherical harmonic of the unit vector, F(r_ij) = R(r_ij)Y(l)(r_ij hat) [W4225405705#006]. This lets its features be equivariant tensors (scalars, vectors, and higher-order tensors) rather than only invariant scalars, and it lets the filters use angular information [W4225405705#006][W4225405705#003]. Without the higher-order terms, NequIP would reduce to a conventional invariant GNN similar to SchNet [W4225405705#008].
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: correct (The answer matches the reference: SchNet's filters depend only on interatomic distances and yield invariant scalar features, while NequIP's filters also use the neighbor direction via spherical harmonics, giving equivariant tensor features that reduce to a SchNet-like invariant network when restricted to scalars. The extra detail on the filter form and citations does not contradict the reference.)
- support: None (judge returned no valid verdict: )

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: The passages do not include the SchNet paper, so they do not say which kernel method SchNet compared against on MD17. Other papers in the set compare SchNet with kernel methods such as GDML and sGDML [W3003486042#028], but that is not the SchNet paper's own comparison. For NequIP, the paper reports that it significantly outperforms kernel-based approaches such as GAP, FCHL19/GPR and sGDML on MD-17 [W4225405705#010]. A GemNet passage notes that kernel methods are typically more sample efficient than the GNNs it compares against [W4287126984#019].
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: partial (The answer correctly reports that NequIP outperforms kernel methods such as GAP, FCHL19 and sGDML, but it declines to name GDML as the kernel method SchNet compared against, which is the first half of the question and the reference's main fact.)
- support: None (judge returned no valid verdict: )

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: The passages do not contain the SchNet paper's discussion of where atomic-contribution predictions fit poorly. The only SchNet mention is a list of MLIP names and citations [W4407925765#005]. The passages do describe the atomic-sum approach of Behler-Parrinello networks, which sums atomic energies so that the model can be applied to molecules of any size [W2988055229#031], and they note its assumption that each atom's energy depends mainly on its local chemical environment [W3093149769#038]. Neither passage says which properties this approach fits poorly, and neither attributes such a statement to SchNet.
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: The passages do not state the exact flaw in CHARMM36 directly. They say CHARMM36m is a refinement with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000], which implies that CHARMM36 was less accurate for such disordered systems.
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (The answer correctly links CHARMM36m to better modeling of intrinsically disordered proteins and peptides, but it fails to name the specific flaw (overstabilization of compact and left-handed helical structures) and instead says the passages do not state it.)
- support: None (judge returned no valid verdict: )

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The passages only partly answer this. CHARMM36m is described as a refinement of CHARMM36 with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. The passages do not specify which force field parameters or terms were changed, so the exact modifications cannot be identified from them.
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (The answer declines to specify the changes (CMAP backbone refit and modified TIP3P water with stronger LJ on hydrogens), which the reference identifies as the key facts, so it misses the main point.})
- support: supported (The cited abstract states that CHARMM36m is a refinement of CHARMM36 with improved accuracy for polypeptide backbone ensembles of intrinsically disordered peptides and proteins, and the answer's statement that the passage doesn't specify the changed parameters is accurate.)

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: The provided passages do not mention RFdiffusion or its experimental success rate for designing protein binders. They cover topics such as machine learning in materials science, PeSTo binding-interface prediction, DynamicBind ligand docking, and machine learning force fields, so the question cannot be answered from them.
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: The passages do not state a dropout rate for training SchNet. The SchNet passage describes its training setup (SGD with ADAM, 32 molecules per mini-batch, initial learning rate 10^-3 with exponential decay, and an exponential moving average of weights with decay rate 0.99) but does not mention dropout [W2726670313#012]. The other passages discuss dropout in general or in other models, not SchNet.
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: DiffTRe avoids differentiating through the MD simulation. It combines automatic differentiation with MD reweighting schemes and leverages thermodynamic perturbation theory, which is limited to time-independent observables [W3168247670#001][W3168247670#003]. Direct reverse-mode AD instead backpropagates through the whole trajectory, which is memory-hungry and prone to exploding gradients [W3168247670#003][W3168247670#011]. DiffTRe only differentiates through the potential energy computation of decorrelated states [W3168247670#011].

This yields gradient computation about 2 orders of magnitude faster, with exploding gradients avoided and memory requirements comparable to the adjoint method [W3168247670#001][W3168247670#003]. In the toy double-well example, the authors measured a gradient speed-up of 486 and an overall per-update speed-up of 3.7, though they note these values are sensitive to the setup [W3168247670#011]. Because the method is reweighting-based, dynamical properties cannot be used as target observables [W3168247670#019].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: None (judge returned no valid verdict: {"verdict": "correct", "reason": "The answer captures the reference's key points: DiffTRe avoids differentiating through the simulation, combines AD with MD reweighting, is)
- support: None (judge returned no valid verdict: )

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: Reweighting weights are computed as w_i = exp(-β(U_θ(S_i) − U_θ̂(S_i))) normalized by the sum of the same exponential terms over all retained states [W3168247670#005]. They are derived from state probabilities p_θ(S_i) ~ exp(-βH(S_i)), where H is the Hamiltonian (potential plus kinetic energy) and β = 1/(k_B T) [W3168247670#005]. The kinetic energy cancels because it appears identically in the numerator and denominator of the probability ratio p_θ/p_θ̂, so only the potential energy difference remains [W3168247670#005]. For θ = θ̂ the weights reduce to 1/N, recovering the plain time average [W3168247670#005].
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (The answer gives the same weight formula (exponential of -β times the potential energy difference, normalized over all states), explains that kinetic energy cancels in the Boltzmann ratio, and notes that weights reduce to 1/N when θ equals the reference, matching the reference's key facts.)
- support: None (judge returned no valid verdict: )

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe keeps reusing the stored reference trajectory states for reweighting and updates until the effective sample size falls below a predefined threshold: as soon as Neff < N̄eff, a new reference trajectory is sampled using the current θ as the new reference parameters [W3168247670#007]. Equivalently, the new trajectory is generated when the statistical error from reweighting is no longer acceptably small [W3168247670#006]. The new trajectory starts from the last generated state S_N [W3168247670#007].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (The answer matches the reference: DiffTRe switches to a new reference trajectory when the effective sample size drops below a threshold (so reweighting error becomes too large), and the new trajectory starts from the last state of the old one; citations are ignored as instructed.)
- support: None (judge returned no valid verdict: {"verdict": "supported", "reason": "Passage 007 states that reweighting repeats until Neff falls below the predefined threshold, then a new reference trajectory is sampled with the current θ as the ne)

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The DiffTRe diamond potential (a DimeNet++ model) was trained on experimental elastic stiffness tensor data for diamond. The loss used three distinct stiffness moduli, C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa (Voigt notation), together with the assumption of a stress-free state at zero strain [W3168247670#013]. The simulation temperature (298.15 K) and density (3512 kg/m3) were also taken from experimental values [W3168247670#013].
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer identifies the experimental elastic stiffness tensor of diamond with C11 = 1079 GPa, C12 = 124 GPa, C44 = 578 GPa and the stress-free zero-strain condition, matching the reference; the extra details on temperature and density are consistent additions rather than contradictions.)
- support: None (judge returned no valid verdict: {"verdict": "supported", "reason": "The cited passage states the DimeNet++ potential was learned from experimental elastic stiffness data with the three moduli C11, C)

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: The learned coarse-grained water model got the **self-diffusion coefficient D** wrong. It predicted D = 10.91 μm²/ms, while the experimental value is D̃ = 2.2 μm²/ms, so it is too large [W3168247670#017].

The passages offer these explanations:
- CG models generally show accelerated dynamics compared with atomistic models because their potential energy surfaces are smoother [W3168247670#017].
- For CG water models, diffusion coefficients decrease as the number of interaction sites increases [W3168247670#017].
- The authors suggest the model may act like a single-site model early in optimization, and the decreasing diffusion during training may reflect it becoming more like a multi-site model as it learns 3-body interactions. This is presented as a possibility, not a confirmed cause [W3168247670#017].

For comparison, a single-site tabulated potential from iterative Boltzmann inversion with pressure correction gave D = 14.15 μm²/ms under the same setup [W3168247670#017]. The model did match the experimental tetrahedral order parameter closely (q ≈ 0.569 vs. 0.576) [W3168247670#017].
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (The answer identifies the self-diffusion coefficient as the wrong property (10.91 vs 2.2 μm²/ms, too fast), attributes it to smoother energy surfaces accelerating CG dynamics, and notes the tetrahedral order parameter matched well, all consistent with the reference.)
- support: None (judge returned no valid verdict: )

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: {"answerable": false, "answer": "The passages do not say whether DiffTRe can be used to fit a potential to a measured diffusion coefficient. In the DiffTRe paper, the targets were experimental oxygen RDF, ADF and pressure, and the self-diffusion coefficient was a held-out observ
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: incorrect (The answer declines to answer by saying the passages don't specify, whereas the reference clearly answers 'No' because DiffTRe's reweighting ignores temporal order so dynamical properties like diffusion coefficients cannot be targets.)
- support: unsupported (no passages cited)

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: The DiffTRe authors see the main obstacle in bottom-up training of neural network potentials as the limited availability of highly precise and sufficiently broad datasets, which becomes intractable for larger systems where quantum calculations are too costly [W3168247670#003]. The SchNet C20 model relied on this approach: its reference data came from classical MD run with DFT (PBE+vdW-TS) [W2778051509#019]. Instead, DiffTRe uses a top-down approach that trains on experimental data. Examples include a DimeNet++ model for diamond fitted to its experimental stiffness tensor, and a coarse-grained water model fitted to pressure and radial and angular distribution functions [W3168247670#003].
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: None (judge returned no valid verdict: {"verdict": "partial", "reason": "It correctly identifies the lim)
- support: None (judge returned no valid verdict: )

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: The passages do not mention DiffTRe or the empirical potential its diamond model starts from, so I cannot name that potential. They do mention carbon as a test system for neural network potentials: Behler and Parrinello's approach was applied to carbon [W2968923792#056], and early ML studies of carbon allotropes, including the graphite-diamond coexistence line and diamond nucleation in graphite, used a neural-network potential [W3189164715#120]. Those passages do not link this to DiffTRe, so the specific paper cannot be identified from them.
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: incorrect (declined to answer although the corpus has the answer)

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: The passages do not state which graph neural network DiffTRe uses as its learnable potential, so that part cannot be answered from them. On MD-17, NequIP is reported to improve on state-of-the-art accuracy and to significantly outperform invariant GNN interatomic potentials such as SchNet and DimeNet [W4225405705#010]. On the revised MD-17 data set, the authors report that NequIP outperforms all other methods compared [W4225405705#011].
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: partial (The answer fails to identify DimeNet++ as DiffTRe's learnable potential, claiming the passages don't say, which contradicts the reference's key fact, though its NequIP comparison to SchNet and DimeNet on MD-17 matches the reference.)
- support: None (judge returned no valid verdict: {"verdict": "supported", "reason": "Each substantive claim is stated in the cited passages: #010 says NequIP improves on state-of-the-art MD-17 accuracy and significantly outperforms invariant GNN pot)

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: The prior potential U_prior is a constant potential that approximates a-priori known properties of the system, such as the Pauli exclusion principle [W3168247670#008]. It is not a Bayesian prior that biases learnable parameters in the small-data regime [W3168247670#008]. Its purpose is to control trajectory generation at the start of optimization, and it acts as a physics-informed initialization that speeds up convergence [W3168247670#008][W3168247670#010]. If it contradicts the data, the learned model term U_model corrects for it during optimization [W3168247670#008].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: None (judge returned no valid verdict: )
- support: None (judge returned no valid verdict: )

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The passages do not report the GPU hours needed to train the DiffTRe diamond potential. They say only that DiffTRe trains a DimeNet++ model for diamond from its experimental stiffness tensor [W3168247670#004] and that it reduces gradient computation effort by about two orders of magnitude compared with backpropagation through the simulation [W3168247670#003]. No total GPU time is given.
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.

