# Answer eval: claude-sonnet-5-5

- **Generator:** `{"name": "agent", "provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "agent-v3", "tools": ["search", "read_around", "open_paper"], "max_turns": 8, "token_budget": 100000}`
- **Judge:** `{"provider": "anthropic", "model": "claude-sonnet-5-5", "prompt": "judge-v1", "max_tokens": 1500}`
- **Retrieval:** bm25, top 5 from pymupdf_w400_o60
- **Questions:** 32 (split: dev, file sha1 9e6de1d92dea)
- **Cost:** generator $0.592, judge $0.343

## Overall

| metric | value | n |
|---|---|---|
| Correct (judge vs your reference) | 0.88 [0.78, 0.97] | 29 |
| Supported by its citations | 0.91 [0.84, 0.98] | 28 |
| Cites your evidence | 0.78 [0.63, 0.93] | 27 |
| Evidence was retrieved | 0.78 [0.63, 0.93] | 27 |
| Cites passages it wasn't given (lower is better) | 0.00 [0.00, 0.00] | 28 |
| Declines when unanswerable | 1.00 [1.00, 1.00] | 3 |
| Declines although answerable (lower is better) | 0.03 [0.00, 0.10] | 29 |

Correct when the evidence was retrieved: 0.95 (n=21)

Correct when no evidence was retrieved: 0.83 (n=6)

## Effort per question (mean)

2.7 model calls, 2.1 tool calls (2.0 searches), 8.4 passages read, 15,511 input tokens, $0.0185 per question, 4.3 s. Gave up on 12%, ran out of budget on 0%.

## Answers

