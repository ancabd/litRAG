# Answer eval: extractive

- **Generator:** `{"name": "extractive", "min_overlap": 2}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1"}`
- **Retrieval:** bm25, top 5 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 487184e30344)
- **Cost:** generator $0.000, judge $0.146

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.12 [0.03, 0.22] | 29 |
| Supported by its citations | 1.00 [1.00, 1.00] | 29 |
| Cites your evidence | 0.22 [0.07, 0.41] | 27 |
| Evidence was retrieved | 0.59 [0.41, 0.78] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 29 |
| Declines when unanswerable | 0.00 [0.00, 0.00] | 3 |
| Declines although answerable (lower is better) | 0.00 [0.00, 0.00] | 29 |

Correct when the evidence was retrieved: 0.22 (n=16)

Correct when no evidence was retrieved: 0.00 (n=11)

## Effort per question (mean)

0.0 model calls, 1.0 tool calls (1.0 searches), 5.0 passages read, 0 input tokens, 0.0 s. Gave up on 0%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: To create our neural network potential we can write init_fn, energy_fn = energy.behler_parrinello(d) or init_fn, energy_fn = energy.graph_network(d) which uses Haiku [61] to construct the energy model. [W2991697224#016]
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: incorrect (The answer only shows code for building a neural network potential in a library and never names bulk silicon as the test system, so it does not address the question.)
- support: supported (The answer reproduces the passage's sentence nearly verbatim, including both energy function calls and the Haiku reference.)

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: Heavily modified Behler and Parrinello symmetry functions25 (BPSF) and their high-dimensional neural network potential model, depicted in Figure 1, form a base for our ANAKIN-ME (ANI) model. [W2541404351#007]
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: incorrect (The answer never gives the functional form of the cutoff function and only mentions that the ANI model is based on Behler-Parrinello symmetry functions, so it misses the reference's cosine cutoff.)
- support: supported (The cited passage opens with this exact sentence, so the claim is stated directly.)

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: High-dimensional neural network potentials established the second generation and are based on three key steps: first, the expression of the total energy as a sum of environment-dependent atomic energy contributions; second, the description of the atomic environments by atom-centered symmetry functions as descriptors fulfilling the requirements of rotational, translational, and permutation invariance; and third, the iterative construction of the reference electronic structure data sets by active learning. [W3141927472#000]
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states the total energy is a sum of environment-dependent atomic energy contributions, matching the reference's key point, though it omits the per-atom neural network and cutoff details and adds extra correct context.)
- support: supported (The answer is a near-verbatim copy of the abstract's sentence on second-generation HDNNPs and their three key steps.)

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: A key innovation of the Cormorant network20, tensor-field networks21 and steerable 3D convolutional neural networks (CNNs)22 was to create equivariant internal features that transform (under the symmetry operations of the input) like the irreducible representations of the symmetry group and construct invariants only at the very last step. [W4406405186#002]
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: incorrect (The answer describes Cormorant, tensor-field networks and steerable CNNs in general terms and never says NequIP is E(3)-equivariant, nor that its features are built from tensor products with spherical harmonics of relative position vectors.)
- support: supported (The cited passage states this claim almost verbatim, including the Cormorant, tensor-field and steerable 3D CNN attribution and the construction of invariants only at the last step.)

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: The Behler-Parrinello neural network potentials (NNPs)[1–3] express the potential energy surface (PES) in terms of the atom-centered symmetry functions (ACSF)[4] using fully- connected feed-forward neural networks. [W3000291311#028]
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: incorrect (The answer only describes Behler-Parrinello's use of atom-centered symmetry functions and never addresses NequIP's equivariant message-passing features or how the two approaches differ in handling rotational symmetry.)
- support: supported (The answer is a verbatim copy of the first sentence of the cited passage, so every claim is stated there.)

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: Assuming edges are connected within rc, this implies that GNN-IP models using only two-body message- passing functions, such as SchNet,23 PhysNet,18 PaiNN,40 NequIP,15 and MACE,32 can be parallelized using our approach by adapting atomic force computations to each architecture. [W4391631778#024]
- reference: Several design choices come from SchNet. The initial atom features are a trainable embedding of the atomic number (one-hot encoded). Atoms then pass through a stack of interaction blocks that do continuous convolutions over neighbors within a cutoff. In those convolutions the learnable filter weights are an MLP of the interatomic distance expanded in a radial basis: Gaussians in SchNet, Bessel functions with an envelope in NequIP. The output is per-atom energies summed to a total energy, and forces are its negative gradient. The difference is that NequIP also multiplies the radial part by spherical harmonics of the bond direction. If only l = 0 (scalar) features are kept, NequIP reduces to a SchNet-style invariant network.
- correctness: incorrect (The answer only says that SchNet, NequIP and others use two-body message passing within a cutoff and can be parallelized, and does not identify the shared features (atomic-number embedding, continuous convolutions with radial-basis MLP filters, summed per-atom energies with forces as gradients, l=0 reduction).)
- support: supported (The cited passage states this claim nearly verbatim, including the list of models and the condition about edges within rc.)

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: We utilize NequIP as the foundational GNN-IP architecture for SevenNet and implement our parallelization algorithm, to be discussed in the following section. [W4391631778#007]
- reference: It embeds each atom's chemical species. The atomic number Z_i, one-hot encoded, goes through a trainable self-interaction (linear) layer. This gives the initial per-atom features, which are scalar (l = 0) only. The embedding follows SchNet. Higher-order tensor features first appear in the interaction blocks.
- correctness: incorrect (The answer does not describe the embedding step (one-hot atomic number through a linear self-interaction layer) and instead talks about using NequIP as the base for SevenNet, which does not address the question.)
- support: supported (The answer reproduces a sentence from the cited passage almost verbatim, stating that NequIP is the foundational GNN-IP architecture for SevenNet and that the parallelization algorithm is implemented on it.)

**q009** (lookup): What datasets is Nequip tested on?
- answer: We have tested this DPA-2 model on the 6 test datasets provided in the Ref. [W4405574099#044]
- reference: 1) MD-17 small organic molecules, both the original DFT version and the revised MD-17 (rMD17). 2) Small molecules at quantum-chemical accuracy: aspirin at CCSD; benzene, malonaldehyde, toluene and
   ethanol at CCSD(T).
3) Periodic systems:
   - liquid water and ice
   - a chemical reaction at a solid/gas interface (formate decomposition on a copper surface)
   - amorphous lithium phosphate (Li4P2O7)
   - a lithium superionic conductor (Li6.75P3S11, "LiPS")
- correctness: incorrect (The answer talks about a DPA-2 model and unnamed '6 test datasets' and does not list any of the NequIP datasets (MD-17/rMD17, CCSD(T) molecules, water/ice, formate on Cu, LiPO, LiPS).)
- support: supported (The cited passage states that the DPA-2 model was tested on the 6 test datasets provided in Ref. [11] (ANI-MD, DrugBank, GDB07-09, GDB10-13, S66x8, Tripeptide); the answer's paraphrase matches this, though it cites the passage ID in place of Ref. [11].)

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: Importantly, we train and test separate NequIP models on both the original and the revised MD-17 data set, and find that NequIP obtains significantly lower energy errors on the revised data set, while the force accuracy is similar on the two data sets. [W4225405705#011]
- reference: Invariant GNN potentials: SchNet and DimeNet. A shallow neural network: ANI. Kernel methods: GAP, FCHL19/GPR and sGDML. Other methods: ACE, SpookyNet and GemNet. Other equivariant networks: PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are restricted to l_max = 1. Results for ACE, GAP and ANI on revised MD-17 are taken from another paper (Kovács et al.), not retrained by the authors. NequIP reports the best accuracy of all of them.
- correctness: incorrect (The answer does not list any comparison models and only discusses NequIP's results on the original vs revised MD-17 data, so it misses the reference's main point.)
- support: supported (The answer reproduces the cited passage nearly verbatim, and every claim in it is stated there.)

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: The rotational invariance is obtained by using interatomic distances dij = ∥ri −rj∥ as input for the filter network. [W2726670313#009]
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: incorrect (The answer only says interatomic distances are used as input for rotational invariance and omits the Gaussian basis expansion, the grid of centers, and the gamma and spacing values that the reference gives.)
- support: supported (The passage states verbatim that rotational invariance is obtained by using interatomic distances dij = ∥ri −rj∥ as input for the filter network.)

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: We have presented SchNet as such a versatile deep learning architecture for quantum chemistry and a valuable tool in a variety of applications ranging from the property prediction for diverse datasets of molecules and materials to the highly accurate prediction of potential energy surfaces and energy-conserving force fields. [W2778051509#022]
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: incorrect (The answer never names the shifted softplus activation or explains why smoothness and differentiability matter for forces; it only gives a generic statement about SchNet's applications.)
- support: supported (The answer is a near-verbatim sentence from the cited conclusions passage, so every claim in it is stated there.)

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: This generalization is necessary since atoms are not located on a regular grid like image pixels, but can be located at arbitrary positions. [W2778051509#006]
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: partial (It correctly says atoms sit at arbitrary positions rather than on a regular grid, but it omits that a fixed filter tensor can't be used and that SchNet's continuous-filter convolutions generate filters from relative positions.)
- support: supported (The cited passage states verbatim that this generalization is necessary because atoms are not on a regular grid like image pixels but can be at arbitrary positions.)

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: We employ SchNet to predict formation energies for bulk crystals using 69,640 structures and reference calculations from the Materials Project (MP) repository58,59. [W2778051509#014]
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: incorrect (The answer never states the cutoff radius (5 Angstrom), only describing the dataset, so it fails to answer the question.)
- support: supported (The answer restates the passage's first sentence verbatim, and every claim in it is stated in the cited passage.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: The predicted forces are not guaranteed by construction to conserve energy since they are not obtained as gradients of the total potential energy. [W4225405705#004]
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: incorrect (The answer claims forces are not derived as gradients of the energy, which directly contradicts the reference that forces are the negative gradient of the predicted energy, ensuring energy conservation.)
- support: supported (The answer reproduces the passage's statement that directly predicted forces are not guaranteed to conserve energy because they are not gradients of the total potential energy.)

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: Since the initial atom embeddings are obviously equivariant to the order of atoms, atom-wise layers are independently applied to each atom and continuous-filter convolutions sum over all neighboring atoms, indexing equivariance is retained in the atom-wise representations. [W2778051509#010]
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: incorrect (The answer discusses permutation equivariance over atom indexing and never says what the filters see (distances only for SchNet, distances plus direction for NequIP) or how that affects features (invariant scalars vs equivariant tensors).)
- support: supported (The answer restates the cited passage's sentence nearly verbatim, and each claim appears in it.)

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: We compare OQML and GPR models based on FCHL19 to OQML models based on FCHL18.1,22 In addition, we compare to GDML28 and sGDML29 which are two state-of-the-art kernel-based methods closely related to GPR. [W3003486042#028]
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: partial (The answer names GDML and sGDML as kernel methods and mentions FCHL, but it never states that SchNet compared against GDML, and it does not say how NequIP performs against kernel methods (that it outperforms them).)
- support: supported (The answer's sentence is copied almost word for word from the cited passage, so all of its claims are stated there.)

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: Accurate NeurAl networK engINe for Molecular Energies (ANAKIN-ME, ANI for short): [12] Allegro: [13] Atomic Cluster Expansion (ACE): [14] Atomic Energy Network (ænet): [15,16] Atomistic Line Graph Neural Network-based Force Field (ALIGNN-FF): [17] Atoms-In-Molecules Network 2 (AIMNet2): [18] Behler-Parrinello Neural Network (BP-NN, or BP)[19] Crystal Hamiltonian Graph Neural Network (CHGNet)[20] Deep Molecular Dynamics (DeepMD): [21,22] Elemental Spatial Density Neural Network Force Field (Elemental-SDNNFF): [23] EquiformerV2-OMAT24: [24] Fast Learning of Atomistic Rare Events (FLARE): [25] Gaussian Approximation Potential (GAP): [26] Graph-based Pre-trained Transformer Force Field (GPTFF): [27] Graph Networks for Materials Exploration (GNoME): [28] Graph Atomic Cluster Expansion (grACE): [29] Mattersim: [30] ACE with message passing (MACE): [31] MACE foundation model (MACE-MP-0): [32] MACE-OFF23 potential for organics (MACE-OFF23): [33] Moment Tensor Potential (MTP): [34] Neural Equivariant Interatomic Potential (NequIP): [35] Orb: [36] PreFerred Potential (PFP): [37] Scalable EquiVariance-Enabled Neural NETwork (SevenNet): [38] SchNet: [39] Spectral Neighbor Analysis Potential (SNAP): [40] Three-body Materials Graph Network (M3GNet): [41] Ultra-Fast Force Fields (UF3) potential: [42] [W4407925765#005]
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: incorrect (The answer is just a list of potential names and citations; it never mentions polarizability or the electronic spatial extent <R^2>, so it does not answer the question.)
- support: supported (The answer is a verbatim copy of the list in the cited passage, with no added claims.)

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: Simply multiplying a switch to the attention maps does not fix the problem. [W4405574099#032]
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: incorrect (The answer is unrelated to the question; it mentions attention maps and does not say that CHARMM36 overstabilized compact and left-handed helical structures in disordered proteins.)
- support: supported (The cited passage states verbatim that simply multiplying a switch to the attention maps does not fix the discontinuity problem of the softmax.)

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The all-atom additive CHARMM36 protein force field is widely used in molecular modeling and simulations. [W2555870966#000]
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (The answer only states that CHARMM36 is a widely used protein force field and never says which parts changed (CMAP backbone refit, modified TIP3P water), so it fails to address the question.)
- support: supported (The cited abstract states verbatim that the all-atom additive CHARMM36 protein force field is widely used in molecular modeling and simulations.)

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: Out of 20 complexes composed by 40 constituent subunits and relative interfaces, the model has a perfect recovery rate for 16 interfaces when applied straightaway on the experimental structures of the unbound subunits. [W4366279959#006]
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: When a similar randomization procedure is applied to the prediction procedure as well, the methodology becomes Monte-Carlo dropout [336]. [W3208687975#062]
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: We present the Differentiable Trajectory Reweighting (DiffTRe) method, which bypasses differentiation through the MD simulation for time-independent observables. [W3168247670#001]
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: partial (It correctly says DiffTRe bypasses differentiating through the MD simulation for time-independent observables, but it omits the reweighting mechanism and the benefits (no exploding gradients, ~100x faster, memory similar to the adjoint method).)
- support: supported (The abstract states directly that DiffTRe bypasses differentiation through the MD simulation for time-independent observables.)

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: (3) allows computing weights as a function of θ (the kinetic energy cancels) wi = e−β(Uθ(Si)−U ˆθ(Si)) N i=j e−β(Uθ(Sj)−U ˆθ(Sj)) . [W3168247670#005]
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: partial (The formula is correct (normalized Boltzmann ratio of potential energy differences, with U_θ̂ as the reference), and it says kinetic energy cancels, but it gives no reason why (same under both potentials) and omits that θ = θ̂ gives uniform weights 1/N.)
- support: supported (The answer reproduces the passage's statement and Eq. (4) almost verbatim, including the kinetic energy cancellation.)

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: We measure speed-ups of sg = 486 for gradient computations and s = 3.7 as overall speed-up per update when a new reference trajectory is sampled. [W3168247670#011]
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: incorrect (The answer reports speed-up figures and never says that a new trajectory is triggered when the effective sample size N_eff falls below a threshold, so it does not address the question.)
- support: supported (The answer reproduces the passage's sentence verbatim: speed-ups of sg = 486 for gradient computations and s = 3.7 overall per update when a new reference trajectory is sampled.)

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: Addressing the call for NN potentials trained on experimental data [1], we propose the Differentiable Trajectory Reweighting (DiffTRe) method. [W3168247670#003]
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: incorrect (The answer never identifies the training data (the experimental elastic stiffness constants of diamond, C11, C12, C44, with a zero-strain stress-free target) and only restates that DiffTRe trains on experimental data.)
- support: supported (The passage contains this sentence nearly verbatim, so the claim is directly stated.)

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: The learning process is robust to weak choices of Uprior: DiffTRe is able to converge to the same prediction quality as with the reference prior even if σR is misestimated by ±0.1 nm (approximately ±30%) compared to the classical SPC water model (Supplementary Fig. [W3168247670#017]
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: incorrect (The answer discusses robustness to the choice of prior (σR misestimation) and never names the self-diffusion coefficient as the property the model got wrong or explains the too-fast dynamics from smoother coarse-grained energy surfaces.)
- support: supported (The cited passage states the claim nearly verbatim, including robustness to weak Uprior choices, convergence to the same prediction quality, the ±0.1 nm (~±30%) misestimation of σR, and the SPC reference.)

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: To further verify and understand the physical effects of the top-down fine-tuning process from the microscopic perspective, we compare the refined potential with the CCSD(T)/complete basis set (CBS) calculation results 0 25 50 75 100 Loop 0 2 4 6 8 Density Diffusion coefficient 0.55 0.60 0.65 0.70 0.75 0.80 0 25 50 75 100 Loop 0 1 2 3 4 5 6 a IR spectrum Density Diffusion coefficient 0.10 0.15 0.20 0.25 0.30 0.35 0.40 Initial Fit(den) Fit(IR+den) 1.00 1.02 1.04 1.06 1.08 b Exp 0 1000 2000 3000 4000 Wavenumber (cm−1) 0 5 10 15 20 c d Initial Fit(den) Fit(IR+den) Exp [W4406553977#018]
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: incorrect (The answer is unrelated text with figure fragments and never says whether DiffTRe can fit a diffusion coefficient, missing the reference's point that reweighting ignores time ordering so dynamical properties can't be targets.)
- support: supported (The answer reproduces the passage's text, including the CCSD(T)/CBS comparison sentence and the figure axis labels, so every claim appears in the cited passage.)

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: By training SchNet on DFT data at the PBE+vdWTS level, we reduce the computation time per single point by three orders of magnitude from 11s using 32 CPU cores to 10ms using one NVIDIA GTX1080. [W2778051509#019]
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: incorrect (The answer only states a computational speedup for SchNet on DFT data; it never names the limitation (limited availability of quantum data and accuracy capped by the reference method) or says DiffTRe trains top-down on experimental observables.)
- support: supported (The cited passage states this claim almost verbatim, including the PBE+vdWTS level, three orders of magnitude, 11s on 32 CPU cores, and 10ms on one NVIDIA GTX1080.)

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: For example, early ML-driven atomistic simulation studies of carbon allotropes were concerned with the description of the graphite–diamond coexistence line116 and, subsequently, with the nucleation mechanism of diamond in graphite under compression.117 These studies have been carried out with a neural-network potential following ref 66. [W3189164715#120]
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: incorrect (The answer never names the Stillinger-Weber potential or silicon, and it does not identify the Behler-Parrinello silicon paper; it talks about carbon allotropes and graphite-diamond studies instead.)
- support: supported (The cited passage contains the answer's sentences nearly verbatim, including the graphite–diamond coexistence line, diamond nucleation in graphite under compression, and the neural-network potential following ref 66.)

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: Learning Curve Experiments For learning curve experiments on the aspirin molecule in MD-17, a series of NequIP models with increasing order l ∈{0, 1, 2, 3} were trained on varying data set sizes. [W4225405705#027]
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: incorrect (The answer never names DimeNet++ as DiffTRe's potential and never says NequIP outperforms invariant models like SchNet and DimeNet, so it does not address either part of the question.)
- support: supported (The passage states this nearly verbatim: learning curve experiments on aspirin in MD-17 with NequIP models of order l ∈ {0,1,2,3} trained on varying data set sizes.)

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: Augmenting NN potentials with a prior is common in the bottom-up coarse-graining literature [8,10] to provide qualitatively correct behavior in regions of the potential energy surface (PES) not contained in the data set, but reachable by the CG model. [W3168247670#008]
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: partial (The answer gives one role of the prior (physically sensible behavior in regions not covered by data), which loosely matches the reference's point about steering visited configurations, but it omits the physics-informed starting point with the network learning a correction, and that the network can override the prior.)
- support: supported (The answer is a near-verbatim restatement of a sentence in the cited passage, so every claim is stated there.)

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: Second, we train the state-of-the-art graph neural network potential DimeNet++ [11, 12] for an atomistic model of diamond from its experimental stiffness tensor. [W3168247670#004]
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.

