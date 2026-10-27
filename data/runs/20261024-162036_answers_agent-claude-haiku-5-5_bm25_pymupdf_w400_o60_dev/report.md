# Answer eval: claude-haiku-5-5

- **Generator:** `{"name": "agent", "provider": "anthropic", "model": "claude-haiku-5-5", "prompt": "agent-v2", "tools": ["search", "read_around", "open_paper"], "max_turns": 8, "token_budget": 100000}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1"}`
- **Retrieval:** bm25, top 8 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 487184e30344)
- **Cost:** generator $0.066, judge $0.299

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.89 [0.80, 0.98] | 28 |
| Supported by its citations | 0.95 [0.85, 1.00] | 10 |
| Cites your evidence | 0.85 [0.70, 0.96] | 27 |
| Evidence was retrieved | 0.85 [0.70, 0.96] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 29 |
| Declines when unanswerable | 1.00 [1.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.00 [0.00, 0.00] | 29 |

Correct when the evidence was retrieved: 0.96 (n=23)

Correct when no evidence was retrieved: 0.83 (n=3)

## Effort per question (mean)

2.8 model calls, 2.9 tool calls (2.8 searches), 15.4 passages read, 24,084 input tokens, $0.0021 per question, 5.1 s. Gave up on 9%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: Behler and Parrinello demonstrated their neural network potential on bulk silicon. They applied the method to bulk silicon and compared it with empirical potentials and DFT [W2025444507#000]. The test set was about 9000 DFT energies, with 8200 used for optimization and 800 as an independent test set [W2025444507#007]. Their checks included the energy-volume curves of the silicon crystal phases and the radial distribution function of a 3000 K silicon melt in a 64-atom cell [W2025444507#007].
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: correct (The answer identifies bulk silicon as the test system and notes comparison with DFT, matching the reference; the extra details on dataset size and checks do not contradict it.)
- support: None (judge returned no valid verdict: Checking claims: (1) Demonstrated on bulk silicon, compared with empirical potentials and DFT — supported by #000. (2) About 9000 DFT energies, 8200 for optimization, 800 as independent test set — sup)
- steps: search "Behler Parrinello neural network potential test system" (5 passages, 5 new); search "high-dimensional neural network potential silicon bulk test" (5 passages, 5 new); answer

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: The original high-dimensional neural network potential (Behler and Parrinello, 2007) uses a cosine cutoff. The function is f_c(R_ij) = 0.5 × [cos(π R_ij / R_c) + 1] for R_ij ≤ R_c, and 0 for R_ij > R_c, so it goes smoothly to zero at the cutoff radius R_c [W2025444507#004]. The paper states that at separations beyond R_c the function gives zero value and slope [W2025444507#005]. The formula text in the extracted passage is garbled, so the form above is reconstructed from the passage and matches the standard expression in later papers [W3000291311#028].
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: correct (The answer gives the same cosine cutoff, f_c = 0.5[cos(πR/R_c)+1] for R ≤ R_c and 0 beyond, matching the reference.)
- support: supported (The cosine cutoff form, the zero value and slope beyond R_c, the garbled formula in the 2007 passage, and the matching standard form in the 2020 paper are all stated in the cited passages.)
- steps: search "cutoff function high-dimensional neural network potential" (8 passages, 8 new); search "Behler-Parrinello symmetry functions cutoff function smooth decay to zero" (8 passages, 8 new); answer

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: The total energy in a high-dimensional neural network potential (HDNNP) is expressed as a sum of atomic contributions: E = Σ_i E_i, where the sum runs over all N atoms and each E_i is the energy contribution of atom i, predicted by a neural network (subnet) fed with that atom's local, atom-centred symmetry-function descriptors [W2025444507#003][W4312043350#015]. The subnets are constrained to share the same structure and weights for atoms of the same element, which keeps the total energy invariant to swapping identical atoms [W2025444507#003]. In the ANI variant, the same sum is used, with one atomic-number-specific network per element [W2541404351#007].
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states that total energy is the sum of atomic energies, each predicted by an atomic NN from the atom's local environment (symmetry-function descriptors), consistent with the reference; extra details on weight sharing are correct.)
- support: None (judge returned no valid verdict: )

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP is equivariant under E(3), the group of rotations, reflections, and translations in 3D space [W4225405705#005]. Its internal features are geometric tensors (scalars, vectors, and higher-order tensors) [W4225405705#005]. They are built in each convolution by combining a radial function of interatomic distances with the spherical-harmonic projection of the unit vector r̂ij through a tensor product, which uses Clebsch-Gordan coefficients [W4225405705#007][W4225405705#009]. Only the rotationally invariant radial function carries learnable filter weights, and the final output (the total energy) is invariant [W4225405705#005][W4225405705#007].
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: correct (The answer gives E(3), geometric tensor features, and tensor products with spherical harmonics of relative position vectors; it omits the explicit O(3) irreps indexing but the content is consistent with the reference.)
- support: None (judge returned no valid verdict: )

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: Behler-Parrinello symmetry functions enforce rotational invariance by construction: they are fixed functions of interatomic distances and angles that "exhibit translational, rotational, and same-element-permutation invariance" [W2976347420#003][W3000291311#028]. Because these fingerprints contain no directional information, they can only regress rotation-invariant quantities like energy, and forces must be obtained by differentiating the energy [W2976347420#003].

NequIP instead keeps rotation as an equivariance constraint on internal features. Each atom carries scalar, vector and higher-order tensor features, and the network's internal features are geometric tensors that transform with rotations and reflections. Only the predicted total energy is invariant [W4225405705#005][W4225405705#006]. Its convolution filters are built from learnable radial functions multiplied by spherical harmonics, and features are combined with Clebsch-Gordan tensor products, so each interaction is equivariant [W4225405705#007][W4225405705#008]. Forces are then obtained as negative gradients of the energy, which keeps them rotation-equivariant [W4225405705#009].
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: correct (The answer captures the key points: BP uses fixed hand-designed invariant descriptors, while NequIP uses equivariant vector/tensor features through message passing with only the final energy invariant; extra details are accurate.)
- support: supported (Every claim in the answer is stated in the cited passages: B-P invariance and energy-then-differentiate forces (W2976347420#003, W3000291311#028), NequIP's scalar/vector/tensor features and invariant energy (W4225405705#005/006), radial-times-spherical-harmonic filters and Clebsch-Gordan products (#006–#008), and forces as negative energy gradients that stay rotation-equivariant (#009).)
- steps: search "NequIP E(3) equivariant rotational symmetry" (8 passages, 8 new); search "Behler-Parrinello symmetry functions rotation invariant" (8 passages, 8 new); search "NequIP equivariant convolution spherical harmonics tensor product features irreducible representations" (8 passages, 7 new); answer

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: NequIP and SchNet share several core design elements, though NequIP adds equivariant tensor features that SchNet does not have.

- **Radial filters from interatomic distances:** NequIP's convolution filters use a learnable radial function R(r_ij) built from a basis expansion of the distance, implemented as a small MLP [W4225405705#007]. SchNet also feeds an expanded distance (radial basis functions) into a filter-generating network to compute its filter weights [W2726670313#009].
- **Rotational invariance of the radial part:** NequIP's learnable weights lie in the rotationally invariant radial function [W4225405705#007], and SchNet restricts its filters to be rotationally invariant by using interatomic distances as filter input [W2726670313#009].
- **Energy as a sum of atomic contributions with forces from gradients:** NequIP sums per-atom scalar outputs into the total energy and obtains forces as the negative gradient via automatic differentiation [W4225405705#029]. SchNet likewise yields energy-conserving force predictions, and its architecture reflects energy conservation of the predicted force fields [W2726670313#007].
- **Scalar-only convolutions as a special case:** The NequIP authors note that keeping only the scalar (0⊗0→0) interaction gives a conventional invariant GNN potential "similar to e.g. SchNet" [W4225405705#007].

The main difference is that NequIP uses features that are vectors and higher-order tensors, combined through Clebsch-Gordan tensor products, to make its internal features equivariant [W4225405705#006][W4225405705#007].
- reference: Several design choices come from SchNet. The initial atom features are a trainable embedding of the atomic number (one-hot encoded). Atoms then pass through a stack of interaction blocks that do continuous convolutions over neighbors within a cutoff. In those convolutions the learnable filter weights are an MLP of the interatomic distance expanded in a radial basis: Gaussians in SchNet, Bessel functions with an envelope in NequIP. The output is per-atom energies summed to a total energy, and forces are its negative gradient. The difference is that NequIP also multiplies the radial part by spherical harmonics of the bond direction. If only l = 0 (scalar) features are kept, NequIP reduces to a SchNet-style invariant network.
- correctness: partial (It correctly covers distance-based MLP radial filters, energy as a sum of atomic contributions with forces as gradients, and the scalar-only reduction to SchNet, but it omits the one-hot atomic-number embedding for initial features and the stack of interaction blocks with continuous convolutions over neighbors within a cutoff.)
- support: None (judge returned no valid verdict: )
- steps: search "NequIP equivariant interatomic potential" (5 passages, 5 new); search "SchNet continuous-filter convolutional neural network" (5 passages, 5 new); search "radial basis functions cutoff network filter distance message passing" (5 passages, 5 new); search "radial basis cutoff filter-generating network interaction block atom-wise" (5 passages, 2 new); answer

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: Nequip's first step is an atomic embedding. The NequIP architecture is built on an atomic embedding, followed by a series of interaction blocks and then an output block. The embedding is a trainable embedding that operates on the atomic number Z_i (one-hot encoded) alone, implemented via a trainable self-interaction layer [W4225405705#009]. Its initial features come from this embedding, and the interaction blocks follow it [W4225405705#009].
- reference: It embeds each atom's chemical species. The atomic number Z_i, one-hot encoded, goes through a trainable self-interaction (linear) layer. This gives the initial per-atom features, which are scalar (l = 0) only. The embedding follows SchNet. Higher-order tensor features first appear in the interaction blocks.
- correctness: partial (It correctly identifies the atomic embedding of one-hot Z_i through a trainable self-interaction layer, but omits that the initial features are scalar (l=0) only, that the embedding follows SchNet, and that higher-order tensor features first appear in the interaction blocks.)
- support: supported (The passage states the architecture is built on an atomic embedding followed by interaction blocks and an output block, and that the embedding is trainable, operates on one-hot atomic number Z_i alone, and is implemented via a trainable self-interaction layer.)

**q009** (lookup): What datasets is Nequip tested on?
- answer: NequIP was tested on MD-17 (eight small organic molecules, with the original and revised versions both used), the CCSD and CCSD(T) small-molecule set (aspirin, benzene, malonaldehyde, toluene, ethanol), liquid water and ice structures, an amorphous lithium phosphate, and the lithium superionic conductor LiPS [W4225405705#023][W4225405705#010][W4225405705#012]. The paper also describes a chemical reaction at a solid/gas interface, which is not named as a specific dataset in the passages I read [W4225405705#010][W4225405705#017].
- reference: 1) MD-17 small organic molecules, both the original DFT version and the revised MD-17 (rMD17). 2) Small molecules at quantum-chemical accuracy: aspirin at CCSD; benzene, malonaldehyde, toluene and
   ethanol at CCSD(T).
3) Periodic systems:
   - liquid water and ice
   - a chemical reaction at a solid/gas interface (formate decomposition on a copper surface)
   - amorphous lithium phosphate (Li4P2O7)
   - a lithium superionic conductor (Li6.75P3S11, "LiPS")
- correctness: correct (The answer covers all the reference datasets: MD-17 and rMD17, the CCSD/CCSD(T) molecules, water and ice, amorphous Li phosphate, LiPS, and the solid/gas interface reaction. It does not name formate on copper, but it does mention the reaction, so nothing contradicts the reference.)
- support: None (judge returned no valid verdict: The answer's claims check out against the passages:

- **MD-17:** [023] describes eight small organic molecules and both the original and revised versions, and [010] confirms NequIP was benchmarked on)
- steps: search "NequIP datasets tested" (8 passages, 8 new); search "NequIP equivariant neural network interatomic potential dataset" (8 passages, 8 new); search "NequIP benchmark data sets molecules MD17 materials dataset" (8 passages, 6 new); answer

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: In the original NequIP paper (W4225405705), the MD-17 comparison covers invariant GNNs SchNet and DimeNet, the shallow network ANI, and the kernel methods GAP, FCHL19/GPR and sGDML [W4225405705#010]. It also compares against ACE, SpookyNet, GemNet, and the equivariant networks PaiNN, NewtonNet and UNiTE [W4225405705#010]. The paper notes that PaiNN and NewtonNet are lmax=1-only versions [W4225405705#011]. I did not read the result tables themselves, so this list is taken from the paper's text.
- reference: Invariant GNN potentials: SchNet and DimeNet. A shallow neural network: ANI. Kernel methods: GAP, FCHL19/GPR and sGDML. Other methods: ACE, SpookyNet and GemNet. Other equivariant networks: PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are restricted to l_max = 1. Results for ACE, GAP and ANI on revised MD-17 are taken from another paper (Kovács et al.), not retrained by the authors. NequIP reports the best accuracy of all of them.
- correctness: correct (The answer lists all the reference models with the same categories and notes the l_max=1 restriction for PaiNN and NewtonNet; it omits only the Kovács et al. sourcing detail and the best-accuracy claim, which are secondary to the question.)
- support: supported (All listed methods, their categories, and the PaiNN/NewtonNet lmax=1 note are stated in the cited passages.)
- steps: search "NequIP MD17 comparison models accuracy" (8 passages, 8 new); search "NequIP E(3)-equivariant interatomic potentials MD-17 benchmark" (8 passages, 8 new); answer

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet takes the interatomic distance d_ij = ||r_i − r_j|| as input to its filter-generating network, and first expands it with radial basis functions: e_k(r_i − r_j) = exp(−γ‖d_ij − μ_k‖²), with centers μ_k spaced every 0.1 Å between 0 and 30 Å and γ = 10 Å⁻² [W2726670313#009]. The expanded distances then pass through two dense layers with softplus activations to produce the filter weights W(r_i − r_j) [W2726670313#009]. The expansion, rather than the raw distance, is what keeps the initial filters from being too correlated, which speeds up training [W2726670313#009].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: None (judge returned no valid verdict: )
- support: None (judge returned no valid verdict: The passage supports the main claims: the distance input, the RBF expansion with centers every 0.1 Å from 0 to 30 Å, the two dense layers with softplus activations, and the claim that the expansion ma)

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses the shifted softplus, ssp(x) = ln(0.5e^x + 0.5), throughout the network [W2726670313#007][W2778051509#006]. Its shift ensures ssp(0) = 0 and improves convergence, and it has infinite order of continuity [W2726670313#010]. This matters for force fields because forces are obtained by differentiating the predicted energy with respect to atomic positions, so the model must be at least twice differentiable to train with forces [W2726670313#010]. The smoothness of the activation gives smooth potential energy surfaces, force fields and second derivatives, which are needed for training with forces and for computing vibrational modes [W2778051509#006]. By contrast, a ReLU-type max(0, x) is not differentiable at zero, which causes problems when continuous derivatives of the output are needed [W2923693308#007].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (The answer matches all key facts of the reference: the shifted softplus formula, ssp(0)=0 and better convergence, infinite differentiability, and smooth energy surfaces, forces and second derivatives for force training and vibrational modes. The extra ReLU comparison is correct and does not contradict the reference.)
- support: supported (Every claim is stated in the cited passages: the ssp definition and its use throughout the network, the shift and infinite continuity, forces from energy derivatives with the twice-differentiable requirement, smooth PES/second derivatives for vibrational modes, and max(0,x) not being differentiable at zero.)
- steps: search "SchNet activation function shifted softplus" (6 passages, 6 new); search "SchNet continuous-filter convolutional neural network smooth potential energy surface forces derivative" (6 passages, 5 new); answer

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: Ordinary convolutions rely on a regular grid, where a fixed filter tensor can be applied to each pixel's neighbours. Atoms in a molecule do not sit on such a grid. They are unevenly spaced at arbitrary 3D positions, and their exact positions carry essential physical information that discretizing would lose [W2726670313#001][W2778051509#006]. So a filter tensor is not applicable. SchNet instead generates the filter values continuously from interatomic distances with a filter-generating network [W2778051509#006][W2778051509#008]. Discretizing the positions onto a grid would also make energy predictions discontinuous as atoms move, which is why SchNet uses continuous filters [W2726670313#005].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (The answer states that atoms lie at arbitrary positions rather than on a regular grid, so a fixed filter tensor can't be used, and that SchNet uses a filter-generating network to compute continuous filters from interatomic distances (relative positions). The additional points about discretization are consistent with this.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

1. Ordinary convolutions rely on a regular grid and a filter tensor: W2778051509#006 says atoms are not on a regular grid like image pixels and a filter tens)
- steps: search "SchNet continuous-filter convolutional layers atoms not on grid" (8 passages, 8 new); search "SchNet convolution image grid molecules irregular positions" (8 passages, 5 new); answer

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of r_cut = 5 Å when learning formation energies of bulk crystals from the Materials Project data [W2778051509#014]. (The MEGNet paper, which used 4 Å, is a different model and not what was asked.)
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer gives the 5 Å cutoff on Materials Project data, matching the reference; it omits the dropped structures and the QM9/MD17 note, which are minor details.)
- support: partial (The 5 Å cutoff for SchNet on Materials Project is supported, but the parenthetical claim that the MEGNet paper used 4 Å is not in the cited passage.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: SchNet obtains its forces by differentiating the energy model with respect to the atomic positions, rather than predicting forces as a separate output: the force on atom i is the negative gradient of the predicted energy, F̂_i = −∂Ê/∂r_i [W2726670313#010]. Because the force is defined as the gradient of a single energy function, it is energy-conserving by construction [W2726670313#010][W2726670313#003]. The model also uses a shifted softplus activation, which makes it at least twice differentiable and gives a smooth potential energy surface [W2726670313#010]. Forces are included in the training loss alongside energies, so the model is trained on both properties [W2726670313#010].
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: correct (The answer states that forces are the negative gradient of the predicted energy with respect to positions (not predicted separately), making them energy-conserving by construction, matching the reference; the extra details about the softplus activation and the training loss are consistent with SchNet, and the omission of rotational equivariance is minor.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

1. Forces obtained by differentiating the energy model, F̂_i = −∂Ê/∂r_i: stated in #010 (Eq. 4).
2. Energy-conserving by construction: stated in #010 and in )
- steps: search "SchNet forces energy conservation gradient of energy with respect to positions" (8 passages, 8 new); search "SchNet continuous-filter convolutional neural network forces as negative gradient of predicted energy" (8 passages, 5 new); answer

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: SchNet's filters see only the distance between atoms. Its filter-generating network takes interatomic distances expanded in radial basis functions, which makes the filters rotationally invariant [W2726670313#009]. Each filter therefore emphasizes ranges of distance, so each interaction block builds features from the radial environment of each atom, and the stacked blocks give many-body representations while staying rotationally invariant [W2726670313#009].

NequIP's filters also see direction. Each filter is a learnable radial function of the distance multiplied by spherical harmonics of the unit vector from the central atom to the neighbor [W4225405705#006]. Its features are therefore tensors of different orders (scalars, vectors, higher-order tensors) with parity, and the convolution is equivariant rather than invariant [W4225405705#006]. The design-space analysis also classes NequIP as using Cartesian-free spherical tensors with l_max ≥ 1, unlike SchNet's l = 0 convolution [W4406405186#008].

So SchNet builds invariant scalar features from distances, while NequIP builds equivariant features that carry directional and tensorial information about the neighborhood.
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: correct (Matches the reference: SchNet filters see only distances (radial basis expansion), giving invariant scalar features; NequIP filters also use direction via spherical harmonics, giving equivariant tensor features; it also notes SchNet corresponds to l=0, which is consistent with the reference's scalar-restriction point.)
- support: None (judge returned no valid verdict: The SchNet claims are supported by W2726670313#009: distance-only input, radial basis expansion, rotational invariance, filters emphasizing distance ranges, radial environment updates, and stacked blo)
- steps: search "SchNet continuous-filter convolution interatomic distances" (5 passages, 5 new); search "NequIP E(3) equivariant convolution radial basis spherical harmonics neighbors" (5 passages, 5 new); answer

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: The SchNet paper compared against GDML (gradient domain machine learning), the kernel method introduced by Chmiela et al. for MD17, alongside DTNN. Its MD17 tables list GDML's energy and force errors next to SchNet's at 1,000 and 50,000 training examples [W2726670313#014][W2778051509#017].

NequIP is competitive with kernel methods on small molecular datasets. Its paper reports that it outperforms other neural networks there and is competitive with kernel approaches, which typically reach better accuracy than neural network potentials on small data, though at higher cost in training and prediction [W4225405705#002]. In a later comparison table, NequIP's MD17 force errors were lower than those of sGDML and FCHL19 on most molecules [W4287126984#018].
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: partial (The answer correctly names GDML for SchNet and says NequIP beats sGDML and FCHL19 on most molecules, but it describes NequIP overall as only 'competitive with' kernel methods, omits GAP, and never says GDML was more data-efficient on small training sets.)
- support: None (judge returned no valid verdict: )
- steps: search "SchNet MD17 kernel method comparison" (8 passages, 8 new); search "NequIP MD17 kernel methods comparison" (8 passages, 5 new); answer

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: The SchNet paper says the atomic-contribution decomposition is a poor fit for the polarizability α and the electronic spatial extent ⟨R²⟩. It says these two properties "fall noticeably short in terms of accuracy" and that this is "most likely due to the decomposition of the energy into atomic contributions which is not appropriate for these properties" [W2778051509#013]. The passages I retrieved do not mention the Behler-Parrinello potential in that context, so the comparison to it is not addressed there.
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: correct (The answer identifies polarizability α and electronic spatial extent ⟨R²⟩ as the poorly fitting properties and attributes this to the atom-wise decomposition, matching the reference; the note about Behler-Parrinello not being retrieved is harmless.)
- support: supported (The quoted statements and the paraphrase match the passage, and the passage does not mention Behler-Parrinello, as the answer says.)
- steps: search "SchNet atomic contributions Behler-Parrinello poor fit properties" (8 passages, 8 new); search "atomic contributions not suitable for extensive properties total energy continuous-filter convolutional" (8 passages, 8 new); search "atom-wise contributions poor fit property not additive dipole moment band gap" (8 passages, 7 new); search "Behler-Parrinello atomic contributions summation limitation" (8 passages, 3 new); answer

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: The passages I could reach do not state the specific flaw in CHARMM36 that CHARMM36m targets. The CHARMM36m paper's abstract says it is a refinement of the all-atom CHARMM36 protein force field with "improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins" [W2555870966#000]. So the problem it addressed was the inaccuracy of CHARMM36 in describing backbone ensembles of intrinsically disordered proteins and peptides. Only the abstract of that paper was available, so I could not confirm the exact nature of that inaccuracy.
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (It correctly says CHARMM36 was inaccurate for intrinsically disordered proteins and peptides, but it omits the specific flaw (overstabilized compact and left-handed helical structures) and does not mention keeping accuracy for folded proteins.)
- support: supported (All claims, including the quoted abstract text and the inference that CHARMM36 was less accurate for IDP backbone ensembles, follow from the cited passage, and the stated limitations are consistent with it.)
- steps: search "CHARMM36m improved force field intrinsically disordered proteins" (6 passages, 6 new); search "CHARMM36 overly compact disordered proteins correction" (6 passages, 3 new); search "CHARMM36 overestimates compaction of unfolded or disordered peptides, too collapsed" (1 passage, 0 new); open_paper "W2555870966" (1 section); search "CHARMM36 force field too compact disordered proteins CHARMM36m fixes" (8 passages, 2 new); search "CHARMM36 IDPs overly compact simulations dimensions too small" (8 passages, 7 new); search "CHARMM36 disordered proteins simulations too compact" (1 passage, 0 new); answer

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The retrieved passages only partly answer this. CHARMM36m is described as a refinement of CHARMM36 with improved accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. The paper's full text was not available (only its abstract), so I could not find which specific parameters (for example the backbone CMAP correction or the nonbonded terms) were changed. Other papers in the collection, such as the CHARMM36 NMR validation study, discuss CMAP and χ1/χ2 dihedral parameters for CHARMM36 relative to CHARMM22/CMAP [W2109154308#000], but they do not describe the CHARMM36-to-CHARMM36m modifications.
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (The answer declines to state what changed (backbone CMAP refit, modified TIP3P with stronger water-hydrogen LJ), only mentioning CMAP as a possibility it could not confirm, so it misses the reference's main point.)
- support: None (judge returned no valid verdict: The claims check out against the passages:

1. CHARMM36m is a refinement of CHARMM36 with improved accuracy for polypeptide backbone ensembles of IDPs. W2555870966 states this directly.
2. The full te)
- steps: search "CHARMM36m modified force field changes" (8 passages, 8 new); search "CHARMM36 refinement backbone dihedral CMAP modification intrinsically disordered proteins" (8 passages, 7 new); search "CHARMM36m modified backbone CMAP torsion potential Lennard-Jones water-protein interaction scaled" (1 passage, 0 new); open_paper "W2555870966" (1 section); search "CHARMM36m refinement CMAP backbone dihedral and modified water interaction Lennard-Jones terms for protein" (8 passages, 4 new); search "CHARMM36m differs from CHARMM36 by" (8 passages, 4 new); answer

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: The collection does not contain the RFdiffusion paper itself. The only passages that mention RFdiffusion are citations in other papers (e.g., DynamicBind cites "De novo design of protein structure and function with RFdiffusion" [W4391542588#028]), and none report an experimental success rate for protein binder design. The related Watson et al. (2022) RoseTTAFold-based binder work is mentioned only as having "successful experimental validation" [W4393118201#004], with no rate given.
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.
- steps: search "RFdiffusion protein binder design experimental success rate" (6 passages, 6 new); search "RFdiffusion de novo binder experimentally validated percent of designs" (6 passages, 6 new); search "RFdiffusion generative model of protein backbones denoising diffusion" (6 passages, 3 new); search "RFdiffusion binders success rate experimental characterization" (8 passages, 6 new); give_up

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: The SchNet papers in the collection (W2726670313, W2778051509) describe their training setup (Adam/SGD optimizer, initial learning rate 10^-3 with exponential decay, 32 molecules per mini-batch, EMA decay 0.99, early stopping on a 1,000-example validation set), but none of the passages I found mention a dropout rate. Searches for dropout within the SchNet paper returned nothing relevant, so the papers do not state the dropout rate used for SchNet.
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.
- steps: search "SchNet dropout rate training" (8 passages, 8 new); search "SchNet dropout" (8 passages, 5 new); search "dropout" (no results); search "dropout rate regularization hyperparameters" (1 passage, 0 new); search "SchNet model trained with dropout" (10 passages, 6 new); give_up

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: DiffTRe does not backpropagate through the MD simulation. For time-independent observables, it reweights states from a reference trajectory, so it only differentiates through the potential energy of a set of saved, decorrelated states. Direct reverse-mode AD instead differentiates through the whole trajectory [W3168247670#003][W3168247670#011]. The payoff is that gradients avoid exploding for long trajectories, with constant gradient magnitudes versus exponential growth under direct AD [W3168247670#011]. Gradient computation is about 2 orders of magnitude faster than backpropagation through the simulation, and its memory needs are comparable to the adjoint method [W3168247670#003]. Reweighting also lets previously generated trajectories be reused [W3168247670#006]. The trade-off is that the reweighting scheme makes DiffTRe invariant to the sequence of states, so dynamical properties cannot be used as targets [W3168247670#019].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: correct (The answer matches the reference: no backprop through the simulation, reweighting of ensemble averages, avoids exploding gradients, ~2 orders of magnitude faster, memory comparable to adjoint; extra details (trajectory reuse, no dynamical properties) are consistent.)
- support: None (judge returned no valid verdict: The answer's claims check out against the passages:

- **No backpropagation through the MD simulation, differentiating only through the potential energy of decorrelated states, with direct AD going th)
- steps: search "DiffTRe differentiable trajectory reweighting" (6 passages, 6 new); search "backpropagation through molecular dynamics simulation memory cost gradients" (6 passages, 6 new); answer

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: DiffTRe computes each retained state's weight from the potential energy difference between the current and reference parameters. Starting from the reweighting ansatz, the weight is w_i = exp(-β(U_θ(S_i) - U_θ̂(S_i))) divided by the sum of the same quantity over all N stored states, where β = 1/(k_B T) [W3168247670#005]. The weights are recomputed from the stored reference states, and the gradient of the loss flows through these weights and U_θ(S_i) [W3168247670#007].

The kinetic energy drops out because the state probabilities are Boltzmann factors of the full Hamiltonian, p_θ(S_i) ~ exp(-βH(S_i)), where H is the sum of potential and kinetic energy. In the ratio p_θ(S_i)/p_θ̂(S_i), the kinetic term is the same under both parameter sets and cancels, leaving only the potential energy difference [W3168247670#005]. The paper notes this explicitly: "the kinetic energy cancels" [W3168247670#005].
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (The answer gives the same normalized weight formula w_i = exp(-β(U_θ - U_ref)) and explains that the kinetic energy cancels in the Boltzmann ratio because it is identical under both parameter sets; the omitted 1/N detail at θ = reference is minor.)
- support: None (judge returned no valid verdict: The answer's claims match the passages.

- **Weight formula:** Eq. 4 in #005 gives w_i = exp(-β(U_θ - U_θ̂)) divided by the sum over all N states, with β = 1/(k_B T). The answer matches this.
- **Kine)
- steps: search "DiffTRe reweighting weights kinetic energy" (8 passages, 8 new); search "differentiable trajectory reweighting reweighting factor potential energy difference" (8 passages, 6 new); answer

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe keeps reweighting and updating θ with the saved states until the effective sample size drops below a predefined threshold, N_eff < N̄_eff. At that point a new reference trajectory is sampled from the last generated state S_N, using the current θ as the new reference [W3168247670#006][W3168247670#007].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (Matches the reference: a new trajectory is simulated when the effective sample size falls below a threshold, starting from the last state of the old trajectory with the current parameters; the omitted N_eff formula and the explanation that a few states dominate the average are minor details.)
- support: supported (The cited passages state that DiffTRe repeats reweighting, gradient computation and θ updates on saved states until N_eff < N̄_eff, and that a new reference trajectory is then sampled from the last state S_N with the current θ as the new reference.)
- steps: search "DiffTRe trajectory reuse new simulation" (8 passages, 8 new); search "differentiable trajectory reweighting reuse trajectory threshold" (8 passages, 5 new); answer

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The DiffTRe diamond potential was trained on diamond's experimental elastic stiffness tensor. The loss uses three stiffness moduli, C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa, plus a stress-free state at zero strain [W3168247670#013]. The simulation matched the experimental density (3512 kg/m³) and temperature (298.15 K) [W3168247670#013]. The paper describes this as learning the DimeNet++ model "from its experimental stiffness tensor" [W3168247670#004].
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer matches the reference: experimental elastic stiffness tensor with C11=1079, C12=124, C44=578 GPa plus stress-free state at zero strain; the extra details on density and temperature do not contradict it.)
- support: None (judge returned no valid verdict: Check claims against passages.

1. Trained on experimental elastic stiffness tensor: supported (#013).
2. Loss uses three moduli C11=1079, C12=124, C44=578 plus stress-free state at zero strain: suppo)
- steps: search "DiffTRe diamond potential trained" (8 passages, 8 new); search "differentiable trajectory reweighting diamond experimental data" (8 passages, 4 new); answer

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: DiffTRe's coarse-grained water model got the self-diffusion coefficient wrong. It predicted D = 10.91 μm²/ms against an experimental value of 2.2 μm²/ms [W3168247670#017]. The paper attributes this to coarse-graining: CG models have smoother potential energy surfaces, which accelerate dynamical processes compared with atomistic models [W3168247670#017]. The authors also note that diffusion coefficients decrease as the number of interaction sites grows [W3168247670#017]. The learned model's diffusion coefficient fell over the optimization, which they suggest means it behaves like a single-site model at first and then learns three-body interactions that make it more like a multi-site CG model [W3168247670#017].
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (The answer identifies self-diffusion coefficient, gives 10.91 vs 2.2 μm²/ms, and attributes it to smoother potential energy surfaces in CG models accelerating dynamics, matching the reference; extra details are consistent.)
- support: None (judge returned no valid verdict: The answer's claims match the passage.

- **D values:** The passage gives D = 10.91 μm²/ms against an experimental 2.2 μm²/ms. The answer says the model "got the self-diffusion coefficient wrong", whi)
- steps: search "DiffTRe coarse-grained water model held-out property" (8 passages, 8 new); search "differentiable trajectory reweighting water transferability" (8 passages, 6 new); answer

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: No, not with DiffTRe as originally published. The DiffTRe paper states that reweighting makes the method invariant to the sequence of states, so "dynamical properties cannot be employed as target observables" [W3168247670#019]. It applies to time-independent observables such as RDFs, pressure, and stiffness tensors [W3168247670#001].

A 2025 follow-up extends this idea to dynamical properties. It fits the self-diffusion coefficient of a Lennard-Jones liquid by combining differentiable reweighting (for the thermodynamic gradient) with trajectory differentiation via the adjoint method (for the dynamical gradient) [W4406553977#004][W4406553977#006][W4406553977#010]. That work is a different method from DiffTRe, though it builds on the same reweighting framework [W4406553977#003].
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: correct (The answer says No, as the reference does, and gives the same reason: reweighting is invariant to state order, so only time-independent observables can be targets. The extra detail about a follow-up method is a separate method and does not contradict the reference.)
- support: None (judge returned no valid verdict: )
- steps: search "DiffTRe differentiable trajectory reweighting diffusion coefficient" (8 passages, 8 new); search "differentiable trajectory reweighting experimental observables potential fitting" (8 passages, 5 new); search "Refining potential energy surface dynamical properties diffusion coefficient reweighting" (8 passages, 7 new); answer

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: The DiffTRe authors do not discuss SchNet's C20 model. The C20 work is in the SchNet paper, which trained on PBE+vdW-TS DFT reference data [W2778051509#019]. In the DiffTRe paper, the authors say the main obstacle in bottom-up learning of NN potentials is "limited availability of highly precise and sufficiently broad data sets," since quantum mechanics computations for larger systems such as macromolecules remain intractable [W3168247670#003]. They also note that DFT-trained models are limited by the accuracy of DFT itself, which is sensitive to the functional used [W3168247670#002]. Instead, they train on experimental data (top-down): for example, the experimental stiffness tensor of diamond, and pressure plus radial and angular distribution functions for coarse-grained water [W3168247670#003][W3168247670#013][W3168247670#017].
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: correct (The answer states the same limitation (scarce, precise and broad enough quantum data, and accuracy capped by DFT) and the same alternative (top-down training on experimental observables), with accurate extra detail.)
- support: None (judge returned no valid verdict: )
- steps: search "DiffTRe differentiable trajectory reweighting coarse-grained C20 SchNet" (8 passages, 8 new); search "limitation training on DFT data experimental observables" (8 passages, 5 new); search "C20 fullerene SchNet force field" (8 passages, 8 new); answer

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: DiffTRe's diamond model starts from the Stillinger-Weber potential, which was originally parametrized for silicon. The authors adjusted its length and energy scales for carbon [W3168247670#013]. The neural network paper that used silicon as its test system is Behler and Parrinello's "Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces", which applies its NN-based potential to bulk silicon [W2025444507#000].
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: correct (Identifies the Stillinger-Weber potential originally for silicon, rescaled for carbon, and the Behler-Parrinello NN potential paper using bulk silicon, matching the reference.)
- support: None (judge returned no valid verdict: The first part is directly supported by W3168247670#013: the Stillinger-Weber potential is parametrized for silicon, and the length and energy scales were adjusted for carbon (σSW = 0.14 nm, εSW = 200)
- steps: search "DiffTRe diamond empirical potential" (8 passages, 8 new); search "differentiable trajectory reweighting diamond neural network potential" (8 passages, 4 new); search "neural network potential silicon test system" (8 passages, 8 new); search "machine-learned interatomic potential silicon Gaussian approximation potential" (8 passages, 8 new); answer

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: DiffTRe uses DimeNet++, a graph neural network, as its learnable potential. In its examples, the learnable part is a graph neural network that works iteratively on the atomic graph, and the paper names DimeNet++ as the model it trains for diamond and coarse-grained water [W3168247670#004][W3168247670#007].

NequIP is an E(3)-equivariant graph neural network, and it significantly outperforms invariant GNN potentials such as SchNet and DimeNet on MD-17. The paper also reports that the equivariant NequIP models outperform all other methods it benchmarks, which include GemNet and PaiNN [W4225405705#010][W4225405705#011]. The passages I retrieved do not show the full MD-17 numbers for DimeNet++ itself, so I can't give a quantitative gap against it.
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: correct (The answer identifies DimeNet++ for DiffTRe (diamond and coarse-grained water) and states NequIP significantly outperforms invariant GNNs like SchNet and DimeNet on MD-17, matching the reference; extra details do not contradict it.)
- support: None (judge returned no valid verdict: The DiffTRe claims are supported: [004] names DimeNet++ for diamond and CG water, and [007] says Umodel is a graph neural network operating iteratively on the atomic graph.

The NequIP claims are also)
- steps: search "DiffTRe learnable potential graph neural network" (8 passages, 8 new); search "NequIP MD-17 comparison" (8 passages, 8 new); search "NequIP DimeNet SchNet MD-17 mean absolute error table energies forces" (8 passages, 2 new); answer

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: In DiffTRe, the prior potential U_prior is a constant potential that approximates a-priori known properties of the system, such as the Pauli exclusion principle. It is added to the learnable model potential, and it is not a prior in the Bayesian sense, which would impose a bias on the learnable parameters in the small-data regime [W3168247670#008]. Its role is to control trajectory generation at the start of optimization and to turn learning into fitting the difference between U_prior and the optimal potential [W3168247670#008][W3168247670#010].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: correct (It captures the main points: a fixed physics-based potential added to the NN, controlling trajectory generation early in training, and making the network learn a correction; the omitted 'data can override it' detail is minor.)
- support: supported (All claims (constant potential approximating known properties, added to model potential, not Bayesian, controls early trajectory generation, reformulates learning as the difference) are stated in #008 and #010.)
- steps: search "DiffTRe prior potential not a Bayesian prior" (8 passages, 8 new); search "DiffTRe differentiable trajectory reweighting prior potential" (8 passages, 5 new); answer

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The DiffTRe paper (W3168247670) does not state a total GPU-hour figure for training the diamond DimeNet++ potential. Its diamond section describes the setup (1000 carbon atoms, 10 ps equilibration and 60 ps production per trajectory, 700 update steps shown in Fig. 3) and says the wall-clock time per update is in Supplementary Fig. 5 a [W3168247670#013][W3168247670#014]. The supplementary figure is not in the indexed text, so the total cannot be computed from the passages. The only GPU-hour numbers in the collection belong to other papers (for example UNiTE and DTNN), which do not concern DiffTRe.
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.
- steps: search "DiffTRe diamond potential GPU hours training" (8 passages, 8 new); search "DiffTRe differentiable trajectory reweighting GPU hours" (8 passages, 6 new); search "GPU hours diamond DimeNet++ training total" (8 passages, 3 new); search "computational cost hours NVIDIA GPU" (6 passages, 3 new); search "wall-clock time per update training loss diamond supplementary hours" (8 passages, 4 new); search "GPU hours" (no results); search "trained on NVIDIA GPU total training time diamond potential updates" (5 passages, 0 new); search "Supplementary Method 4 diamond simulation details" (5 passages, 0 new); open_paper "W3168247670" (15 sections); read_around "W3168247670#020" (4 passages, 3 new); give_up