**q001** (lookup): What test system did Behler and Parrinello use to demonstrate their neural network potential?
- answer: Behler and Parrinello demonstrated their neural network potential on bulk silicon. They built an NN-based many-body potential for it and compared it with empirical potentials and DFT [W2025444507#000][W2025444507#001]. They report that the potential works well in the solid semiconducting and liquid metallic phases. It also reproduces the small energy differences between the high-pressure crystalline phases of Si [W2025444507#001].
- reference: Bulk silicon; the network potential was compared against DFT reference calculations.
- correctness: correct (The answer identifies bulk silicon as the test system and mentions comparison with DFT, matching the reference; the additional details are consistent with the Behler-Parrinello work.)
- support: supported (All claims match the passages: demonstration on bulk silicon, NN-based many-body potential, comparison with empirical potentials and DFT, good performance in solid semiconducting and liquid metallic phases, and reproduction of small energy differences between high-pressure crystalline phases.)
- steps: search "Behler Parrinello neural network potential test system" (5 passages, 5 new); search "Behler and Parrinello original 2007 neural network silicon bulk demonstrated" (5 passages, 3 new); search "Generalized neural-network representation of high-dimensional potential-energy surfaces" (5 passages, 4 new); answer

**q002** (lookup): What is the functional form of the cutoff function in the original high-dimensional neural network potential?
- answer: In the original high-dimensional neural network potential (Behler and Parrinello, 2007), the cutoff function is a cosine that goes smoothly to zero at the cutoff radius Rc. It is fc(Rij) = 0.5·[cos(π·Rij/Rc) + 1] for Rij ≤ Rc, and fc(Rij) = 0 for Rij > Rc [W2025444507#004]. That paper's own text is garbled and the π is missing from its Eq. 3. I took the π from a later paper that restates the same function [W3000291311#004]. Beyond Rc the function has zero value and zero slope. The 2007 paper used Rc = 6 Å [W2025444507#005].
- reference: A cosine cutoff: f_c(R) = 0.5 [cos(pi R / R_c) + 1] for R <= R_c, and 0 beyond the cutoff radius R_c.
- correctness: correct (The answer gives the same cosine cutoff, f_c = 0.5[cos(πR/Rc)+1] for R ≤ Rc and 0 beyond, matching the reference; the extra details (zero slope, Rc = 6 Å) do not contradict it.)
- support: supported (The cutoff form, the missing π in the 2007 text, the π in the 2020 restatement, the zero value and slope beyond Rc, and the 6 Å cutoff are all stated in the cited passages.)

**q003** (lookup): How are the total energy and the atomic contributions related in a high-dimensional neural network potential?
- answer: In a high-dimensional neural network potential (HDNNP), the total energy E is the sum of atomic energy contributions: E = Σ_i E_i [W2025444507#003][W4312043350#015].

Each atom i has its own atomic ("standard") neural network, called a subnet S_i. It takes symmetry-function values that describe the atom's local environment and outputs E_i [W2025444507#003]. All subnets have the same structure and weights for a given element, so swapping two identical atoms leaves E unchanged [W2025444507#003]. In ANI-1, one network is used per element [W2541404351#007].

The sum lets the potential be applied to systems of different sizes. It also lets the computation scale nearly linearly with the number of atoms [W2025444507#003][W2541404351#007].
- reference: The total energy is a sum of atomic energies, each predicted by an atomic neural network from that atom's local environment within a cutoff.
- correctness: correct (The answer states total energy is the sum of atomic energies, each output by an atomic NN from symmetry-function descriptors of the atom's local environment, matching the reference; the cutoff is implicit in 'local environment'.)
- support: partial (Most claims are supported, but the passage says near-linear scaling is with added cores or GPUs up to the number of atoms, not with the number of atoms as the answer states, and 'for a given element' is not in the 2007 passage.)

**q004** (lookup): Under which symmetry group are NequIP's internal features equivariant, and how are they built?
- answer: NequIP's internal features are equivariant to E(3), the group of rotations, reflections and translations in 3D. The output energy is invariant under these operations [W4225405705#005].

**How the features are built:**
- Each atom carries features that are geometric tensors: scalars, vectors and higher-order tensors. Formally these are direct sums of irreducible representations of O(3), indexed by rotation order l = 0, 1, 2, … and parity p ∈ {1, −1} [W4225405705#006].
- The layers build on Tensor-Field Networks, with primitives implemented in e3nn [W4225405705#006].
- The convolution filters are products of a learnable radial function and spherical harmonics: F(r_ij) = R(r_ij) Y_m^(l)(r̂_ij). The spherical harmonics are equivariant under SO(3), and all learnable weights sit in the rotation-invariant radial function R [W4225405705#006]. R is a small MLP acting on interatomic distances expressed in a chosen basis [W4225405705#006].
- Translation invariance comes from the filters acting on relative distance vectors. Permutation invariance comes from summing over neighbours [W4225405705#006].
- Combining features with filters uses tensor products of irreps. These are equivariant operations that follow the selection rules |l1−l2| ≤ l_out ≤ |l1+l2| and p_out = p1·p2 [W4319162181#004]. The tensor-product layers use Clebsch-Gordan coefficients [W4310273071#010].
- reference: E(3); features are geometric tensors indexed by irreducible representations of O(3), combined by tensor products with spherical harmonics of relative position vectors.
- correctness: correct (Answer states E(3) equivariance, features as geometric tensors indexed by O(3) irreps, and construction via tensor products with spherical harmonics of relative position vectors, matching the reference.)
- support: supported (All claims trace to the cited passages; the only stretch is applying the TFN Clebsch-Gordan statement to NequIP, which the passages link through NequIP building on TFN.)

**q005** (comparison): How does NequIP's handling of rotational symmetry differ from the Behler-Parrinello symmetry functions?
- answer: NequIP and Behler-Parrinello (BP) networks differ in where rotational symmetry is built in. BP networks make their input features invariant. NequIP keeps internal features equivariant.

**Behler-Parrinello.** The atom-centered symmetry functions turn each local atomic environment into numeric vectors that are rotationally and translationally invariant [W3000291311#028]. They do this using only distances and angles between neighbors [W2988055229#031]. A dense network then maps these features to an atomic energy, which is invariant by construction [W2988055229#031]. Because the fingerprints carry no directional information, they can't be regressed directly onto Cartesian force vectors. Forces are instead obtained by differentiating the predicted energy [W2976347420#003].

**NequIP.** Its output energy is invariant, but its internal features are geometric tensors (scalars, vectors and higher-order tensors) that are equivariant to rotation and reflection [W4225405705#005]. These features are labeled by a rotation order l and a parity p, which together index irreducible representations of O(3) [W4225405705#006]. The convolutions are equivariant: if a feature is rotated, the convolution output transforms accordingly [W4225405705#006]. To achieve this, the filters are constrained to be a learnable radial function times spherical harmonics, F(r_ij) = R(r_ij) Y_m^(l)(r̂_ij). All learnable weights sit in the rotationally invariant radial function [W4225405705#006].

The NequIP paper presents this as its core difference from invariant-feature approaches, and its authors attribute the improvements to using equivariant instead of invariant representations [W4225405705#005][W4225405705#022].
- reference: Behler-Parrinello uses fixed, hand-designed invariant descriptors (scalars) of the environment; NequIP learns equivariant features that carry vector/tensor information through message passing, and only the final energy is invariant.
- correctness: correct (The answer captures the key facts: BP uses invariant symmetry-function descriptors built from distances and angles, while NequIP keeps equivariant tensor features through convolutions with an invariant final energy; it does not explicitly say the descriptors are hand-designed or that NequIP's features are learned, but this is implied.)
- support: supported (Each claim about Behler-Parrinello invariance, force-by-differentiation, and NequIP's equivariant features, filters and authors' attribution is stated in the cited passages.)
- steps: search "NequIP E(3)-equivariant rotation equivariance compared to Behler-Parrinello symmetry functions invariant descriptors" (5 passages, 5 new); search "Behler-Parrinello atom-centered symmetry functions rotation invariance" (5 passages, 5 new); answer

**q007** (comparison): What features does the Nequip architecture use, that are also used by schnet?
- answer: NequIP and SchNet share several features, based on the passages I read.

- **Invariant radial filter on interatomic distances:** SchNet feeds interatomic distances d_ij, expanded in radial basis functions, into dense layers to produce rotationally invariant filter weights [W2726670313#009]. NequIP's radial function R(r_ij) is also a small MLP on interatomic distances expressed in a basis. The basis is Bessel functions with a polynomial envelope. All of the filter's learnable weights sit in this invariant function [W4225405705#007].
- **Convolution inside stacked interaction blocks:** SchNet uses a continuous-filter convolution in each of three interaction blocks, which it uses to build many-body representations [W2726670313#009]. NequIP likewise refines atomic features through a series of interaction blocks that contain a convolution [W4225405705#011].
- **Two-body message passing within a cutoff:** One paper groups SchNet and NequIP as GNN interatomic potentials that use only two-body message-passing functions [W4391631778#024]. NequIP restricts interactions to atoms inside a local cutoff radius [W4225405705#007].
- **Energy-conserving forces:** SchNet's force predictions conserve energy [W2726670313#007]. In NequIP, forces are computed as negative gradients of the predicted energy with respect to atomic positions [W4391631778#007].
- **Scalar-only limit:** If NequIP drops all higher-order interactions beyond 0⊗0→0, it becomes a conventional GNN-IP with invariant convolutions over scalar features, "similar to e.g. SchNet" [W4225405705#007].

The main difference is that NequIP adds E(3)-equivariant higher-order tensor features. SchNet's filters are invariant only [W4391631778#024].
- reference: Several design choices come from SchNet. The initial atom features are a trainable embedding of the atomic number (one-hot encoded). Atoms then pass through a stack of interaction blocks that do continuous convolutions over neighbors within a cutoff. In those convolutions the learnable filter weights are an MLP of the interatomic distance expanded in a radial basis: Gaussians in SchNet, Bessel functions with an envelope in NequIP. The output is per-atom energies summed to a total energy, and forces are its negative gradient. The difference is that NequIP also multiplies the radial part by spherical harmonics of the bond direction. If only l = 0 (scalar) features are kept, NequIP reduces to a SchNet-style invariant network.
- correctness: partial (The answer covers the radial MLP filters, interaction blocks with convolutions within a cutoff, forces as energy gradients, and the scalar-only limit, but it never mentions the one-hot atomic-number embedding as initial features or the per-atom energies summed to a total energy.)
- support: supported (Each claim about SchNet and NequIP, including the radial filters, interaction blocks, two-body message passing, force computation, scalar-only limit and the equivariant-versus-invariant difference, is stated in or follows from the cited passages.)
- steps: search "NequIP architecture compared to SchNet features" (5 passages, 5 new); search "SchNet continuous-filter convolution interatomic distances radial basis" (5 passages, 5 new); answer

**q008** (lookup): What does Nequip do as a first step in the architecture?
- answer: NequIP starts with an embedding step. It builds the initial atomic feature from the atomic number Z_i alone, written as a one-hot encoding. A trainable self-interaction layer produces that feature, following SchNet [W4225405705#009]. The interaction blocks and the output block come after this embedding [W4225405705#009].
- reference: It embeds each atom's chemical species. The atomic number Z_i, one-hot encoded, goes through a trainable self-interaction (linear) layer. This gives the initial per-atom features, which are scalar (l = 0) only. The embedding follows SchNet. Higher-order tensor features first appear in the interaction blocks.
- correctness: partial (The answer correctly describes the one-hot atomic number embedding, the trainable self-interaction layer and the SchNet reference, but it omits that the initial features are scalar (l=0) only and that higher-order tensor features first appear in the interaction blocks.)
- support: supported (All claims (embedding from one-hot Z_i alone, trainable self-interaction layer, following SchNet, followed by interaction blocks and output block) are stated in the passage.)

**q009** (lookup): What datasets is Nequip tested on?
- answer: In the NequIP paper, NequIP is tested on the following datasets [W4225405705#010]:

- **MD-17:** a set of small organic molecules. NequIP is benchmarked on both the original and the revised MD-17 versions [W4225405705#010]. The original has eight molecules at the PBE+vdW-TS level, and the revised version is a recomputed set at the PBE/def2-SVP level [W4225405705#023].
- **Small molecules at CCSD/CCSD(T) accuracy:** aspirin (CCSD), plus benzene, malondialdehyde, toluene and ethanol (CCSD(T)) [W4225405705#023].
- **Extended systems with periodic boundary conditions:**
  - water in different phases (liquid water and ice) [W4225405705#010][W4225405705#023];
  - a chemical reaction at a solid/gas interface [W4225405705#010];
  - amorphous lithium phosphate (Li4P2O7) [W4225405705#010][W4225405705#037];
  - a lithium superionic conductor [W4225405705#010].

A separate paper on Allegro also used the NequIP code, with revised MD-17, 3BPA, QM9 and Li3PO4 as reference sets [W4319162181#024]. That passage describes Allegro's experiments, so I can't tell from it whether NequIP itself was evaluated on 3BPA, QM9 or Li3PO4.
- reference: 1) MD-17 small organic molecules, both the original DFT version and the revised MD-17 (rMD17). 2) Small molecules at quantum-chemical accuracy: aspirin at CCSD; benzene, malonaldehyde, toluene and
   ethanol at CCSD(T).
3) Periodic systems:
   - liquid water and ice
   - a chemical reaction at a solid/gas interface (formate decomposition on a copper surface)
   - amorphous lithium phosphate (Li4P2O7)
   - a lithium superionic conductor (Li6.75P3S11, "LiPS")
- correctness: correct (The answer lists all the reference datasets: MD-17 and rMD17, the CCSD/CCSD(T) molecules, and the periodic systems (water/ice, solid/gas interface reaction, Li4P2O7, lithium superionic conductor). Its extra details and the Allegro caveat do not contradict the reference.)
- support: supported (Every claim matches the cited passages: the NequIP dataset list and details come from #010 and #023, Li4P2O7 is tied to NequIP in #037, and the Allegro passage #024 lists the NequIP code and the four reference sets, with an appropriately hedged caveat.)

**q010** (lookup): Which other models is Nequip compared to in the original Nequip paper on MD-17?
- answer: The NequIP paper benchmarks on both the original and the revised MD-17 data sets. It compares against several groups of published models [W4225405705#010].

- **Invariant GNN potentials:** SchNet and DimeNet.
- **Shallow neural networks:** ANI.
- **Kernel-based approaches:** GAP, FCHL19/GPR and sGDML.
- **Other methods:** ACE, SpookyNet and GemNet.
- **Other equivariant networks:** PaiNN, NewtonNet and UNiTE.

The authors say PaiNN and NewtonNet are lmax = 1-only versions of equivariant networks. They report that NequIP outperforms all the other methods [W4225405705#011].

The ACE, GAP and ANI results on revised MD-17 are taken from another paper's reported numbers [W4225405705#010]. DeepMD appears only in the separate water and ice comparison, not in the MD-17 tables [W4225405705#014].
- reference: Invariant GNN potentials: SchNet and DimeNet. A shallow neural network: ANI. Kernel methods: GAP, FCHL19/GPR and sGDML. Other methods: ACE, SpookyNet and GemNet. Other equivariant networks: PaiNN, NewtonNet and UNiTE. The paper notes that PaiNN and NewtonNet are restricted to l_max = 1. Results for ACE, GAP and ANI on revised MD-17 are taken from another paper (Kovács et al.), not retrained by the authors. NequIP reports the best accuracy of all of them.
- correctness: correct (The answer lists all the same models in the same groupings as the reference, notes PaiNN/NewtonNet are lmax=1, that ACE/GAP/ANI results come from another paper, and that NequIP outperforms all; the DeepMD remark is extra and not contradictory.)
- support: partial (The benchmark scope, model groups, lmax = 1 remark, outperformance claim and the [43] source for ACE/GAP/ANI are all stated in the passages, but the claim that DeepMD appears only in the water and ice comparison and not in the MD-17 tables is not stated. Passage 014 never names water and ice, and its table headers are only partly visible.)

**q011** (lookup): How does SchNet turn an interatomic distance into the input of its filter network?
- answer: SchNet feeds the filter network the interatomic distance d_ij = ‖r_i − r_j‖. Using distances rather than positions makes the filters rotationally invariant [W2726670313#009].

The distance is first expanded in radial basis functions, e_k(r_i − r_j) = exp(−γ‖d_ij − μ_k‖²). The centers μ_k run from 0 Å to 30 Å in steps of 0.1 Å, and γ = 10 Å. This expansion keeps the initial filters from being highly correlated, which would otherwise cause a plateau at the start of training [W2726670313#009].

The expanded distances then pass through two dense layers with softplus activations. These layers produce the filter weight W(r_i − r_j) [W2726670313#009].
- reference: It expands the distance in a basis of Gaussians, e_k = exp(-gamma (|r_j - r_i| - mu_k)^2), with centers mu_k on a uniform grid from zero to the distance cutoff. Grid spacing and gamma are both set to 0.1 Angstrom. The expansion decorrelates the filter values, which improves the conditioning of the optimization.
- correctness: partial (It correctly describes the Gaussian expansion and the decorrelation purpose, but gives a 0–30 Å range and γ = 10 Å, whereas the reference gives a grid from zero to the cutoff with spacing and γ both 0.1 Å.)
- support: supported (Every claim in the answer (distance input giving rotational invariance, RBF expansion with centers 0–30 Å every 0.1 Å and γ=10 Å, avoiding correlated filters and the initial plateau, and two dense softplus layers producing W) is stated in the cited passage.)

**q012** (lookup): Which activation function does SchNet use, and why does that matter for force fields?
- answer: SchNet uses a shifted softplus, ssp(x) = ln(0.5e^x + 0.5), as its non-linearity throughout the network [W2726670313#010].

This matters for force fields for three reasons:

- **Differentiability:** Forces are obtained as the negative gradient of the predicted energy with respect to atom positions. This makes the force field energy-conserving by construction. Training on a force loss then requires the model to be at least twice differentiable [W2726670313#010].
- **Smoothness:** The shifted softplus has infinite order of continuity. It therefore gives a smooth potential energy surface, smooth force fields and smooth second derivatives. Those derivatives are needed for training with forces and for calculating vibrational modes [W2726670313#010][W2778051509#006].
- **Convergence:** The shift makes ssp(0) = 0, which improves the network's convergence [W2726670313#010].
- reference: A shifted softplus, ssp(x) = ln(0.5 e^x + 0.5). The shift makes ssp(0) = 0 and improves convergence, and because it is infinitely differentiable the learned energy surface is smooth, giving smooth forces and the second derivatives needed for training on forces and for vibrational modes.
- correctness: correct (The answer gives the same shifted softplus formula and covers the ssp(0)=0 convergence benefit, smoothness from infinite differentiability, and the need for second derivatives in force training and vibrational modes; the extra detail on energy conservation is correct.)
- support: supported (Every claim (ssp definition, force as energy gradient, twice-differentiability, infinite continuity, smooth PES/forces/second derivatives, vibrational modes, ssp(0)=0 and convergence) appears in the cited passages.)

**q013** (lookup): Why can't SchNet use ordinary convolutional layers like image models do?
- answer: SchNet can't use ordinary convolutional layers because they need the data on a regular grid, and atoms in a molecule aren't on one.

Ordinary convolutional layers work on discretized signals such as image pixels, video frames or audio. For those, the filter can be defined on the same grid as the data. This isn't possible for unevenly spaced inputs such as atom positions [W2726670313#006].

Discretizing would also lose information. The precise atom positions carry essential physical information that would be lost if discretized [W2726670313#001]. A discrete filter can't capture subtle positional changes of atoms, which gives discontinuous energy predictions [W2726670313#005].

Re-sampling the molecule onto a grid is a possible workaround. But choosing an interpolation scheme is a challenge in itself, and it may need a large number of grid points [W2726670313#006].

SchNet instead uses continuous-filter convolutions. A neural network generates the filter values from the relative position, so atoms can sit at arbitrary positions [W2726670313#006].
- reference: Atoms sit at arbitrary positions rather than on a regular grid like pixels, so a fixed filter tensor can't be used. SchNet uses continuous-filter convolutions, where a filter-generating network computes the filter values from the atoms' relative positions.
- correctness: correct (The answer states that ordinary convolutions require regular grids while atoms sit at arbitrary positions, and that SchNet uses continuous-filter convolutions in which a network generates filter values from relative positions, matching the reference.)
- support: supported (Every claim is stated in or follows directly from the cited passages (#006, #001, #005), including the relative-position filter via W(ri − rj).)

**q014** (lookup): What cutoff radius did SchNet use when learning formation energies of bulk crystals?
- answer: SchNet used a distance cutoff of rcut = 5 Å when predicting formation energies for bulk crystals from the Materials Project. Two examples that would have contained isolated atoms at this cutoff were discarded from the data set [W2778051509#014].
- reference: 5 Angstrom, on the Materials Project data. Two structures that would contain isolated atoms at that cutoff were dropped. (For the small QM9 and MD17 molecules no cutoff was used.)
- correctness: correct (The answer states a 5 Å cutoff on Materials Project data and that two structures with isolated atoms were discarded, matching the reference; omission of the QM9/MD17 note is minor.)
- support: supported (The passage states SchNet predicts formation energies for MP bulk crystals, sets rcut = 5 Å, and discards two examples that would include isolated atoms at that setting.)

**q015** (lookup): How does SchNet make sure its predicted forces conserve energy?
- answer: SchNet gets energy-conserving forces by predicting the energy and then differentiating it. The force on atom i is the negative gradient of the predicted energy with respect to that atom's position: F_i = −∂E/∂r_i. The SchNet paper notes that, following Chmiela et al., this gives an energy-conserving force field by construction [W2726670313#010][W2778051509#010]. Because the energy is rotationally invariant, the forces are also rotationally equivariant [W2726670313#010].

Training the force model this way needs the network to be at least twice differentiable. For that reason SchNet uses a shifted softplus non-linearity, which gives a smooth potential energy surface [W2726670313#010]. The forces cost a full forward and backward pass through the energy model, so computing them takes about twice the computation time [W2726670313#010].
- reference: Forces are not predicted directly: they are the negative gradient of the predicted energy with respect to the atomic positions, F_i = -dE/dr_i. With a rotationally invariant energy model this gives rotationally equivariant forces and an energy-conserving force field.
- correctness: correct (The answer states forces are the negative gradient of the predicted energy w.r.t. positions, F_i = -∂E/∂r_i, giving an energy-conserving field and rotationally equivariant forces from the invariant energy, matching the reference; extra details on softplus and compute cost are consistent.)
- support: supported (All claims are stated in the passages; only the causal link between the twice-differentiable requirement and the softplus choice is slightly inferred, since the passage gives smoothness of the potential energy surface as the stated reason.)

**q016** (comparison): SchNet and NequIP both use continuous convolutions over neighboring atoms. What do their filters see about the neighbors, and how does that change the features they can build?
- answer: SchNet's filters see only the interatomic distance to each neighbor. NequIP's filters see the full relative position vector, meaning the distance and the direction.

**SchNet.** The filter-generating network takes only the interatomic distance d_ij = ||r_i − r_j||, expanded in radial basis functions. This makes the filters rotationally invariant [W2726670313#009]. Each filter emphasizes certain ranges of interatomic distances. The interaction block can therefore update an atom's representation according to its radial environment [W2726670313#009]. Stacking three interaction blocks gives complex many-body representations, but the features remain invariant scalars [W2726670313#009].

**NequIP.** The filter is F(r_ij) = R(r_ij) Y_m^(l)(r̂_ij). R is a learnable radial function of the distance, and Y is a spherical harmonic of the unit direction vector [W4225405705#006]. All learnable weights sit in the rotationally invariant radial part R [W4225405705#007]. The filter is combined with the neighbor's feature through a Clebsch-Gordan tensor product. This gives output orders |l_i − l_f| ≤ l_o ≤ |l_i + l_f|, capped at l_max [W4225405705#007]. Atom features are therefore tensors of different orders (scalars, vectors and higher-order tensors) that transform equivariantly under rotation and parity [W4225405705#006].

**Consequence.** Keeping only the 0⊗0→0 interaction gives a conventional invariant GNN with scalar features, similar to SchNet [W4225405705#007]. Because NequIP's filters also carry direction, it can build geometric, directional features. In the MD-17 experiments, going from l = 0 to l = 1 gave a significant improvement, which the authors take to show the crucial role of equivariance, and higher l helped further [W4225405705#011].
- reference: SchNet's filters only see interatomic distances (expanded in Gaussians), so they are rotationally invariant and the features stay scalars. NequIP's filters also use the direction to the neighbor, so its internal features are geometric tensors that are equivariant to rotation; restricted to scalars it reduces to a SchNet-style invariant network.
- correctness: correct (The answer matches the reference: SchNet filters use only distances (Gaussian/radial basis) giving invariant scalar features; NequIP filters also use direction, giving equivariant geometric tensor features, and restricting to scalars reduces to a SchNet-like invariant network.)
- support: supported (Every claim matches the cited passages: SchNet's distance-only RBF filters and invariance, NequIP's R(r)·Y(r̂) filter, the Clebsch-Gordan output orders, the 0⊗0→0 similarity to SchNet, and the l=0→1 MD-17 gain. The only extra is the mild inference that directional features can be built.)
- steps: search "SchNet continuous-filter convolutional layers interatomic distances filter-generating network" (5 passages, 5 new); search "NequIP equivariant convolution filters radial function spherical harmonics tensor product" (5 passages, 5 new); answer

**q017** (multihop): Which kernel method did the SchNet paper compare against on MD17, and how does NequIP do against kernel methods of that kind?
- answer: The SchNet paper compared against gradient-domain machine learning (GDML), a kernel method. It reported GDML alongside DTNN for reference, using training sets of N=1,000 and N=50,000 on MD17 [W2778051509#017].

NequIP does better than kernel methods of that kind. The NequIP paper says it significantly outperforms kernel-based approaches such as GAP, FCHL19/GPR and sGDML (a symmetrized version of GDML) on MD-17 with N=1,000 configurations [W4225405705#010]. It calls the consistent improvement over sGDML and FCHL19/GPR "particularly surprising", because kernel methods typically beat deep neural networks on small training sets [W4225405705#011]. In the introduction, NequIP is described as "competitive with" kernel approaches [W4225405705#002]. Kernel approaches also carry a significant extra cost in training and prediction scaling [W4225405705#002].

A table in the NewtonNet paper agrees on forces for some molecules. NequIP's force MAE is lower than sGDML's for aspirin (0.348 vs 0.68), ethanol (0.208 vs 0.33), malonaldehyde (0.337 vs 0.41), naphthalene (0.096 vs 0.11), salicylic acid (0.238 vs 0.28) and toluene (0.101 vs 0.14) [W3189651386#010]. The same table has no NequIP entries for energies.
- reference: SchNet compared against GDML (gradient-domain machine learning), which was more data-efficient on the small training set for most molecules. The NequIP paper reports outperforming kernel-based approaches, including sGDML (the symmetrized successor of GDML), as well as GAP and FCHL19.
- correctness: correct (The answer identifies GDML as the kernel method SchNet compared against and states that NequIP outperforms kernel methods including sGDML, GAP and FCHL19, matching the reference; the extra detail doesn't contradict it.)
- support: partial (The NequIP claims and the table figures match the passages, but two descriptive details appear in none of them: that GDML is a kernel method, and that sGDML is a 'symmetrized version of GDML'.)
- steps: search "SchNet MD17 comparison kernel method gradient domain machine learning sGDML" (5 passages, 5 new); search "NequIP MD17 compared to kernel methods sGDML FCHL" (5 passages, 3 new); search "NequIP equivariant interatomic potentials MD17 outperforms GDML sGDML kernel" (5 passages, 4 new); answer

**q018** (comparison): Both SchNet and the Behler-Parrinello potential build the prediction from atomic contributions. For which properties does the SchNet paper say this is a poor fit?
- answer: The SchNet paper says the decomposition into atomic contributions is a poor fit for the polarizability α and the electronic spatial extent ⟨R²⟩. SchNet's predictions for these two properties "fall noticeably short in terms of accuracy," which the authors attribute most likely to this decomposition [W2778051509#013].

The paper contrasts this with the enn-s2s model of Gilmer et al. That model uses a set2set variant with a global representation, so it does not have this issue. SchNet still matches or beats enn-s2s on 8 of 12 properties, which the paper describes as ones where an atomic decomposition is a good choice [W2778051509#013].

The passages I found don't discuss the Behler-Parrinello potential in this context, so I can't say what the paper says about it on this point.
- reference: Behler-Parrinello writes the total energy as a sum of atomic energies. SchNet does the same for its targets and does noticeably worse on the polarizability and the electronic spatial extent <R^2> of QM9 molecules, which the authors attribute to that atom-wise decomposition not suiting these properties.
- correctness: correct (The answer identifies polarizability α and electronic spatial extent ⟨R²⟩ as the poorly-fitting properties, attributed to the atom-wise decomposition, matching the reference; the extra details and the note about Behler-Parrinello do not contradict it.)
- support: supported (Every claim (poor accuracy on α and ⟨R²⟩ due to atomic decomposition, enn-s2s's global set2set representation, and SchNet matching or beating enn-s2s on 8 of 12 properties) is stated in the cited passage.)

**q019** (lookup): What problem with CHARMM36 was CHARMM36m designed to fix?
- answer: The passages I could read only partly answer this. CHARMM36m is a refinement of CHARMM36, a widely used all-atom additive protein force field. Its stated aim is better accuracy in generating polypeptide backbone conformational ensembles for intrinsically disordered peptides and proteins [W2555870966#000]. So the problem it addresses is that CHARMM36 was less accurate for disordered proteins and peptides. The title also says CHARMM36m is meant to work for folded proteins too [W2555870966#000]. Only the abstract of the CHARMM36m paper is available. It doesn't say what went wrong with CHARMM36, for example whether disordered chains came out too compact or too helical.
- reference: CHARMM36 overstabilized compact and left-handed helical structures in intrinsically disordered proteins and peptides. CHARMM36m was refined to describe disordered proteins better while keeping the accuracy of CHARMM36 for folded proteins.
- correctness: partial (It correctly says CHARMM36 was less accurate for intrinsically disordered proteins and that CHARMM36m also works for folded proteins, but it omits the specific problem of overstabilized compact and left-handed helical structures and says this detail is unavailable.)
- support: supported (Every claim is stated in or follows from the cited abstract and title, and the caveats about missing detail are accurate.)
- steps: search "CHARMM36m improved force field intrinsically disordered proteins CHARMM36 overly compact" (5 passages, 5 new); search "CHARMM36 overly compact IDP, salt bridge, helical, backbone CMAP refinement, Lennard-Jones, folded proteins" (1 passage, 0 new); search "CHARMM36 simulations of disordered peptides too compact, secondary structure, helical propensity" (5 passages, 5 new); open_paper "W2555870966" (1 section); search "CHARMM36m developed to correct CHARMM36 tendency IDPs collapsed compact helical" (5 passages, 4 new); answer

**q020** (lookup): Which parts of the force field were changed to go from CHARMM36 to CHARMM36m?
- answer: The collection has only the abstract of the CHARMM36m paper [W2555870966#000]. It says CHARMM36m is a refinement of CHARMM36 that gives better backbone conformational ensembles for intrinsically disordered peptides and proteins. It does not say which force-field terms were changed, for example CMAP, dihedral or Lennard-Jones parameters. The other passages I found don't answer this either. [W2109154308#000] describes the earlier C36 changes relative to CHARMM22/CMAP. [W4289550218#000] covers CHARMM36m-SBFIX, a later NBFIX add-on.
- reference: Mainly the backbone CMAP correction was refit, to reduce the left-handed helix bias, and the paper recommends a modified TIP3P water with a stronger Lennard-Jones interaction on the water hydrogens, so that disordered proteins are less overly compact.
- correctness: incorrect (declined to answer although the corpus has the answer)
- steps: search "CHARMM36m modifications relative to CHARMM36 backbone CMAP torsion Lennard-Jones" (5 passages, 5 new); search "CHARMM36m refinement: CMAP backbone potentials, side-chain dihedral, Lennard-Jones well depth of arginine, lysine, aspartate, glutamate, TIP3P" (1 passage, 0 new); open_paper "W2555870966" (1 section); search "CHARMM36m differs from CHARMM36 by modified CMAP, arginine lysine side chain LJ, NBFIX" (5 passages, 3 new); search "CHARMM36m backbone CMAP refined and LJ parameters for NH3+ of lysine and guanidinium, compared to C36" (5 passages, 1 new); search "C36m improved sampling of disordered proteins by reparametrizing backbone dihedral CMAP and tuned Lennard-Jones between hydrogens and water oxygen" (5 passages, 4 new); give_up

**q021** (unanswerable): What experimental success rate does RFdiffusion reach when designing protein binders?
- answer: The collection doesn't contain a passage giving RFdiffusion's experimental binder success rate. The RFdiffusion paper itself (Watson et al., 2023) appears only as a reference entry [W4391542588#028]. Two other papers mention it only qualitatively: one says it generated novel protein-binder backbones "with successful experimental validation" [W4393118201#005], and no percentage appears there. I found no figure for the success rate.
- reference: Not answerable from this corpus, which covers interatomic potentials and force fields, not protein design.
- steps: search "RFdiffusion binder design experimental success rate" (5 passages, 5 new); search "RFdiffusion designed binders experimentally validated hit rate tenfold improvement" (5 passages, 5 new); search "Watson RFdiffusion de novo design of protein structure and function binders success" (5 passages, 5 new); search "diffusion model de novo protein binder design experimental success rate percent of designs bind target" (5 passages, 2 new); give_up

**q022** (unanswerable): What dropout rate was used when training SchNet?
- answer: No passage states a dropout rate for SchNet. Searches for "dropout" within the SchNet papers [W2726670313] and [W2778051509] returned nothing. Other SchNet-related passages cover training settings that don't include dropout: Adam with learning rate 1e-4 and batch size 10 [W3159653252#028], and the MD17 training setup [W2778051509#017]. Dropout rates that appear belong to other models, such as the GELU experiments [W2899663614#006].
- reference: Not in the corpus. The SchNet paper describes its optimizer, batch size and learning-rate decay, but no dropout.
- steps: search "SchNet dropout rate training" (5 passages, 5 new); search "SchNet continuous-filter convolutional dropout" (5 passages, 5 new); search "dropout" (no results); search "SchNet trained without dropout hyperparameters baseline" (5 passages, 4 new); search "SchNet model trained with dropout of" (10 passages, 9 new); search "dropout" (no results); search "dropout" (no results); give_up

**q023** (lookup): What does DiffTRe do differently from backpropagating through an MD simulation, and what does that buy it?
- answer: DiffTRe does not backpropagate through the MD simulation. It uses reweighting instead, and that buys it better numerical stability and a large speed-up in the gradient computation.

**What it does differently.** DiffTRe generates a reference trajectory with reference potential parameters θ̂ and keeps decorrelated, subsampled states. For those states it computes weights wᵢ under the current parameters θ, which give reweighted observables ⟨Ok(Uθ)⟩ [W3168247670#006]. This ties the observables directly to θ. The loss gradient is then obtained by differentiating through the reweighting scheme, which replaces the backward pass through the simulation [W3168247670#006]. The method is based on thermodynamic perturbation theory and applies to time-independent observables [W3168247670#001].

The effective sample size Neff has to be managed. When θ drifts far from θ̂, a few states dominate the average and the statistical error grows. Once Neff drops below a threshold, a new reference trajectory is generated [W3168247670#006].

**What it buys.**
- It avoids the exploding gradients that come with backpropagating through MD [W3168247670#001].
- It gives about 2 orders of magnitude speed-up in gradient computation for top-down learning [W3168247670#001].
- States from earlier trajectories can often be re-used, which speeds up the forward pass [W3168247670#006].
- It generalizes bottom-up structural coarse-graining methods such as iterative Boltzmann inversion to arbitrary potentials [W3168247670#001].
- reference: It doesn't differentiate through the simulation at all. It combines automatic differentiation with MD reweighting, so gradients flow through the reweighted ensemble averages instead of the trajectory. For time-independent observables this avoids exploding gradients and makes gradient computation about two orders of magnitude faster, with memory needs similar to the adjoint method.
- correctness: correct (The answer captures the key points: no differentiation through the simulation, reweighting with automatic differentiation, avoidance of exploding gradients, and about two orders of magnitude faster gradients; the omitted memory comparison to the adjoint method is a minor gap and the extra details are accurate.)
- support: supported (Every claim, including reweighting replacing backprop, Neff management, avoiding exploding gradients, ~2 orders of magnitude speed-up, state re-use, and generalizing iterative Boltzmann inversion, is stated in the cited passages.)

**q024** (lookup): How are the reweighting weights computed in DiffTRe, and why does the kinetic energy drop out?
- answer: In DiffTRe, each subsampled state S_i from a reference trajectory (made with reference potential θ̂) gets a weight equal to its probability ratio under the new and reference potentials, normalized over the trajectory. That is w_i = [p_θ(S_i)/p_θ̂(S_i)] / Σ_j [p_θ(S_j)/p_θ̂(S_j)] [W3168247670#005].

In a canonical ensemble, p(S_i) ∼ exp(−βH(S_i)). The Hamiltonian H is the sum of potential and kinetic energy, and β = 1/(k_B T) [W3168247670#005]. The paper says the kinetic energy cancels. The reason is that the ratio compares the same state under two potentials, so the kinetic term is identical in numerator and denominator. The weights then reduce to:

w_i = exp(−β(U_θ(S_i) − U_θ̂(S_i))) / Σ_j exp(−β(U_θ(S_j) − U_θ̂(S_j)))

They depend only on potential-energy differences [W3168247670#005]. For θ = θ̂, every weight is 1/N [W3168247670#005].

The passage states that the kinetic energy cancels but does not spell out the same-state argument. That explanation is my inference from the ratio form.
- reference: In the canonical ensemble, each saved state gets w_i = exp(-beta (U_theta(S_i) - U_ref(S_i))), normalized over all states. Only the potential energy appears because the kinetic energy is the same under the old and new potential and cancels in the Boltzmann ratio. With theta equal to the reference, all weights are 1/N.
- correctness: correct (The answer gives the same normalized Boltzmann-ratio weights depending only on potential energy differences, explains that kinetic energy is identical under both potentials and cancels, and notes weights are 1/N when theta equals the reference.)
- support: supported (Every claim matches the passage (Eq. 3 weights, Boltzmann form, kinetic energy cancels, Eq. 4, w_i = 1/N for θ = θ̂), and the answer itself flags the same-state explanation as its own inference.)

**q025** (lookup): When does DiffTRe stop reusing the old trajectory and simulate a new one?
- answer: DiffTRe stops reusing the old trajectory when the effective sample size Neff falls below a chosen threshold, written N̄eff in the paper [W3168247670#006]. It keeps updating the potential parameters θ with the reweighted states until then. Once Neff < N̄eff, it generates a new reference trajectory. That trajectory starts from the last sampled state S_N of the previous one [W3168247670#006].

Neff is computed as Neff ≈ exp(−Σ wi ln wi), where the wi are the reweighting weights. It drops when θ moves far from the reference parameters θ̂, because then a few states dominate the average [W3168247670#006].
- reference: When the effective sample size of the reweighted states, N_eff ~ exp(-sum w_i ln w_i), falls below a chosen threshold, meaning a few states dominate the average and its statistical error is too large. A new reference trajectory is then run with the current parameters, starting from the last state of the old one.
- correctness: correct (The answer matches the reference: it gives the same effective sample size formula and threshold criterion, explains that a few states dominate, and says the new trajectory starts from the last state of the old one.)
- support: supported (The passage states each claim: the update loop runs until Neff < N̄eff, a new trajectory then starts from the last sampled state S_N, Neff ≈ exp(−Σ wi ln wi), and large differences between θ and θ̂ let few states dominate.)

**q026** (lookup): Which experimental data was the DiffTRe diamond potential trained on?
- answer: The DiffTRe diamond potential was trained on the experimental elastic stiffness tensor of diamond. The model is a DimeNet++ potential [W3168247670#013]. The tensor has three distinct moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. The loss also assumes a stress-free state, with σ = 0 at zero strain [W3168247670#013]. The simulations matched the experimental density of 3512 kg/m3 and the experimental temperature of 298.15 K [W3168247670#013].
- reference: The experimental elastic stiffness tensor of diamond, which by cubic symmetry has three moduli: C11 = 1079 GPa, C12 = 124 GPa and C44 = 578 GPa. Training also targeted a stress-free state at zero strain.
- correctness: correct (The answer states the experimental elastic stiffness tensor with the correct C11, C12, C44 values and the stress-free state at zero strain, matching the reference; the extra details (DimeNet++, density, temperature) do not contradict it.)
- support: supported (All claims (DimeNet++ model, experimental stiffness tensor, three moduli values, stress-free assumption, density 3512 kg/m3, temperature 298.15 K) are stated in the cited passage.)

**q027** (lookup): Which held-out property did DiffTRe's coarse-grained water model get wrong, and why?
- answer: The held-out property it got wrong was the self-diffusion coefficient D. The learned CG water model predicted D = 10.91 μm²/ms, against an experimental value of 2.2 μm²/ms [W3168247670#017]. The other held-out property, the tetrahedral order parameter q, came out at about 0.569 against 0.576 experimentally, so it matched [W3168247670#017].

The paper explains the error in terms of smoother potential energy surfaces. Coarse-grained models run dynamical processes faster than atomistic models because their surfaces are smoother, and diffusion coefficients fall as the number of interaction sites rises [W3168247670#017]. The model has a single site per water molecule. The iterative Boltzmann inversion single-site model made the same kind of error, with D = 14.15 μm²/ms [W3168247670#017]. DiffTRe also could not use dynamical properties as targets, because its reweighting scheme ignores the order of states in the trajectory [W3168247670#019].
- reference: The self-diffusion coefficient: about 10.9 versus 2.2 μm²/ms in experiment, so diffusion is too fast. Coarse- grained models have smoother energy surfaces, which speeds up their dynamics compared with atomistic models. (The tetrahedral order parameter, by contrast, matched closely.)
- correctness: correct (Identifies self-diffusion coefficient as wrong (10.91 vs 2.2 μm²/ms), attributes it to smoother potential energy surfaces in CG models speeding dynamics, and notes tetrahedral order parameter matched; extra details are consistent.)
- support: supported (All claims match the cited passages; the single-site description of the model is only implied but is consistent with the text's comparison to a single-site IBI model.)

**q028** (lookup): Could you use DiffTRe to fit a potential to a measured diffusion coefficient?
- answer: Not with DiffTRe as originally proposed. The original DiffTRe paper says its reweighting scheme makes it invariant to the order of states in a trajectory. It states that "dynamical properties cannot be employed as target observables" [W3168247670#019]. The self-diffusion coefficient was only a held-out check in that paper. The learned coarse-grained water model gave D = 10.91 μm2/ms, against an experimental 2.2 μm2/ms [W3168247670#017].

A later method extends the idea. It combines reweighting with trajectory differentiation using the adjoint method, and it can fit diffusion coefficients directly [W4406553977#003]. As a test, it recovered Lennard-Jones parameters from a target diffusion coefficient [W4406553977#010]. It also fit water potentials to density and IR spectrum, and it used the diffusion coefficient error to select the final model [W4406553977#018]. Its caveats are that gradients explode for long trajectories, so the velocity autocorrelation integral was truncated at about 2 ps [W4406553977#011]. It also used no moving average in the diffusion example, because storing the full velocity trajectory in GPU memory is difficult [W4406553977#023].

The Lennard-Jones test used a diffusion coefficient computed from known parameters as the target, not a measured one [W4406553977#010]. The water case fit density and IR spectrum, with diffusion used only to select the final model [W4406553977#018].
- reference: No. Reweighting treats the trajectory as a set of states and ignores their order in time, so dynamical properties such as diffusion coefficients can't be targets; only time-independent observables can.
- correctness: correct (The answer says DiffTRe cannot use dynamical properties like diffusion coefficients as targets because reweighting is invariant to state order, matching the reference, and the extra details about later methods do not contradict it.)
- support: partial (The claim that the method 'recovered' the Lennard-Jones parameters is not shown in the cited passage W4406553977#010, which only states the goal of testing whether the optimizer could find them; the other claims are supported.)
- steps: search "DiffTRe diffusion coefficient" (5 passages, 5 new); search "Differentiable Trajectory Reweighting limitations dynamical properties" (5 passages, 5 new); answer

**q029** (comparison): SchNet's C20 force field was trained on DFT data. What do the DiffTRe authors see as the main limitation of that kind of training, and what do they train on instead?
- answer: DiffTRe's authors say the main obstacle to training on quantum-mechanical (DFT-type) data is that highly precise, sufficiently broad data sets are hard to get. For larger systems such as macromolecules, quantum mechanics computations will stay intractable for the foreseeable future, so such data sets can't be generated at all [W3168247670#003]. I didn't find a passage where DiffTRe discusses SchNet's C20 work specifically. This answer rests on their general critique of bottom-up training. SchNet's C20 model was trained on DFT (PBE+vdW-TS) reference data [W2778051509#019].

DiffTRe instead trains top-down, directly on experimental data. It does this by reweighting MD trajectories, which avoids backpropagating through the simulation [W3168247670#001]. Their test cases are:
- a DimeNet++ model of diamond, trained on its experimental stiffness tensor;
- a coarse-grained DimeNet++ water model, trained on pressure plus radial and angular distribution functions [W3168247670#003].
- reference: SchNet is trained bottom-up on DFT reference calculations (PBE+vdW-TS for C20). DiffTRe's authors argue that bottom-up training is limited by the availability of precise and broad enough quantum data sets, and that its accuracy is capped by the reference method. DiffTRe trains top-down instead, so that simulations reproduce experimental observables.
- correctness: partial (It correctly gives the data-availability limitation and top-down training on experimental data, but omits the reference's point that accuracy is capped by the reference method.)
- support: supported (All substantive claims (data-set obstacle, macromolecule intractability, SchNet C20 DFT PBE+vdW-TS training, DiffTRe reweighting, diamond and CG water test cases) are stated in the cited passages.)
- steps: search "DiffTRe differentiable trajectory reweighting limitation of training on ab initio data, experimental data" (5 passages, 5 new); search "SchNet C20 fullerene force field DFT training data" (5 passages, 5 new); answer

**q030** (multihop): DiffTRe's diamond model starts from an empirical potential originally built for another element. Which potential was it, and which neural network potential paper used that same element as its test system?
- answer: DiffTRe's diamond model uses the original Stillinger-Weber potential, which was parametrized for silicon, as its prior. The authors rescaled its length and energy scales to σ_SW = 0.14 nm and ε_SW = 200 kJ/mol to reflect the smaller carbon atoms [W3168247670#013].

The neural network potential paper that used silicon as its test system is "Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces" (Behler and Parrinello, 2007). It built an NN potential for bulk silicon, tested it on energy-volume curves for silicon crystal structures, and checked it against the radial distribution function of a silicon melt at 3000 K [W2025444507#007][W2025444507#008].

The JAX MD paper also trains neural network potentials on silicon DFT data [W2991697224#016]. I took it to be a molecular dynamics library paper rather than a neural network potential paper, so I did not choose it.
- reference: The Stillinger-Weber potential parametrized for silicon, rescaled for carbon. Silicon is also the test system of the original Behler-Parrinello neural network potential, which was compared against empirical potentials and DFT for bulk silicon.
- correctness: correct (Identifies the Stillinger-Weber potential parametrized for silicon, rescaled for carbon, and names Behler-Parrinello (2007) as the NN potential paper using silicon as its test system, matching the reference.)
- support: partial (The DiffTRe/Stillinger-Weber rescaling and the silicon NN details (bulk silicon, energy-volume curves, 3000 K melt RDF, JAX MD silicon DFT data) are all in the passages, but the attribution of the 2007 paper to 'Behler and Parrinello' is not stated in any cited passage.)
- steps: search "DiffTRe diamond model empirical potential" (5 passages, 5 new); search "neural network potential test system silicon" (5 passages, 5 new); answer

**q031** (multihop): Which graph neural network does DiffTRe use as its learnable potential, and how does NequIP compare with that family of models on MD-17?
- answer: DiffTRe uses DimeNet++ as its learnable potential. The paper trains it for diamond and for coarse-grained water [W3168247670#004]. DiffTRe describes this potential only as "a graph neural network" (e.g. a GNN) [W3168247670#006]. DimeNet++ is the successor to DimeNet, which the NequIP paper counts among the invariant GNN interatomic potentials. That link is my inference, because no passage ties DimeNet++ to DimeNet directly.

On MD-17, NequIP is more accurate than the invariant GNN interatomic potentials. The NequIP paper says it "significantly outperforms invariant GNN-IPs (such as SchNet and DimeNet)" [W4225405705#010]. It also outperforms kernel methods and shallow neural networks. On revised MD-17, the NequIP authors report that it outperforms all the other methods they compared [W4225405705#011]. They attribute the gain to equivariance: going from l = 0 to l = 1 gives a large improvement [W4225405705#011].

A table in the PaiNN paper agrees for aspirin forces. It lists NequIP at 0.348, DimeNet at 0.499 and SchNet at 1.35 kcal/mol/Å [W3126679164#021]. For ethanol forces, NequIP is at 0.208 against DimeNet's 0.230 in that table [W3126679164#021].
- reference: DimeNet++ (an improved DimeNet), used for both diamond and coarse-grained water. NequIP reports significantly outperforming invariant graph network potentials, naming SchNet and DimeNet, on MD-17.
- correctness: correct (The answer identifies DimeNet++ for diamond and coarse-grained water and states NequIP significantly outperforms invariant GNN potentials like SchNet and DimeNet on MD-17, matching the reference; extra details are consistent.)
- support: supported (Every claim matches the cited passages, including the table values for aspirin and ethanol forces; the DimeNet++–DimeNet successor link is not in the passages, but the answer itself labels it as an inference.)
- steps: search "DiffTRe differentiable trajectory reweighting graph neural network potential" (5 passages, 5 new); search "NequIP MD-17 comparison with DimeNet SchNet message passing force errors" (5 passages, 5 new); answer

**q032** (lookup): In DiffTRe, what is the prior potential for, if not a Bayesian prior?
- answer: In DiffTRe, the prior potential U_prior is a constant potential. It approximates properties of the system known in advance, such as the Pauli exclusion principle [W3168247670#008]. It has three roles:

- **Trajectory generation.** It controls how trajectories are generated at the start of the optimization [W3168247670#008]. A well-chosen prior should give trajectories as close as possible to ones sampled from the true potential [W3168247670#010].
- **Reformulating the learning problem.** The network no longer learns U_model directly. It learns the difference between U_prior and the optimal potential given the data [W3168247670#008].
- **Initialization.** A well-chosen prior is a physics-informed initialization that speeds up convergence [W3168247670#008].

The paper says U_prior is not a Bayesian prior, meaning it does not impose a pervasive bias on the learnable parameters in the small-data regime. If U_prior contradicts the data, U_model corrects for it during optimization [W3168247670#008].
- reference: A simple physics-based potential (e.g. a repulsive Lennard-Jones term, or Stillinger-Weber) added to the neural network. Early in training it controls which configurations the simulations visit, and therefore where the gradient carries information. It also gives a physics-informed starting point, so the network learns a correction to the prior. If the data contradicts the prior, the network overrides it.
- correctness: correct (The answer captures the key points: a physics-based prior (e.g., Pauli exclusion/repulsion) that controls early trajectory generation, makes the network learn a correction, acts as a physics-informed initialization, and is overridden if it contradicts the data.)
- support: supported (Every claim, including the trajectory-generation, reformulation, initialization, and non-Bayesian points, appears in passages #008 and #010.)

**q033** (unanswerable): How many GPU hours did it take in total to train the DiffTRe diamond potential?
- answer: The DiffTRe paper [W3168247670] describes the diamond DimeNet++ training setup: 1000 carbon atoms, 10 ps equilibration plus 60 ps production per trajectory [W3168247670#013], and about 700 update steps shown in Fig. 3. It mentions wall-clock time per update in Supplementary Fig. 5 [W3168247670#014]. None of the passages I retrieved give a total GPU-hour figure for training the diamond potential. The only GPU-hour numbers I found were for other papers' models.
- reference: Not in the corpus. The main text gives only per-update wall-clock times for the toy example and refers to the supplementary information for the diamond training curve; no total training cost is stated.
- steps: search "DiffTRe diamond potential GPU hours training" (5 passages, 5 new); search "diamond training took hours GPU update steps wall time" (5 passages, 4 new); search "total training time GPU hours diamond water DimeNet++ NVIDIA" (5 passages, 2 new); search "computational cost trained on single GPU hours diamond potential" (8 passages, 2 new); search "training took hours on GPU" (9 passages, 4 new); search "Nvidia GPU computation time hours optimization diamond DiffTRe supplementary" (5 passages, 2 new); give_up

