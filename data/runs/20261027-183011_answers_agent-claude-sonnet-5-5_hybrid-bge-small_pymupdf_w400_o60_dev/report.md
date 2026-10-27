# Answer eval: claude-sonnet-5-5

- **Generator:** `{"name": "agent", "provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "agent-v2", "tools": ["search", "read_around", "open_paper"], "max_turns": 8, "token_budget": 100000}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1"}`
- **Retrieval:** hybrid, top 8 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 9e6de1d92dea)
- **Cost:** generator $1.016, judge $0.319

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.94 [0.85, 1.00] | 27 |
| Supported by its citations | 0.94 [0.81, 1.00] | 8 |
| Cites your evidence | 0.81 [0.67, 0.96] | 27 |
| Evidence was retrieved | 0.81 [0.67, 0.96] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 29 |
| Declines when unanswerable | 0.33 [0.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.00 [0.00, 0.00] | 29 |

Correct when the evidence was retrieved: 1.00 (n=21)

Correct when no evidence was retrieved: 1.00 (n=4)

## Effort per question (mean)

2.6 model calls, 1.9 tool calls (1.8 searches), 12.3 passages read, 18,965 input tokens, $0.0317 per question, 6.5 s. Gave up on 3%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: Behler and Parrinello demonstrated their neural network potential on bulk silicon. They built an NN-based many-body potential for it and compared it with empirical potentials and DFT [W2025444507#000][W2025444507#001]. It worked in the solid semiconducting and liquid metallic phases. It also reproduced the small energy differences between the high-pressure crystalline phases [W2025444507#001].

A review of the method says it reproduced DFT energies to within 5 meV/atom. It also says molecular dynamics with the potential reproduced the radial distribution function (RDF) of a silicon melt at 3000 K [W2968923792#056].
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: correct (The answer identifies bulk silicon as the test system and notes comparison with DFT, matching the reference; the extra details are consistent with the original Behler-Parrinello work.)
- support: supported (Every claim is stated in the cited passages: the bulk silicon demonstration, the comparison with empirical potentials and DFT, the solid and liquid phases, the high-pressure phase energy differences, and the review's 5 meV/atom and 3000 K melt RDF results.)

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: The original high-dimensional neural network potential (Behler and Parrinello, 2007) uses a cosine cutoff function of the interatomic distance R_ij. It is fc(R_ij) = 0.5·[cos(π R_ij / R_c) + 1] for R_ij ≤ R_c, and fc(R_ij) = 0 for R_ij > R_c [W2025444507#004]. The extracted text of that paper is garbled around this equation. I read the "+1" and the π from the cleaner reproductions of the same function in the ANI-1 paper and a later cost-assessment paper [W2541404351#007][W3000291311#028].

The function gives zero value and zero slope at separations beyond R_c [W2025444507#005]. The paper used R_c = 6 Å [W2025444507#005].
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: correct (The answer gives the same cosine cutoff, f_c = 0.5[cos(πR/R_c)+1] for R ≤ R_c and 0 beyond, matching the reference; the extra details (R_c = 6 Å, zero slope) do not contradict it.)
- support: None (judge returned no valid verdict: The answer's claims line up with the cited passages.

- **Cutoff function form:** The Behler–Parrinello passage W2025444507#004 gives a garbled version of Eq. 3, but it shows the cosine form with 0.5 )
- steps: search "cutoff function high-dimensional neural network potential Behler Parrinello" (8 passages, 8 new); search "cutoff function fc(Rij) = 0.5 cos(pi Rij/Rc) + 1 Eq. (3)" (8 passages, 5 new); answer

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: In a high-dimensional neural network potential (HDNNP), the total energy is the sum of atomic energy contributions, E = Σ_i E_i [W2025444507#003][W4312043350#015].

- **Where each E_i comes from.** Each E_i is the output of an atomic neural network (a "subnet"). Its input is a set of symmetry-function values that describe atom i's local environment [W2025444507#003]. In some implementations there is one network per element [W2541404351#007].
- **Weight sharing.** Within an element, the subnet structure and weights are identical. This keeps the total energy unchanged when two atoms of the same type are interchanged [W2025444507#003].
- **Consequences of the sum.** The sum is permutation invariant. It also lets the same network predict systems with different numbers of atoms [W3093149769#038].
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states the total energy is a sum of atomic energies, each output by an atomic neural network from symmetry-function descriptors of the atom's local environment, which matches the reference (cutoff is implied by 'local environment').)
- support: supported (Each claim is stated in the cited passages: the sum E = Σ E_i, subnet outputs from symmetry-function inputs, per-element networks in some implementations (ANI), identical subnet structure and weights for interchange invariance, and permutation invariance and varying atom counts from the decomposition.)

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP's internal features are equivariant under E(3), the group of rotations, reflections (parity) and translations in 3D [W4225405705#005].

**How the features are built**
- Each atom carries features that are geometric tensors: scalars, vectors and higher-order tensors [W4225405705#006]. Formally, these form a direct sum of irreducible representations of O(3) [W4225405705#006].
- The features V^(l,p)_acm are indexed by rotation order l = 0, 1, 2, … and parity p ∈ {1, −1}, which together label the irreducible representations. The other indices are the atom a, the channel c, and the representation index m ∈ [−l, l] [W4225405705#006].
- The layers come from Tensor-Field Networks, with primitives implemented in e3nn [W4225405705#006].
- The convolutions are equivariant. If a feature at layer k is rotated or reflected, the output at layer k+1 transforms accordingly [W4225405705#006].
- The convolution filters are products of a learnable radial function and spherical harmonics: F(r_ij) = R(r_ij) Y^(l)_m(r̂_ij). All learnable weights sit in the rotation-invariant radial function R, which is a small MLP acting on interatomic distances [W4225405705#006].
- Translation invariance comes from the filters acting on relative distance vectors, and permutation invariance from summing over neighbors [W4225405705#006].

The network's final output, the total potential energy, is invariant to translation, reflection and rotation. Only the internal features are equivariant [W4225405705#005].
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: correct (The answer states E(3), features as geometric tensors in irreps of O(3), and filters built from spherical harmonics of relative position vectors combined with radial functions via tensor products, matching the reference.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- E(3) as the group of rotations, reflections and translations in 3D: stated in #005.
- Features are scalars, vectors and higher-order tensors, forming a dir)

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: NequIP's papers don't describe Behler-Parrinello functions in detail, but the contrast is clear from the passages.

NequIP doesn't build rotation-invariant descriptors. Instead, its atomic features are geometric tensors (scalars, vectors and higher-order tensors) that transform equivariantly under rotation and parity [W4225405705#005][W4225405705#006]. These features are direct sums of irreducible representations of O(3), indexed by rotation order l and parity p. The convolution filters are products of a learnable radial function and spherical harmonics, F(r_ij) = R(r_ij) Y_m^(l)(r̂_ij). Because of this, a rotated input gives a correspondingly rotated output at every layer [W4225405705#006]. Only the final potential energy is invariant. It is a sum of atomic energies, and the forces are its gradients [W4225405705#005].

Behler-Parrinello-style atom-centred symmetry functions (ACSF) are a different kind of model. They are descriptors made invariant under rotation, translation, reflection and permutation before the model uses them [W4406405186#000]. Invariant models of this kind act only on scalars. The NequIP authors say its improved accuracy and data efficiency come from using equivariant instead of invariant representations [W4225405705#022]. They also note that a Behler-Parrinello network trained on 1303 structures gave a force RMSE of about 120 meV/Å. NequIP with l = 2 reached 129.8 meV/Å with 100 training points and 103.4 meV/Å with 250 [W4225405705#021].
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: correct (The answer captures the key contrast: Behler-Parrinello uses invariant descriptors acting on scalars, while NequIP uses equivariant tensor features (irreps of O(3)) propagated through layers, with only the final energy invariant.)
- support: None (judge returned no valid verdict: )

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: NequIP takes three things directly from SchNet, and a fourth is shared only in its l = 0 limit.

- **Atomic embedding.** NequIP's initial feature comes from a trainable embedding of the atomic number Zi, given as a one-hot encoding and implemented as a trainable self-interaction layer. The paper says this is done "following SchNet" [W4225405705#009]. SchNet likewise starts each atom from a trainable embedding that depends only on the atom type, x0_i = a_Zi [W2778051509#004].
- **Atom-wise self-interaction layers.** NequIP updates atomic features with dense layers applied atom by atom, with weights shared across atoms. The paper describes these as "similar to the self-interaction layers in SchNet" [W4225405705#008].
- **Overall structure.** Both architectures refine atom-wise features through a series of interaction blocks, using convolutions over neighbouring atoms with filters that depend on interatomic distances [W4225405705#006][W2778051509#003]. Both also sum atom-wise energy contributions into the total energy. SchNet inherits atom-wise energy contributions from DTNN [W2778051509#003]. In NequIP, the output block gives a scalar atomic energy per atom, and these are summed into the total energy [W4225405705#009].
- **Invariant scalar limit.** If NequIP keeps only the 0⊗0→0 interaction (l = 0), it becomes a conventional invariant GNN interatomic potential with convolutions over scalar features, "similar to e.g. SchNet" [W4225405705#008]. The paper also describes this setting as "SchNet-style" [W4225405705#019].

The passages do not state the features NequIP shares with SchNet in a single list, so this is assembled from the separate descriptions above.
- reference: Several design choices come from SchNet. The initial atom features are a trainable embedding of the atomic number (one-hot encoded). Atoms then pass through a stack of interaction blocks that do continuous convolutions over neighbors within a cutoff. In those convolutions the learnable filter weights are an MLP of the interatomic distance expanded in a radial basis: Gaussians in SchNet, Bessel functions with an envelope in NequIP. The output is per-atom energies summed to a total energy, and forces are its negative gradient. The difference is that NequIP also multiplies the radial part by spherical harmonics of the bond direction. If only l = 0 (scalar) features are kept, NequIP reduces to a SchNet-style invariant network.
- correctness: None (judge returned no valid verdict: )
- support: None (judge returned no valid verdict: )
- steps: search "NequIP architecture compared to SchNet features" (8 passages, 8 new); search "NequIP E(3)-equivariant interatomic potential message passing" (8 passages, 8 new); search "NequIP atom type embedding one-hot, radial network, self-interaction, residual, shifted softplus" (8 passages, 6 new); answer

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: As a first step, NequIP embeds each atom. The initial feature for each atom is generated by a trainable embedding that takes only the atomic number Zi, written as a one-hot encoding. It is implemented as a trainable self-interaction layer, following SchNet [W4225405705#009]. Interaction blocks and an output block come after this embedding [W4225405705#009].
- reference: It embeds each atom's chemical species. The atomic number Z_i, one-hot encoded, goes through a trainable self-interaction (linear) layer. This gives the initial per-atom features, which are scalar (l = 0) only. The embedding follows SchNet. Higher-order tensor features first appear in the interaction blocks.
- correctness: correct (The answer captures the key facts: one-hot atomic number Z_i, a trainable self-interaction layer, and the SchNet-style embedding. It omits that the initial features are scalar-only and that higher-order tensors appear later, but this is minor extra detail and nothing contradicts the reference.)
- support: supported (All claims (trainable embedding on one-hot Z only, self-interaction implementation, SchNet, followed by interaction blocks and output block) are stated in the passage.)

**q009** (lookup): What datasets is Nequip tested on?
- answer: In the original NequIP paper, it is tested on these datasets [W4225405705#010][W4225405705#012]:

- **MD-17 and revised MD-17:** small organic molecules with DFT reference data. NequIP is benchmarked on both versions, using 1,000 configurations for training and validation.
- **CCSD(T) molecules:** a set of small molecules at quantum-chemical accuracy. Aspirin is at CCSD and the others are at CCSD(T).
- **Liquid water and ice:** a joint set of liquid water and three ice Ih structures at the PBE0-TS level, 140,000 frames in total. NequIP is trained on only 133 structures.
- **Formate dehydrogenation on Cu<110>:** a reaction at a solid/gas interface, with 6,855 DFT structures. NequIP is trained on 2,500 of them [W4225405705#024].
- **Amorphous Li4P2O7:** lithium phosphate glass, from AIMD simulations of a melt and a quenched glass. NequIP is trained on 1,000 melt structures [W4225405705#016].
- **LiPS:** a lithium superionic conductor, with training sets of 10 to 2,500 structures [W4225405705#020].

NequIP is also trained on the M3GNet dataset in the GNoME paper [W4389132751#033]. The DPA-2 paper trains it on several large datasets as a baseline, including OC2M [W4405574099#057].
- reference: 1) MD-17 small organic molecules, both the original DFT version and the revised MD-17 (rMD17). 2) Small molecules at quantum-chemical accuracy: aspirin at CCSD; benzene, malonaldehyde, toluene and
   ethanol at CCSD(T).
3) Periodic systems:
   - liquid water and ice
   - a chemical reaction at a solid/gas interface (formate decomposition on a copper surface)
   - amorphous lithium phosphate (Li4P2O7)
   - a lithium superionic conductor (Li6.75P3S11, "LiPS")
- correctness: correct (The answer covers all the reference datasets (MD-17/rMD17, CCSD/CCSD(T) molecules, water/ice, formate on Cu, amorphous Li4P2O7, LiPS) and adds extra details that do not contradict the reference.)
- support: None (judge returned no valid verdict: )
- steps: search "NequIP evaluated on datasets" (8 passages, 8 new); search "NequIP experiments: MD-17, water, ice, formate on Cu, Li4P2O7, amorphous LiPO, CCSD(T) data set" (8 passages, 6 new); answer

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: In the original NequIP paper, NequIP is benchmarked on both the original and the revised MD-17 data sets, against these published models [W4225405705#010]:

- **Invariant GNN-IPs:** SchNet and DimeNet.
- **Shallow neural networks:** ANI.
- **Kernel-based approaches:** GAP, FCHL19/GPR and sGDML.
- **Other methods:** ACE, SpookyNet and GemNet.
- **Other equivariant neural networks:** PaiNN, NewtonNet and UNiTE.

The paper says NequIP significantly outperforms the invariant GNN-IPs, ANI and the kernel methods, and that it outperforms all the other methods too [W4225405705#010][W4225405705#011]. For the learning-curve comparison on aspirin, it also uses sGDML, FCHL19 and PhysNet [W4225405705#020].
- reference: Invariant GNN potentials: SchNet and DimeNet. A shallow neural network: ANI. Kernel methods: GAP, FCHL19/GPR and sGDML. Other methods: ACE, SpookyNet and GemNet. Other equivariant networks: PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are restricted to l_max = 1. Results for ACE, GAP and ANI on revised MD-17 are taken from another paper (Kovács et al.), not retrained by the authors. NequIP reports the best accuracy of all of them.
- correctness: correct (The answer lists all the reference's model categories and models (SchNet, DimeNet, ANI, GAP, FCHL19/GPR, sGDML, ACE, SpookyNet, GemNet, PaiNN, NewtonNet, UNiTE) and notes NequIP outperforms them; it omits the minor details about l_max=1 and results taken from Kovács et al., but adds no contradictions.)
- support: None (judge returned no valid verdict: The answer's claims line up with the passages.

- **Benchmarked on both data sets:** [010] says NequIP is benchmarked on both the original and the revised MD-17 data sets.
- **Model categories:** the )

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet first computes the interatomic distance d_ij = ‖r_i − r_j‖. Using the distance rather than the position vector makes the filters rotationally invariant [W2726670313#009].

It then expands the distance in radial basis functions, e_k(r_i − r_j) = exp(−γ‖d_ij − μ_k‖²). The centers μ_k lie between 0 Å and 30 Å, spaced every 0.1 Å, with γ = 10 Å [W2726670313#009]. This expansion is there because a freshly initialized network is close to linear. Without it the filters would be highly correlated, which causes a plateau at the start of training [W2726670313#009]. The extra non-linearity makes the initial filters less correlated and speeds up training [W2726670313#009].

The expanded distances are fed into two dense layers with softplus activations. These layers output the filter weight W(r_i − r_j) [W2726670313#009].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: None (judge returned no valid verdict: )
- support: None (judge returned no valid verdict: Checking each claim against the passage:

- d_ij = ‖r_i − r_j‖, used for rotational invariance: supported.
- The RBF expansion formula, with centers between 0 and 30 Å spaced every 0.1 Å and γ = 10 Å:)

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses a shifted softplus, ssp(x) = ln(0.5e^x + 0.5), as the non-linearity throughout the network [W2726670313#010].

Why it matters for force fields:
- **Smooth energy surface.** Forces are obtained by differentiating the predicted energy with respect to atom positions, F_i = −∂E/∂r_i. This gives an energy-conserving force field by construction. Training on a force loss also needs the model to be at least twice differentiable. The shifted softplus has infinite order of continuity, so the potential energy surface is smooth [W2726670313#010].
- **Convergence.** The shift makes ssp(0) = 0, which improves the network's convergence. The function is also similar to ELUs [W2726670313#010].

A related passage from SpookyNet, a different model, makes the same point in general terms. Kinks in an activation function would introduce discontinuities in the atomic forces [W3159653252#016]. PhysNet, also a different model, makes a similar point about max(0, x), which is not differentiable at 0 [W2923693308#007].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (Identifies shifted softplus with the correct formula, notes ssp(0)=0 aids convergence, and explains that infinite differentiability gives a smooth energy surface and forces, with second derivatives needed for force training; only vibrational modes are not mentioned, which is a minor omission.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- The ssp definition and its use throughout the network are in W2726670313.
- The force formula F_i = −∂E/∂r_i and the energy-conserving property are in W272)

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: SchNet can't use ordinary convolutional layers because atoms aren't on a regular grid, and ordinary convolutions need one.

- **Grid requirement:** Standard convolutions work on discretized signals such as image pixels, video frames or audio. There, the filter can be defined on the same grid as the data. This isn't possible for unevenly spaced inputs like atom positions in a molecule [W2726670313#006]. Atoms can sit at arbitrary positions, so a filter tensor of the kind used in conventional convolutional layers doesn't apply [W2778051509#006].
- **Discretizing loses information:** An atom's precise location carries essential physical information that would be lost if discretized [W2726670313#001]. A discrete filter can't capture subtle positional changes of atoms, which gives discontinuous energy predictions [W2726670313#005].
- **Resampling is a poor workaround:** Resampling onto a grid requires choosing an interpolation scheme, which is a challenge in itself. It may also need a large number of grid points [W2726670313#006].
- **SchNet's solution:** SchNet instead uses continuous-filter convolutions. A filter-generating neural network maps relative atom positions to filter values [W2726670313#006][W2778051509#006].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (The answer states that atoms lack a regular grid so a fixed filter tensor doesn't apply, and that SchNet uses continuous-filter convolutions with a filter-generating network mapping relative positions to filter values, matching the reference; extra detail is consistent.)
- support: None (judge returned no valid verdict: The answer's claims all trace to the cited passages:

- **Grid requirement:** W2726670313#006 states that convolutional layers operate on discretized signals such as image pixels, video frames or digi)

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of rcut = 5 Å when predicting formation energies for bulk crystals from the Materials Project. That setting meant two examples had to be discarded, because they would have contained isolated atoms [W2778051509#014].
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer states the 5 Å cutoff on Materials Project data and notes that two structures were discarded due to isolated atoms, matching the reference; it omits only the parenthetical about QM9/MD17.)
- support: supported (The passage states that rcut = 5 Å was used for Materials Project formation energies and that two examples with isolated atoms were discarded because of that setting.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: SchNet predicts a scalar energy and gets the forces by differentiating that energy with respect to the atom positions: F_i = −∂E/∂r_i. This makes the force field energy-conserving by construction [W2726670313#010]. The paper credits Chmiela et al. for pointing out that this construction gives a conservative force field [W2726670313#010].

Some related details:
- **Equivariance:** SchNet's energy predictions are rotationally invariant, so the forces are rotationally equivariant by construction [W2726670313#010].
- **Smoothness:** The model has to be at least twice differentiable so that the force loss can be trained by gradient descent. SchNet uses a shifted softplus non-linearity throughout, which gives a smooth potential energy surface [W2726670313#010].
- **Cost:** Getting forces needs a full forward and backward pass through the energy model. The force model is therefore twice as deep and takes about twice the computation time [W2726670313#010].
- **Force-only training:** Even when SchNet is trained on forces alone, as for C20-fullerene, using the derivative of an energy model still guarantees an energy-conserving force field [W2778051509#020].
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: correct (The answer states forces are the negative gradient of the predicted energy w.r.t. positions, giving a conservative field, and also notes rotational invariance yields equivariant forces, matching the reference.)
- support: supported (Every claim in the answer is stated in the cited passages: the force derivation, the credit to Chmiela et al., equivariance, twice-differentiability and shifted softplus, the twice-as-deep and twice-the-compute cost, and the C20 force-only point from W2778051509.)

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: SchNet's filters see only the interatomic distance. NequIP's filters see the full relative position vector, meaning both the distance and the direction.

**SchNet.** Each filter is generated by a network from the interatomic distance d_ij = ∥r_i − r_j∥, which is expanded in radial basis functions [W2726670313#009]. This makes the filters rotationally invariant. Each filter emphasizes certain ranges of interatomic distance, so a block can update an atom's representation according to its radial environment [W2726670313#009]. The features stay scalar and invariant. Stacking three interaction blocks lets SchNet build complex many-body representations, but the filters have no angular input [W2726670313#009].

**NequIP.** Each filter is F(r_ij) = R(r_ij)·Y_lm(r̂_ij). It is a learnable radial function times spherical harmonics of the unit direction vector [W4225405705#006]. All the learnable weights sit in the rotationally invariant radial MLP R, which acts on a Bessel basis of the distance [W4225405705#006][W4225405705#007]. Because the filter carries direction, the atom features are geometric tensors (scalars, vectors and higher-order tensors) labeled by rotation order l and parity [W4225405705#006]. The convolution combines input features with the filter through a Clebsch-Gordan tensor product. An input of order li and a filter of order lf give outputs of order |li − lf| ≤ lo ≤ |li + lf|, truncated at lmax [W4225405705#007]. The convolutions are therefore equivariant rather than invariant [W4225405705#006].

**The link between them.** If NequIP kept only the 0⊗0→0 interaction, it would reduce to a conventional GNN with invariant convolutions over scalar features, "similar to e.g. SchNet" [W4225405705#007].
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: correct (The answer matches the reference on all key points: SchNet filters use only distances (invariant, scalar features), NequIP filters include direction giving equivariant geometric tensor features, and scalar-only NequIP reduces to a SchNet-like invariant network.)
- support: None (judge returned no valid verdict: )
- steps: search "SchNet continuous-filter convolution filter depends on interatomic distance" (8 passages, 8 new); search "NequIP equivariant convolution filters radial function spherical harmonics tensor product" (8 passages, 8 new); answer

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: The SchNet paper compared against GDML, a kernel method, on MD17. NequIP does better than kernel methods of that kind, including sGDML.

**SchNet vs. GDML.** The SchNet paper says MD17 was introduced by Chmiela et al. for GDML. It reports SchNet at 1,000 and 50,000 training examples against GDML and DTNN [W2726670313#014]. GDML could not be trained on 50,000 examples because it does not scale well [W2726670313#014]. With 1,000 examples, SchNet beat GDML on the more flexible molecules malonaldehyde and ethanol. GDML had much lower force errors on the remaining trajectories, all of which contain aromatic rings [W2726670313#014][W2778051509#018].

**NequIP vs. kernel methods.** NequIP was trained on 1,000 configurations. It significantly outperformed kernel-based approaches such as GAP, FCHL19/GPR and sGDML, as well as invariant GNNs such as SchNet and DimeNet [W4225405705#010]. The NequIP authors call its consistent gains over sGDML and FCHL19/GPR "particularly surprising", because kernel methods typically beat deep neural networks on small training sets [W4225405705#011]. Elsewhere in the same paper they describe NequIP as "competitive with kernel-based approaches" on small molecular data sets [W4225405705#002].
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: correct (The answer identifies GDML as SchNet's kernel comparison, notes GDML's advantage on most molecules with small data, and states NequIP outperforms kernel methods including sGDML, GAP and FCHL19, matching the reference.)
- support: None (judge returned no valid verdict: The SchNet claims check out against W2726670313#014 and W2778051509#018. These include the MD17 introduction by Chmiela et al., the 1,000 and 50,000 training sizes, GDML not scaling, SchNet beating GD)
- steps: search "SchNet MD17 comparison with kernel method (sGDML, GDML)" (8 passages, 8 new); search "NequIP MD17 compared to kernel methods sGDML FCHL" (8 passages, 5 new); search "NequIP E(3)-equivariant interatomic potentials MD17 outperforms kernel methods with fewer training data" (8 passages, 8 new); answer

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: The SchNet paper says the decomposition into atomic contributions is a poor fit for the polarizability α and the electronic spatial extent ⟨R²⟩. On QM9, SchNet's predictions of these two properties "fall noticeably short in terms of accuracy". The authors attribute this "most likely" to the decomposition of the energy into atomic contributions, which they say "is not appropriate for these properties" [W2778051509#013][W2778051509#012].

By contrast, they say SchNet matches or beats enn-s2s on 8 of 12 properties, which they describe as properties "where a decomposition into atomic contributions is a good choice". They add that enn-s2s uses a set2set variant that builds a global representation and so avoids this issue [W2778051509#013].

The passages I read don't mention the Behler-Parrinello potential, so they don't say how this limitation applies to it.
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: correct (The answer identifies polarizability α and electronic spatial extent ⟨R²⟩ as the poor-fit properties and attributes it to atom-wise decomposition, matching the reference; the note about Behler-Parrinello not being mentioned in the passages is not a contradiction.)
- support: None (judge returned no valid verdict: {"verdict":"supported","reason":"Every claim and quotation matches the cited passages: the α and ⟨R²⟩ sh)

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: CHARMM36m was designed to improve how accurately CHARMM36 generates backbone conformational ensembles for intrinsically disordered peptides and proteins. It was meant to do this while still working for folded proteins [W2555870966#000]. The CHARMM36m abstract doesn't spell out the specific flaw. A separate benchmark gives some context: it found CHARMM36 ensembles had a high population of left-handed α-helix, which disagreed with measured scalar couplings [W2234602429#000]. I only read the CHARMM36m abstract, so I can't say which specific changes were made to fix this.
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (The answer correctly says CHARMM36m targeted IDP/IDPs ensembles while preserving folded-protein accuracy, and mentions left-handed helix overpopulation as context from another source, but it doesn't clearly state that this overstabilization (plus compactness) was the flaw CHARMM36m fixed, and it hedges that the specific flaw isn't spelled out.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

1. CHARMM36m is a refinement of CHARMM36 with improved accuracy in generating backbone conformational ensembles for IDPs. The passage states this directly.
2)
- steps: search "CHARMM36m improved force field for folded and intrinsically disordered proteins" (8 passages, 8 new); search "CHARMM36 deficiencies: overly compact IDP, left-handed helix, salt bridge, CMAP and Lennard-Jones refinement" (1 passage, 0 new); answer

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: I couldn't answer this from the available passages. For the CHARMM36m paper (W2555870966), only the abstract is in the collection. It says CHARMM36m is a refinement of CHARMM36 with improved accuracy for the polypeptide backbone conformational ensembles of intrinsically disordered peptides and proteins [W2555870966#000]. The abstract doesn't say which force field terms were changed. None of the other passages I searched describe the changes either.

The closest related passage is from a CHARMM36 validation paper. It says CHARMM36 itself differed from CHARMM22/CMAP in the peptide-backbone CMAP term and the χ1 and χ2 dihedral parameters, while keeping the same nonbond parameters [W2109154308#000]. That describes the earlier step, from CHARMM22/CMAP to CHARMM36, not the one you asked about.
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (The answer declines to say which force field terms changed (CMAP refit and modified TIP3P water LJ on hydrogens) and gives only unrelated information about the CHARMM22/CMAP to CHARMM36 step.)
- support: None (judge returned no valid verdict: The answer's claims check out against the passages:
- The CHARMM36m abstract describes a refinement of CHARMM36 with improved accuracy for the backbone conformational ensembles of intrinsically disord)
- steps: search "CHARMM36m modifications relative to CHARMM36 force field" (8 passages, 8 new); search "CHARMM36m refinement CMAP backbone, arginine, lysine, aspartate Lennard-Jones, NBFIX, tryptophan, TIP3P" (1 passage, 0 new); search "changes made to CMAP and Lennard-Jones parameters of C36m" (1 passage, 0 new); search "C36m updated backbone CMAP and side chain, NBFIX salt bridge" (8 passages, 8 new); open_paper "W2555870966" (1 section); search "CHARMM36m differs from CHARMM36 in backbone CMAP and Lennard-Jones parameters of arginine, lysine, aspartate, glutamate, with modified TIP3P" (8 passages, 6 new); search "C36m improved backbone CMAP potential and modified LJ parameters of arginine guanidinium carboxylate interactions" (8 passages, 6 new); answer

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: The papers I could search don't give a success rate for RFdiffusion binder design, so I can't answer the question.

The RFdiffusion paper (Watson et al., 2023) isn't in the collection as a full text. The only mentions are reference-list entries and one related-work sentence. That sentence says RFdiffusion generated novel protein-binder backbones "with successful experimental validation" [W4393118201#005]. It gives no number.
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.
- steps: search "RFdiffusion binder design experimental success rate" (8 passages, 8 new); search "Watson RFdiffusion de novo design of protein structure and function; binders experimentally validated success rate" (8 passages, 7 new); search "RFdiffusion high experimental success rate binders without high-throughput screening" (8 passages, 7 new); search "de novo binder design diffusion experimental hit rate percent of designs bind target" (8 passages, 5 new); answer

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: The passages I found don't give a dropout rate for SchNet. They describe its training setup without mentioning dropout:
- Adam optimizer with mini-batches of 32 examples [W2778051509#011][W2726670313#012].
- Learning rate decayed exponentially by a ratio of 0.96 every 100,000 steps [W2778051509#011][W2726670313#012].
- Early stopping on a validation set [W2778051509#011][W2726670313#012].
- An initial learning rate of 10^-3 and an exponential moving average over weights with decay rate 0.99 [W2726670313#012].

A third paper, SpookyNet, trained SchNet with Adam at a learning rate of 10^-4 and a batch size of 10, and it also doesn't mention dropout [W3159653252#028]. Either dropout wasn't used or it isn't stated in the passages I read.
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.
- steps: search "SchNet dropout rate training" (8 passages, 8 new); search "SchNet dropout regularization applied to interaction layers" (8 passages, 7 new); answer

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: DiffTRe doesn't differentiate through the MD simulation. It uses thermodynamic perturbation theory (trajectory reweighting) to get the gradient instead.

**What it does differently**
- It generates a reference trajectory with the reference potential parameters θ̂. It keeps only subsampled, decorrelated states and their reference potential energies [W3168247670#006][W3168247670#007].
- For each kept state it computes a weight w_i under the current parameters θ. These weights give reweighted observables ⟨O_k(U_θ)⟩, which give the loss [W3168247670#006].
- The gradient of the loss is taken by reverse-mode AD through the reweighting scheme. This "replaces the backward pass through the simulation" [W3168247670#006].
- The backward pass only passes through the potential-energy computation U_θ(S_i) of the retained states. The differentiation path is therefore independent of how the trajectory was generated [W3168247670#007][W3168247670#012].
- The effective sample size N_eff tracks the statistical error from reweighting. A new reference trajectory is generated only when N_eff falls below a threshold [W3168247670#007].
- The method applies to time-independent observables [W3168247670#001].

**What it buys**
- It avoids the exploding gradients that come from backpropagating through the whole simulation [W3168247670#001][W3168247670#003].
- Gradient computation is about 2 orders of magnitude faster than backpropagating through the simulation [W3168247670#001][W3168247670#003].
- Memory use is low, comparable to the adjoint method, because only the subsampled states and their energies are stored [W3168247670#007][W3168247670#003]. Direct reverse-mode AD, by contrast, needs excessive memory and is typically intractable for systems with more than about a hundred particles and a few hundred time steps [W3168247670#003].
- Decorrelated states from earlier trajectories can often be reused, which speeds up the forward pass [W3168247670#006].
- In the toy example, the rule-of-thumb speed-up estimates were 330 (sg) and 4 (s). These agreed with the measured values [W3168247670#012].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: correct (The answer matches all key points: no differentiation through the simulation, AD combined with reweighting, applies to time-independent observables, avoids exploding gradients, ~2 orders of magnitude faster, and memory comparable to the adjoint method; extra details are consistent.)
- support: None (judge returned no valid verdict: {"verdict": "supported", "reason": "Every claim in the answer is stated in the cited passages, including the rewe)

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: In DiffTRe, each weight is the ratio of a state's probability under the current potential parameters θ to its probability under the reference parameters θ̂, normalized over all retained states: wi = [pθ(Si)/pθ̂(Si)] / Σj [pθ(Sj)/pθ̂(Sj)] (Eq. 3) [W3168247670#005].

In the canonical ensemble the state probabilities are Boltzmann distributed, pθ(Si) ∼ exp(−βH(Si)). Here H is the sum of potential and kinetic energy, β = 1/(kB T), kB is the Boltzmann constant and T is the temperature [W3168247670#005].

The kinetic energy drops out because the ratio pθ/pθ̂ compares the same state under two potentials. The kinetic term is the same in numerator and denominator and cancels, so only potential energies remain. This is my reading of the cancellation the paper notes. The result is wi = exp(−β(Uθ(Si) − Uθ̂(Si))) / Σj exp(−β(Uθ(Sj) − Uθ̂(Sj))) (Eq. 4) [W3168247670#005].

When θ = θ̂, every weight is 1/N, which recovers the plain time average [W3168247670#005].
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (The answer gives the same normalized Boltzmann weights using only the potential energy difference, explains that the kinetic term cancels in the ratio, and notes that the weights are 1/N when θ equals the reference.)
- support: None (judge returned no valid verdict: The answer's claims all track the passage. Eq. 3 gives the weights as normalized probability ratios over the retained states. The passage says the Boltzmann distribution applies in the canonical ensem)

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe simulates a new reference trajectory when the effective sample size Neff falls below a predefined threshold N̄eff. Until then, it keeps reweighting the saved states, computing gradients and updating θ [W3168247670#007].

Neff is computed as Neff ≈ exp(−Σ wi ln wi). It drops when the current potential parameters θ differ a lot from the reference parameters θ̂ [W3168247670#006]. The new trajectory is then sampled with the current θ as the new θ̂. It starts from the last generated state S_N [W3168247670#007]. Every reference trajectory gets at least one θ update, because Neff = N at the start [W3168247670#007].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (The answer matches the reference: a new trajectory is run when N_eff falls below a threshold, using the same formula, with the current parameters, and starting from the last state of the old trajectory.)
- support: None (judge returned no valid verdict: The answer's claims match the cited passages.

- **Trigger for a new trajectory:** The answer says a new reference trajectory is simulated when Neff falls below N̄eff, and that until then DiffTRe keep)

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The DiffTRe diamond potential, a DimeNet++ model, was trained on the experimental elastic stiffness tensor of diamond. That tensor has three distinct moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. The training also assumed a stress-free state (σ = 0) at zero strain [W3168247670#013].

The simulations matched the experimental density (3512 kg/m3) and temperature (298.15 K) [W3168247670#013]. Density functional theory (DFT) data were not used for training. They served only as a comparison for the stress-strain curve [W3168247670#014].
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer matches the reference on the experimental elastic stiffness tensor, the three moduli (C11=1079, C12=124, C44=578 GPa) and the stress-free state at zero strain; the extra details about density, temperature and DFT do not contradict it.)
- support: supported (The cited passages state each claim: the DimeNet++ model, the three moduli values, the stress-free assumption, the matched density and temperature, and DFT appearing only as a comparison for the stress-strain curve. The loss is defined solely by experimental data, so DFT was not used for training.)

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: DiffTRe's coarse-grained water model got the self-diffusion coefficient wrong. The model gave D = 10.91 μm²/ms, against an experimental value of 2.2 μm²/ms [W3168247670#017]. The other held-out observable, the tetrahedral order parameter q, matched well: about 0.569 against 0.576 experimentally [W3168247670#017].

The paper explains the error by the smoother potential energy surfaces of coarse-grained models, which speed up dynamics compared with atomistic models [W3168247670#017]. It adds that diffusion coefficients fall as the number of interaction sites rises. The learned model may act like a single-site model early in training and become more like a multi-site model as it learns 3-body interactions [W3168247670#017]. A single-site tabulated potential from iterative Boltzmann inversion gave an even larger D of 14.15 μm²/ms [W3168247670#017].

The paper also says dynamical properties cannot be used as training targets. The reweighting scheme does not depend on the order of states in the trajectory [W3168247670#019].
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (The answer identifies the self-diffusion coefficient (10.91 vs 2.2 μm²/ms) as wrong, attributes it to smoother coarse-grained potential energy surfaces speeding up dynamics, and notes that the tetrahedral order parameter matched, which agrees with the reference.)
- support: supported (Every claim in the answer matches the cited passages: the D and q values, the explanation via smoother PESs, the site-count trend, the single-site IBI value of 14.15, and the limitation that reweighting is invariant to state sequence so dynamical properties cannot be targets.)

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: Not directly. DiffTRe is designed to bypass differentiation through the MD simulation "for time-independent observables" [W3168247670#001]. It works by reweighting states from a reference trajectory, so the observables must be ensemble averages that can be computed from those states, such as RDF, ADF, pressure and the stiffness tensor [W3168247670#006][W3168247670#023]. A diffusion coefficient depends on dynamics, so it doesn't fit that scheme. The passages I read don't say how it would be handled as a target.

In the paper, the self-diffusion coefficient of the coarse-grained water model was only a held-out check. It was not a training target. The learned model predicted D = 10.91 μm2/ms, against the experimental 2.2 μm2/ms [W3168247670#017]. The authors attribute this to coarse-grained models having smoother potential energy surfaces and therefore faster dynamics [W3168247670#017].

To fit a diffusion coefficient you would probably need a different approach, such as backpropagating through the simulation. The paper notes that this approach faces numerical and computational challenges, including exploding gradients [W3168247670#001].
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: correct (The answer says DiffTRe works only for time-independent observables via reweighting and that a dynamical property like diffusion cannot be a target, matching the reference; the added detail about the held-out check and backpropagation is consistent with it.)
- support: partial (Most claims are supported, but "A diffusion coefficient depends on dynamics, so it doesn't fit that scheme" is the answerer's own inference and the passages don't say it, and the claim that observables must be ensemble averages computable from reweighted states is only loosely supported, since the passages mention the stiffness tensor as not merely an average of instantaneous quantities.)

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: The passages I found don't mention SchNet's C20 force field specifically, so this answer covers DFT-style bottom-up training in general.

The DiffTRe authors see two limits on training from DFT data. The first is that the model's accuracy is capped by the quality of the data-generating simulation [W3168247670#002]. State-of-the-art NN potentials already reach the accuracy limit imposed by DFT. Any remaining deviation from experiment is then attributed to uncertainty in DFT itself, which is sensitive to the functional used [W3168247670#002]. The second is that highly precise, broad data sets are hard to get. More accurate methods such as CCSD(T) cost much more, and for large systems like macromolecules quantum mechanical data sets will stay intractable [W3168247670#002]. They name this limited availability of precise, broad data sets as the main obstacle to bottom-up learning [W3168247670#003].

Instead, they train top-down on experimental data. The DiffTRe method matches time-independent experimental observables, using reweighting so it doesn't have to backpropagate through the MD simulation [W3168247670#001]. For diamond, they train a DimeNet++ model on the experimental stiffness tensor, and for coarse-grained water on pressure plus radial and angular distribution functions [W3168247670#004].
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: correct (The answer identifies both key limits (accuracy capped by the reference DFT method, and limited availability of precise, broad quantum data sets) and that DiffTRe trains top-down on experimental observables, matching the reference.)
- support: None (judge returned no valid verdict: The answer's claims all trace to the cited passages.

- **Opening caveat:** it is a statement about the search, not a claim needing support.
- **First limit:** accuracy is capped by the data-generatin)
- steps: search "DiffTRe differentiable trajectory reweighting limitation of training on DFT data, experimental data" (8 passages, 8 new); search "bottom-up NN potentials limited by accuracy of DFT reference; SchNet C20" (8 passages, 6 new); answer

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: DiffTRe's diamond model uses the original Stillinger-Weber potential, which was parametrized for silicon, as its prior. The authors rescaled its length and energy scales to σSW = 0.14 nm and εSW = 200 kJ/mol to reflect the smaller size of carbon atoms [W3168247670#013].

The neural network potential paper that used silicon as its test system is Behler and Parrinello's "Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces" (2007). It builds an NN-based many-body potential for bulk silicon [W2025444507#001].

Other papers in the collection also fit silicon neural network potentials. I chose the Behler–Parrinello paper because it is the one that introduces the method and demonstrates it on bulk silicon.
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: correct (Identifies the Stillinger-Weber potential parametrized for silicon, rescaled for carbon, and the Behler-Parrinello 2007 paper using bulk silicon as its test system, matching the reference.)
- support: None (judge returned no valid verdict: {"verdict": "partial", "reason": "The DiffTRe/Stillinger-Weber rescaling and the bulk-silicon NN potential are supported, but the pass)
- steps: search "DiffTRe diamond model empirical potential" (8 passages, 8 new); search "neural network potential test system silicon" (8 passages, 8 new); answer

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: DiffTRe uses DimeNet++, a state-of-the-art graph neural network potential. In its diamond and coarse-grained water examples, U_model is a graph neural network operating iteratively on the atomic graph defined by the pairwise distance matrix D [W3168247670#007]. The paper says it trains DimeNet++ for both systems [W3168247670#004].

The NequIP paper does not name DimeNet++. It does say that NequIP significantly outperforms invariant GNN-IPs such as SchNet and DimeNet on MD-17 [W4225405705#010]. DimeNet++ is an invariant, distance-based model of the DimeNet family, but that grouping is my inference, not something the passages state.

NequIP also outperforms all the other methods compared, including kernel methods and other equivariant networks [W4225405705#011]. The authors link its gains to its E(3)-equivariant convolution. Going from l=0 to l=1 gives a large improvement, which they take to show the importance of equivariance [W4225405705#011].
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: correct (The answer correctly identifies DimeNet++ for both diamond and water systems and states that NequIP significantly outperforms invariant GNN potentials such as SchNet and DimeNet on MD-17, matching the reference; the extra details are consistent.)
- support: None (judge returned no valid verdict: )
- steps: search "DiffTRe differentiable trajectory reweighting graph neural network potential" (8 passages, 8 new); search "NequIP MD-17 comparison with other graph neural network potentials accuracy" (8 passages, 8 new); answer

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: In DiffTRe, U_prior is not a Bayesian prior. It does not impose a persistent bias on the learnable parameters in the small-data regime. If it conflicts with the data, the learned part U_model_θ simply corrects for it during optimization [W3168247670#008]. The prior has three roles:

- **Trajectory generation:** it controls how trajectories are generated at the start of the optimization, since DiffTRe has no pre-computed data set [W3168247670#008]. This also shapes how informative the gradient is early in training [W3168247670#010].
- **Easier learning problem:** the model only has to learn the difference between U_prior and the optimal potential, rather than the potential from scratch [W3168247670#008].
- **Physics-informed initialization:** a well-chosen prior speeds up convergence. It encodes a-priori known properties of the system, such as the Pauli exclusion principle [W3168247670#008].

The authors also list the need for a reasonably chosen prior potential as a limitation of DiffTRe [W3168247670#019].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: correct (The answer covers the key points: the prior controls which trajectories are generated early (and thus gradient informativeness), provides a physics-informed starting point with the network learning a correction, and is overridden by data if it conflicts; it omits only specific examples like LJ/Stillinger-Weber.)
- support: None (judge returned no valid verdict: Checking each claim against the passages:

- "Not a Bayesian prior ... model corrects for it": supported by #008.
- Trajectory generation at the start: supported by #008.
- Shaping gradient informativ)

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The DiffTRe paper (W3168247670) text that I could read never states the number of GPU hours used to train the diamond potential. It says the diamond DimeNet++ model was trained for about 700 update steps and refers to wall-clock time per update in Supplementary Fig. 5a, but that figure's content isn't in the passages. No other retrieved paper gives this number.
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.
- steps: search "DiffTRe diamond potential training GPU hours" (8 passages, 8 new); search "diamond model training took hours on GPU, computational cost, stiffness tensor" (8 passages, 7 new); search "total training time diamond DiffTRe GPU hours NVIDIA wall-clock" (10 passages, 4 new); search "diamond training required GPU hours; water model required GPU hours" (10 passages, 1 new); open_paper "W3168247670" (15 sections); read_around "W3168247670#019" (2 passages, 1 new); search "DiffTRe trained in hours on a single GPU; total compute time for diamond and water" (8 passages, 4 new); search "DiffTRe diamond potential training took GPU hours compared to" (8 passages, 8 new); give_up

