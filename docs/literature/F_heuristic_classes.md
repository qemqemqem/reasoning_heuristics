> Research-agent report written 2026-11-13 for the literature review in [../LITERATURE.md](../LITERATURE.md). Every source was found by web search or fetch during the review, and the report tags how each was checked. Treat details as leads to confirm before citing.

# F. Classes of heuristics for NP-hard problems: a theory-built zoo

*Literature review slice F for "Heuristics Under Hardness" (`~/Dev/reasoning_heuristics`). Written 2026-11-13.*

**Andrew's question:** "Much more mathematically, what are the major classes of heuristics for NP-hard problems?"

**How the sources were checked.** Each source carries a tag:

- **[R]**: read closely this session (full text or long excerpts).
- **[A]**: abstract or publisher summary read this session.
- **[S]**: claim taken from a secondary source found this session (a citing paper, a compendium entry or a search summary), not from the original.
- **[M]**: bibliographic record only (Crossref or arXiv metadata). Only the title-level claim is used.

The session's shared web-search budget ran out partway through. Later checks used WebFetch on arXiv and publisher pages, plus bibliographic lookups (Crossref, arXiv API) made earlier. Anything recalled but not found is listed under *Unverified*.

---

## Summary

- **There is a mathematical answer to "what is a heuristic class".** Theory has formal *models of algorithmic paradigms*, and each comes with provable limits:
  - **priority algorithms** for greedy methods (Borodin, Nielsen & Rackoff 2003);
  - **priority branching trees (pBT)** for backtracking and simple dynamic programming (Alekhnovich et al. 2011);
  - **PLS** for local search (Johnson, Papadimitriou & Yannakakis 1988);
  - the **LOCAL model**, i.e. constant-round distributed algorithms, which equals GNNs (Sato, Yamada & Kashima 2019);
  - **low-degree polynomials**, covering message passing and local algorithms on random instances (Bresler & Huang 2021; Gamarnik, Jagannath & Wein 2020);
  - **linear sketches / streaming** for one-pass methods (Chou et al. 2024).

  We should build the zoo as *parameterised members of these models*, not as a list.
- **Pearl (1983/84) is the generative theory for heuristic content.** He names three kinds of simplified model: **relaxed** (delete constraints), **over-constrained** (add constraints or fix part of the solution) and **probabilistic** ([R], Pearl 1983). Our reading is that this split predicts error signatures:
  - relaxations are optimistic or sound, which gives *omission* errors in entailment;
  - restrictions are pessimistic or unsound, which gives *commission* errors in entailment and false "no solution" answers in search.

  ETR, MM, `FIRST` and `MATCH` are all restrictions of the model set. `UP-k` is a relaxation of the proof system.
- **Pearl's decomposability criterion lines up with our C/S split** (our interpretation). Relaxed models that are *fully decomposable*, i.e. sums of independent sub-goals such as misplaced tiles or Manhattan distance, are constant-depth. *Semi-decomposable* models solved by greedy "cheapest-subgoal-first", such as MST, are sequential.
- **P-completeness results give citable S labels for existing zoo entries.** The Greenlaw–Hoover–Ruzzo compendium [R] lists all of these as P-complete:
  - lexicographically-first maximal independent set (Cook 1985);
  - lexicographically-first Δ+1 greedy colouring, i.e. `FIRST-FIT` in input order;
  - the **nearest-neighbour TSP tour**, i.e. `NN-from-0`;
  - **first-fit-decreasing bin packing**;
  - list scheduling;
  - **unit resolution** and **Horn unit resolution**, i.e. unbounded `UP`;
  - relaxed consistent labelling (arc consistency; Kasif);
  - linear programming.

  If TC⁰ ≠ P, no fixed-depth transformer reproduces these outputs exactly at scale without chain of thought.
- **Not every greedy is S.** Under a *random* vertex order, sequential greedy MIS has O(log² n) dependence depth on any graph, and the same holds for greedy matching (Blelloch, Fineman & Shun 2012) [A]. Constant-round local and message-passing algorithms are exactly what L-layer GNNs compute (Sato et al. 2019) [R]. We propose a third class, **L** (polylog depth), between C and S.
- **Random-instance theory gives each class a threshold signature.** Each class has a provable or analysed algorithmic threshold:
  - **Unit-clause heuristic** on random 3-SAT: about 8/3 [S].
  - **Optimal "myopic" unit-clause-style algorithms:** 3.26 [A].
  - **Greedy colouring:** about 2χ colours [A].
  - **BP-guided decimation:** fails at order 2^k/k [S].
  - **Low-degree polynomials:** fail above about 4.911·2^k log k / k, while solutions exist up to about 2^k log 2 [A].
  - **Local algorithms:** at most 1/2 + 1/(2√2) of the maximum independent set [A].

  The knee in a model's error-vs-density curve is therefore an identification signature.
- **Theory says when simple heuristics are optimal.** Greedy is exact on matroids (Edmonds 1971) [M] and has (1 − 1/e) guarantees for submodular objectives (Nemhauser, Wolsey & Fisher 1978) [M]. A uniformly random assignment is already optimal for MAX-E3-SAT unless P = NP (Håstad 2001) [S]. Under the UGC, one SDP-plus-rounding scheme is optimal for every CSP (Raghavendra 2008) [S]. In human-decision research, lexicographic one-reason rules decide *identically* to the linear rule under noncompensatory weights (Martignon & Hoffrage 2002, via Şimşek 2013) [R].
- **The zoo is missing three whole classes:**
  - constant-round **message passing** (`BP-t`, `WP-t`; note that `UP-k` is its hard-decision special case);
  - **randomised guessing and sampling** (`RANDOM`, `SAMPLE-m`);
  - **relaxation-and-solve** members with diagnosable violation profiles (`2SAT-CORE`, `PREMISE-SUBSET`, MST-based TSP).

  Several existing entries are one parametric family, e.g. `PRIORITY(order, score, rule)` and `RESTRICT(selector)`.
- **Recent LLM-designed heuristics mostly fill templates.** FunSearch, EoH and ReEvo evolve *scoring functions inside fixed templates* (greedy, guided local search, ACO). One case study found the LLM "concentrated its efforts almost exclusively on refining the scoring function" of a greedy solver (Quan et al. 2025) [A]. LLM-evolved bin-packing heuristics "do not generalise well" across benchmarks (Sim, Renau & Hart 2025) [A]. This supports modelling LLM heuristics as *priority-function choices inside a paradigm template*.

---

## Proposed taxonomy

### Organising principle (our proposal)

Classify a heuristic by **the object it manipulates** and **how it commits**. Several properties are cross-cutting axes, not classes:

- approximation guarantee;
- randomisation;
- soundness;
- feasibility;
- depth class.

Williamson & Shmoys organise approximation algorithms *by technique* (greedy and local search, DP, LP/SDP, randomisation) [A], and techniques recur across guarantees. That supports treating the guarantee as an axis rather than a class.

A formal definition to anchor everything (Bogdanov & Trevisan 2006) [R]:

- A **heuristic algorithm** for a distributional problem (L, D) with error δ satisfies Pr_{x∼D_n}[A(x) ≠ L(x)] ≤ δ(n).
- An **errorless heuristic** instead outputs either L(x) or ⊥, with Pr[⊥] ≤ δ(n).
- **HeurP** consists of the problems with a heuristic scheme; **AvgP** of those with an errorless scheme.

Our zoo is a finite sample of algorithms A drawn from resource-bounded classes R. The theory below gives lower bounds on δ per (R, D).

### The tree

```
Heuristics for NP-hard problems
├── A  Answer without a witness ("cue / substitution")
│    A1 constant / base-rate answers           ALWAYS-SAT, NONE, ECHO
│    A2 feature-threshold rules                 DENSITY, LENGTH-PRIOR, ATMOSPHERE, FREQ, PRIMACY, RECENCY
│    A3 problem substitution                    TEXTBOOK-TRANSFER
├── B  Solve a simplified model exactly (Pearl)
│    B1 relaxation by constraint deletion       UP-k (proof-system relaxation), PREMISE-SUBSET*, 2SAT-CORE*, MST-TSP*, HALLUC-drop
│    B2 abstraction / aggregation               pattern databases, merge-and-shrink (planning)
│    B3 convex relaxation + rounding            LP/SDP/Lagrangian + threshold or randomised rounding
│    B4 restriction / over-constraint           FIRST, MATCH, MM, ETR, CLOSED-WORLD*, BICONDITIONAL*, HALLUC-add
│    B5 probabilistic / mean-field model        expected-cost estimates → leads into E
├── C  Constructive, irrevocable (priority algorithms)
│    C0 one-shot independent scoring            POLARITY, MOMS, PURE-LITERAL (1 round)
│    C1 fixed-order                             GREEDY, FIRST-FIT, NN-from-0, RATIO, VALUE, LARGEST-FIT, LARGEST-FIRST, INPUT-ORDER
│    C2 adaptive-order                          DSATUR, UC/GUC/SC*, UP+GUESS, GREEDY-EDGE, FARTHEST-INSERTION
│    C3 random-order                            RANDOM-ORDER-FIRST-FIT, (PPZ-style random order + forcing*)
│    C4 online / one-pass with bounded state    ETR update over premises, ONLINE-STATE*
├── D  Systematic search with pruning (pBT, DPLL/CDCL, B&B, A*)
│    D1 complete                                exact solver (ground truth)
│    D2 budget-truncated                        DPLL-b, width-w pBT / beam*, A* with node budget
│    D3 parameterised / backdoor / kernel       branch only on a small backdoor; reduction rules
├── E  Iterated local message passing (LOCAL / GNN / low-degree)
│    E1 t rounds + rounding                     BP-t*, WP-t*, SP-t*, UP-k (hard-decision MP), LOCAL-t colouring*
│    E2 decimation (re-run after fixing)        BP-DEC*, SP-DEC*
├── F  Local search over complete assignments (PLS)
│    F1 descent                                 2OPT-k, MIN-CONFLICTS*
│    F2 noisy / annealed                        WALK-k, SA
│    F3 memory                                  tabu
│    F4 population                              GA, ACO
├── G  Decomposition / dynamic programming      treewidth DP, divide & conquer, pseudo-poly / scaled DP (knapsack FPTAS)
├── H  Randomised guessing & sampling           RANDOM*, SAMPLE-m* (sample models, check conclusion), random restarts
└── I  Meta-level                               algorithm selection / portfolios, hyper-heuristics, learned (NCO, learn-to-branch, GNN), LLM-designed (FunSearch/EoH/ReEvo)

Cross-cutting axes: guarantee (exact / ratio / none) · soundness · feasibility · randomness · depth class (C / L / S)
Not heuristics (nuisance models): NOISY-EXACT, random perception noise
(* = proposed new zoo member)
```

### Class table

"Depth class" uses our proposed three-way split:

- **C:** O(1) sequential rounds, i.e. constant-depth RASP-L.
- **L:** polylog rounds.
- **S:** inherently sequential (P-complete output, or exponential).

The table gives the evidence for each label. Error signatures are our interpretation unless a citation is given.

| Class | Defining mathematical idea | Representative algorithms | Typical error signature | Depth class (evidence) | Key citations |
|---|---|---|---|---|---|
| **A. Cue / substitution** | Answer = f(φ(x)) for a low-dimensional, easily computed feature map φ. Kahneman–Frederick: a hard *target attribute* is replaced by an accessible *heuristic attribute* [S]. | Base rate; threshold on density or length; take-the-best on cues | Wrong on the minority class, whatever the deeper structure. Invariant to manipulations that keep φ; maximally sensitive to manipulations of φ. One-sided when the rule is constant. | **C**. Counts and thresholds are majority-type: TC⁰, not AC⁰. This matters under O2's constant-precision AC⁰ case (see Unverified). | Kahneman & Frederick 2002; Gigerenzer & Goldstein 1996; Martignon & Hoffrage 2002; Şimşek 2013 |
| **B1. Relaxation (constraint deletion)** | Solve the problem with a constraint subset deleted. The solution value is optimistic, hence admissible, and "guaranteed to be consistent" (Pearl 1983) [R]. In inference: a weaker but sound proof system. | MST and assignment bounds for TSP; misplaced tiles and Manhattan distance; delete-relaxation h⁺ in planning; unit propagation; 2-SAT core | **Sound but incomplete** (omission) in entailment. In search, it returns objects that violate *exactly the deleted constraint type*, so the violation profile identifies the relaxation. In SAT decisions it is biased toward "SAT". | Depends on how decomposable the relaxed model is (our reading of Pearl). Fully decomposable gives C (a sum of independent terms). Greedy-solvable gives S. Unbounded unit or Horn resolution is **P-complete → S** [R, compendium A.6.1–A.6.2]; k rounds is C. | Pearl 1983 [R]; Hart, Nilsson & Raphael 1968; Bonet & Geffner 2001; Helmert & Domshlak 2009; Pommerening et al. 2014 |
| **B2. Abstraction** | Map states to an abstract space (homomorphism) and solve there exactly | Pattern databases, merge-and-shrink | Optimistic like B1. Errors concentrate where the abstraction merges distinct states. | Table lookup is C once the table exists; building it is S | Helmert & Domshlak 2009 [S]; Prieditis 1993 [S] |
| **B3. Convex relaxation + rounding** | Replace the integer domain with a convex one (LP/SDP), or dualise constraints (Lagrangian); then round | LP threshold rounding; SDP + hyperplane rounding; Raghavendra's generic SDP | Feasible-by-construction under some roundings, infeasible under others. Ratio guarantees hold on worst cases. | Exact LP is **P-complete** [R, compendium A.4.3] → S. Approximate *positive* LP is parallelisable (Luby & Nisan 1993) [M] → L. | Williamson & Shmoys 2011; Raghavendra 2008 [S]; Yau et al. 2024 [A] |
| **B4. Restriction / over-constraint** | Add constraints or fix part of the solution. Pearl: "loading the original model with additional constraints … solutions … would no longer be admissible", giving upper bounds [R]. In inference: consider only a subset of the premises' models. | Fix an initial subtour; read "A or B" as A; principle of truth; closed world; conditional as biconditional | **Commission** in entailment (illusory inferences). False "no solution" in search. Feasible but suboptimal in optimisation. | C when the restriction is a local rewrite (choose a disjunct). S when it requires a sequential update. | Pearl 1983 [R] |
| **B5. Probabilistic model** | Replace the exact completion cost with its expectation under a distributional model (Pearl's third class) [R] | Expected-cost estimates; independence (mean-field) approximations | Neither sound nor complete. Pearl: estimates can be "grossly overestimated", ending search prematurely [R]. | Usually C (closed-form statistics) | Pearl 1983 [R] |
| **C. Constructive / priority** | Data items are considered in an order (fixed, or adaptive and set after each step) and each gets an **irrevocable** decision: the priority model "to formalize 'greedy-like' or 'myopic' algorithms" [S] | Greedy set cover; matroid greedy; first-fit; DSATUR; NN-TSP; ratio knapsack; unit-clause / shortest-clause SAT heuristics | Always feasible when every partial solution extends (colouring, knapsack); otherwise dead-ends. Fixed order is **order-sensitive**. Random-instance thresholds: UC up to about 8/3 on 3-SAT [S]; optimal myopic up to 3.26 [A]; about 2χ colours [A]. Width-1 pBT cannot approximate knapsack better than n^{−1/4}, while the 1/2-approximation needs width 2 [R]. | Fixed order with lexicographic output is **S**, citable per algorithm: LFMIS (Cook 1985), LF Δ+1 colouring, **NN-TSP tour**, **FFD bin packing**, list scheduling are all P-complete [R, compendium A.2.1, A.2.6, A.2.12, A.4.7, A.4.8]. Random order is **L**: greedy MIS has O(log² n) dependence depth [A]. One-shot scoring (C0) is **C**. | Borodin, Nielsen & Rackoff 2003 [S]; Alekhnovich et al. 2011 [R]; Edmonds 1971; Nemhauser, Wolsey & Fisher 1978; Feige 1998; Achlioptas 2001 [S]; Achlioptas & Sorkin 2000 [A] |
| **C4. Online / one-pass** | Decide each item on arrival with bounded state; judged by competitive ratio. Sketching and streaming give space lower bounds. | First-fit online colouring; ETR-style premise-at-a-time update | **Premise-order reversal changes answers.** Errors on items whose decisive information arrives late. | S in the number of items, but with associative updates a prefix-scan gives L. Sketching dichotomy: polylog-space linear sketches either solve a Max-CSP approximation, or o(√n) space is impossible [A]. | Borodin & El-Yaniv 1998 (review only); Chou, Golovnev, Sudan & Velusamy 2024 [A]; Kapralov, Khanna & Sudan 2015 [M] |
| **D. Systematic search** | Tree of partial assignments with propagation, branching and backtracking. pBT "for backtracking and dynamic programming algorithms" generalises priority algorithms; it "encompasses DPLL in many situations" [R]. | DPLL/CDCL, branch and bound, A*, IDA* | None if run to completion. Truncation gives a default answer, so error correlates with solver hardness (node counts, backbone). 3-SAT needs exponential width in fully adaptive pBT [R]. Heavy-tailed runtimes are why restarts and portfolios help (Gomes et al., title-level). | **S** (exponential; truncation at b decisions is depth O(b)) | Alekhnovich et al. 2011 [R]; Gomes, Selman, Crato & Kautz 2000 [M]; Williams, Gomes & Selman 2003 (in DESIGN) |
| **D3. Parameterised / backdoor** | Search only over a small parameter, e.g. a backdoor set that makes the rest tractable. Kernelisation is sound reduction rules. | FPT branching; backdoor search; preprocessing rules | Exact when the parameter is small. Error rate grows with the parameter. | S (2^k · poly); reduction rules C if applied in parallel | Hromkovič 2004 [M]; Williams, Gomes & Selman 2003 |
| **E. Iterated local message passing** | Each variable or node updates from its neighbours for t rounds, then rounds or decides. An L-layer GNN equals an L-round distributed local algorithm, and problems solvable by a GNN class are exactly those solvable by the matching local-algorithm class [R]. | BP, SP, warning propagation, mean-field, AMP; constant-round local algorithms; NeuroSAT | Fails beyond algorithmic thresholds. Local algorithms give at most a (1/2 + 1/(2√2)) fraction of the max independent set [A]; low-degree polynomials at most half [A]. BP-guided decimation fails at order 2^k/k [S]. Local MCMC works up to clustering, BP up to condensation [A]. GNN approximation ratios are no better than simple greedy without extra features [R]. | **C** for constant t (Sato et al.) [R]. Decimation (E2) is **S**. | Sato et al. 2019 [R]; Gamarnik & Sudan 2017 [A]; Wein 2022 [A]; Bresler & Huang 2021 [A]; Krzakala et al. 2007 [A]; Mézard, Parisi & Zecchina 2002 [M]; Coja-Oghlan 2017 [S]; Kuhn, Moscibroda & Wattenhofer 2016 [A] |
| **F. Local search (SLS / metaheuristics)** | Move between complete candidate solutions via a neighbourhood. Intensification vs diversification is "the two forces that largely determine the behavior of a metaheuristic" [S]. Formal class: PLS. | Hill-climbing, 2-opt, WalkSAT, SA, tabu, GA, ACO | **Infeasible near-misses**: few violated constraints, Hamming-close to solutions. Never certifies UNSAT. Stochastic answers that depend on initialisation. Smoothed 2-opt is polynomial (Englert et al., title-level). OGP blocks "stable" algorithms [A]. | **S** for k steps (depth O(k)). Even *predicting which local optimum* standard local search reaches is PSPACE-complete for local max-cut (Schäffer & Yannakakis 1991) [S]. One step is C. | Blum & Roli 2003 [S]; Hoos & Stützle 2004 [A]; Johnson, Papadimitriou & Yannakakis 1988 [M]; Gamarnik 2021 [A]; Englert, Röglin & Vöcking 2014 [M] |
| **G. Decomposition / DP** | Optimal substructure over a decomposition (tree decomposition, stages) | Treewidth DP, knapsack DP / FPTAS, divide and conquer | Exact when the structure holds. Used heuristically (ignoring cross-links), it becomes B1. | Typically S (stages); GNNs "align" with DP, which lowers sample complexity [A] | Xu et al. 2020 [A]; Dudzik & Veličković 2022 [M]; Williamson & Shmoys 2011 |
| **H. Randomised guessing & sampling** | Sample from a simple distribution, optionally check, optionally restart | Uniform random assignment; random walk with restarts; sample-models-and-check | Accuracy at chance, independent of structure. Random assignment satisfies 7/8 of E3 clauses, which is optimal unless P = NP [S]. | C (one sample); S with restarts or long walks | Håstad 2001 [S]; Schöning 1999 [M]; Paturi, Pudlák & Zane 1997 [M] |
| **I. Meta-level** | Rice: problem, feature, algorithm and performance spaces, and a selection mapping from features to algorithm [S]. Hyper-heuristics split into *selection* vs *generation*, and *constructive* vs *perturbative* [S]. | SATzilla; portfolios; hyper-heuristics; learned branching (imitating strong branching); NCO; FunSearch, EoH, ReEvo | Inherits base errors, plus *selection errors that correlate with features*. LLM-evolved heuristics generalise poorly [A] and stay inside greedy templates [A]. | Selector is C (features → choice); the base varies | Rice 1976 [S]; Xu et al. 2008 [M]; Kerschke et al. 2019 [M]; Burke et al. 2010/2013 [S]; Bengio, Lodi & Prouvost 2021 [M]; Romera-Paredes et al. 2024 [R]; Liu et al. 2024 [A]; Ye et al. 2024 [A] |

**Why A–I and not the textbook list.** Some items on the textbook list are not classes in their own right:

- "Approximation algorithms", "randomised algorithms" and "parameterised algorithms" are *properties* or *resource analyses* that cut across mechanisms.
- "Hyper-heuristics" and "portfolios" are *meta* constructions over the other classes.

The classes A–I are mechanism classes. Most of them have a formal model with lower bounds:

- C: priority algorithms;
- D: pBT;
- E: LOCAL and low-degree polynomials;
- F: PLS;
- C4: sketching.

---

## Theories of heuristics (for deriving zoo members)

We recommend three generators. Each yields candidates mechanically for a new domain, and each also predicts a C/S label and an error signature.

### Theory 1: Pearl's simplified-model calculus (relax / restrict / probabilistic), plus decomposability

**What the source says** (Pearl 1983, *On the Discovery and Generation of Certain Heuristics*, AI Magazine 4(1)) [R]:

- **The paradigm.** "heuristics are discovered by consulting simplified models of the problem domain."
- **Relaxation.** Typical heuristics "can be obtained by the process of deleting constraints from the original problem and solving the relaxed problem." For TSP:
  - deleting connectivity gives the *assignment* heuristic;
  - deleting the degree-2 condition gives the *MST* heuristic.
- **Consistency.** "heuristics generated by optimizations over relaxed models are guaranteed to be consistent."
- **Two further kinds of simplification.**
  - *Over-constrained* models, e.g. "assume that a certain portion of the solution is given a-priori". These give upper bounds and are not admissible.
  - *Probabilistic* models, which estimate the most probable completion cost and can overestimate.
- **Simpler is not guaranteed.** Not every relaxation is simpler: diagonal jumps in the 8-puzzle make the search "shallower" but "bushier".
- **Mechanical generation.** Refine and delete constraints "until a semidecomposable model is identified". Simplicity comes from decomposability:
  - fully independent sub-goals, as in the most relaxed 8-puzzle;
  - semi-decomposable structures where a greedy "cheapest-subgoal-first" order is optimal thanks to *commutativity* (MST);
  - semi-decomposable structures with a *partial order on subgoals* (the swap-sort 8-puzzle).

**Modern descendants.** These turn Pearl's idea into a lattice with dominance relations:

- Helmert & Domshlak (2009) prove that admissible heuristics from delete relaxation, critical paths, abstractions and landmarks "are in fact very closely related". They derive dominance results, e.g. merge-and-shrink strictly dominates landmark and additive h^max heuristics [S].
- Pommerening et al. (2014) put landmarks, the state equation and post-hoc optimisation into one LP over operator counts ("operator-counting") [S].
- Mostow & Prieditis (1989) and Prieditis (1993) automate the discovery of admissible heuristics by abstraction transformations, which are admissible because they add "shortcut" paths [S].

**How it generates zoo members (our proposal).** Write the domain as a conjunction of constraint types over a solution object, then generate three families:

1. **Relaxations `RELAX(S)`.** Delete a constraint set S and solve the rest exactly.
   - *Entailment:*
     - `UP-k`: relax the proof system to k rounds of unit resolution;
     - `RES-w`: bounded-width resolution;
     - `PREMISE-SUBSET(sel)`: conclude only what follows from the last j premises, or from the categorical premises only.

     All of these are **sound**, so they produce omission errors only.
   - *SAT:* `2SAT-CORE` keeps the clauses of length ≤ 2, solves them, then fills by default. Its errors violate only clauses that were dropped (a diagnosable violation profile).
   - *Coloring:* drop edges by a rule (the latest-mentioned, or the longest-range in the layout), then colour exactly. This replaces part of `HALLUC-CONSTRAINT` with a *systematic*, testable member.
   - *TSP:* MST-based or assignment-based tours.
2. **Restrictions `RESTRICT(T)`.** Add constraints T or fix parts of the solution.
   - *Entailment:*
     - `FIRST`, `MATCH`: select one disjunct;
     - `MM` (principle of truth);
     - `ETR` (issue-matching filter);
     - `CLOSED-WORLD`: unmentioned atoms are false;
     - `BICONDITIONAL`: read "if" as "iff".

     All of these are **unsound**, so they produce commission errors.
   - *SAT:* fix variables by polarity, then propagate.
   - *Knapsack:* fix the k best-ratio items.
3. **Probabilistic models.** Replace exact constraints with independence assumptions and expectations, giving mean-field and BP marginals (`BP-t`), and expected satisfaction (`POLARITY` / `FREQ` as zero-round special cases).

**Predicted signatures** (our derivation, to be checked in simulation):

| Kind of simplified model | Decision problems "is there a solution?" (SAT) | Entailment "does C follow?" (coNP) | Optimisation |
|---|---|---|---|
| Relaxation | Biased toward YES (accepts some UNSAT) | **Omission only** (sound) | Optimistic value; returned object infeasible in a specific way |
| Restriction | Biased toward NO (rejects some SAT) | **Commission** (illusory inferences) | Feasible, suboptimal |
| Probabilistic | Two-sided | Two-sided | Two-sided |

**Depth link (our interpretation, to verify per heuristic).** The decomposability of the relaxed model predicts the class:

- **fully decomposable** relaxed model (sum or max of independent local terms) → **C**;
- **semi-decomposable**, greedy-solvable → **S**, by the compendium's P-completeness of lexicographic greedy outputs;
- **not decomposable** → search (D).

### Theory 2: formal paradigm models as parametric templates

**What the sources say.**

- **Alekhnovich et al. (2011)** [R] start from the observation that "algorithmic paradigms are rarely, if ever, precisely defined". They define pBT:
  - "an algorithm creates a tree of solutions, where each branch … builds a solution one item at a time";
  - orders can be *fixed*, *adaptive* or *fully adaptive*;
  - width counts parallel branches.

  The model "generalizes both the priority model of Borodin, Nielson and Rackoff, as well as a simple dynamic programming model due to Woeginger". Results:
  - knapsack optimality needs exponential width (adaptive order);
  - width 1 cannot beat n^{−1/4}, whereas width 2 achieves 1/2;
  - 2-SAT needs linear width in adaptive order but exponential width in fixed order;
  - 3-SAT needs exponential width in the fully adaptive model.
- **Sato et al. (2019)** [R] show that GNN classes equal LOCAL-model classes: SB(1), MB(1) and VV_C(1), "strictly nested". They prove optimal ratios: (Δ+1) for minimum dominating set, improving to (Δ+1)/2 with a weak 2-colouring; and 2 for minimum vertex cover.
- **Low-degree polynomials** capture Fix, BP/SP-guided decimation with few rounds and local algorithms, and fail above κ*·2^k log k / k on random k-SAT (Bresler & Huang 2021) [A].

**How it generates zoo members.** Each template is a small parameter space, and the zoo becomes a *grid* over it:

- `PRIORITY(order ∈ {input, random, static-score, adaptive-score}, score, decision rule)`:
  - SAT gives `GREEDY` (input order), `MOMS` (static score), `UC`/`GUC` (adaptive), and PPZ-style forcing (random order);
  - coloring gives `FIRST-FIT`, `LARGEST-FIRST`, `DSATUR`, `RANDOM-ORDER-FIRST-FIT`;
  - knapsack gives `RATIO`, `VALUE`, `LARGEST-FIT`;
  - TSP gives `NN-*`, `INPUT-ORDER`.
- `pBT(order, width w, depth budget b)`: `DPLL-b`, beam search. Width 2 recovers `RATIO+BEST-SINGLE` (the 1/2-approximation for knapsack).
- `LOCAL(t rounds, message type ∈ {hard (UP/WP), soft (BP), survey (SP)}, readout)`: `UP-k`, `BP-t`, `SP-t`, `LOCAL-t` colouring.
- `PLS(neighbourhood, acceptance ∈ {descent, noise p, temperature}, steps k)`: `WALK-k`, `2OPT-k`, min-conflicts.

Each template carries **lower bounds**, i.e. predictions that a member *cannot* do something, and a **depth label**:

- LOCAL with constant t → C;
- random-order priority → L;
- fixed-order lexicographic priority → S (P-complete);
- pBT and PLS → S.

### Theory 3: bounded optimality and resource rationality, with ecological rationality

**What the sources say.**

- **Russell & Subramanian (1995)** [A]: "an agent is bounded-optimal if [i]ts program is a solution to the constrained optimization problem presented by its architecture and the task environment."
- **Lieder & Griffiths (2020)** [A] propose "the rational use of limited resources as a unifying principle", which "can reconcile the mind's most impressive cognitive skills with people's ostensive irrationality".
- **Ecological rationality** gives exact conditions under which simple rules are optimal. With binary cues and noncompensatory weights (w_i > Σ_{j>i} w_j), "the linear decision rule and the corresponding lexicographic decision rule decide identically" (Şimşek 2013, citing Martignon & Hoffrage 1999/2002) [R]. Şimşek also shows that dominance and cumulative dominance are common across 51 natural datasets, so simple rules can "reach the accuracy levels of the linear decision rule using less information" [R].

**How it generates zoo members (our proposal).** This is the decision-theoretic version of O6's MDL objective: h\* = argmax_{P : depth(P) ≤ d, |P| ≤ ℓ} E_{x∼D}[acc(P, x)]. Generate candidates by *solving this program search* on our item distribution:

- enumerate short RASP-L programs under a depth cap; or
- run FunSearch- or EoH-style LLM program search restricted to a C-class template (e.g. "one scoring pass + threshold") and to an S-class template (e.g. "priority loop").

The winners are the bounded-optimal heuristics for each budget. They are the most principled entries for O6 prediction 1 (the Pareto frontier).

Ecological rationality also gives **environment manipulations**: change D so that a different heuristic becomes bounded-optimal. Two examples:

- planted SAT instances with biased literal polarity make `POLARITY` near-optimal;
- balanced-polarity instances make it useless.

A model whose mixture weights track the bounded-optimal heuristic across environments is selecting strategies (Lieder & Griffiths 2017, *Strategy selection as rational metareasoning* [M]), which is what H4 asks about.

**A fourth generator for class A.** Kahneman & Frederick's attribute substitution [S] generates cue heuristics: list the *accessible attributes* of an item, then threshold each one. Accessible attributes include density, length, polarity skew, atom overlap with the question, recency, and premise mood.

---

## When and why heuristics work

| Result | What the source claims | What it means for us (interpretation) |
|---|---|---|
| **No Free Lunch** (Wolpert & Macready 1997) [S/M] | Averaged over all problems, any gain on one class is offset on another | Heuristic quality is *distribution-relative*. Report every heuristic's δ under our D (Bogdanov–Trevisan framing), never "in general". |
| **Matroid greedy** (Edmonds 1971) [M]; **submodular greedy** (Nemhauser, Wolsey & Fisher 1978) [M]; **set cover ln n threshold** (Feige 1998) [M] | Greedy is exact on matroids; has guarantees for submodular maximisation; and greedy's ln n ratio for set cover is the best possible (title-level) | Structure explains greedy success. Pearl's "commutativity" condition for greedy-optimal MST is the matroid property in his own words. |
| **PCP / hardness of approximation** (Arora et al. 1998) [M]; **Håstad 2001** [S] | MAX-E3-SAT cannot be approximated beyond 7/8 unless P = NP, and a uniformly random assignment achieves 7/8 | Even `RANDOM` is worst-case optimal for some objectives. Any model answer satisfying < 7/8 of clauses is worse than random, which is a cheap diagnostic. |
| **Raghavendra 2008** [S]; **Yau et al. 2024** [A] | Under the UGC, a generic SDP gives the best ratio for every CSP. Polynomial-sized message passing can represent these optimal algorithms. | A single relaxation-plus-rounding "super-heuristic" exists for approximate CSPs and is message-passing-expressible. It is a principled upper anchor for the zoo, though not a plausible LLM procedure. |
| **Smoothed analysis** (Spielman & Teng 2004) [A]; **2-opt** (Englert, Röglin & Vöcking 2014) [M] | Smoothed complexity is the "maximum over inputs of the expected performance" under small random perturbations. The simplex method is polynomial in this sense. | Explains why local search with small k may suffice on typical items. Supports `2OPT-k` / `WALK-k` with small k. |
| **Beyond worst case** (Roughgarden ed. 2021) [A] | Worst-case guarantees are often impossible, so "a more nuanced analysis approach is called for" | Frames O1's "heuristic-relative hardness" axis |
| **Average-case definitions** (Bogdanov & Trevisan 2006) [R]; Impagliazzo 1995 [M] | Formal heuristic, errorless heuristic (⊥) and heuristic scheme; HeurP and AvgP | Gives us vocabulary. "Declared impossible" (DESIGN §5.5) is the ⊥ of an errorless heuristic. |
| **Algorithmic thresholds on random CSPs**: Achlioptas 2001 [S]; Achlioptas & Sorkin 2000 [A]; Achlioptas & Coja-Oghlan 2008 [A]; Krzakala et al. 2007 [A]; Coja-Oghlan 2017 [S]; Bresler & Huang 2021 [A] | UC works below 8/3 on 3-SAT. Optimal myopic algorithms reach 3.26. Known colouring algorithms use 2χ, the point where the solution-space geometry changes from "giant ball" to "error-correcting code". Local MCMC works up to clustering, BP up to condensation, and "survey propagation may beat also this threshold". BP-guided decimation fails at order 2^k/k. Low-degree polynomials fail above about 4.911·2^k log k / k. | Each zoo member has a characteristic **success-vs-density curve**. Compute these curves by simulation on our generator, and compare the knee of the model's error curve with them (new signature). The asymptotic-in-k results don't give numbers for k = 3, so measure them. |
| **Overlap gap property** (Gamarnik 2021) [A]; Gamarnik, Jagannath & Wein 2020 [A]; Gamarnik & Sudan 2017 [A]; Wein 2022 [A] | Near-optimal solutions of random problems show a disconnected overlap structure. This rules out "stable" algorithms: low-degree polynomials, **low-depth Boolean circuits**, Langevin dynamics and local algorithms. | A formal reason why class-C procedures fail on random optimisation: "low-depth circuits fail" (GJW) is close to a theorem about direct-answer mode. |
| **Backbones and backdoors** (Monasson et al. 1999 [M]; Williams, Gomes & Selman 2003, in DESIGN) | Typical-case complexity relates to the nature of the phase transition (2+p-SAT, title-level). Small backdoors explain industrial tractability. | Backbone size and backdoor size are the natural covariates for D-class truncation errors |
| **Heavy tails and portfolios** (Gomes et al. 2000; Gomes & Selman 2001) [M] | Heavy-tailed phenomena in SAT/CSP search; algorithm portfolios (title-level) | Run-to-run variance of truncated search is large, so we need repeats for D-class identification |
| **Ecological rationality** (Martignon & Hoffrage 2002; Şimşek 2013) [R via Şimşek] | Exact equivalence of lexicographic and linear rules under noncompensatory weights. Dominance structures are prevalent. | Lets us *construct* environments where cue heuristics are optimal, versus environments where they fail |

---

## Bounded-compute heuristics (class C vs S)

### What is established

1. **Constant-round local algorithms are exactly GNNs** (Sato et al. 2019) [R]. "An L-layer GNN corresponds to a distributed algorithm that runs for exactly L communication rounds." Classic constant-round results then carry over: no GNN gets below a 2-approximation for vertex cover, and optimal ratios are "no better than simple greedy methods in the degree-only setting".

   *Interpretation:* `UP-k`, `BP-t`, `WP-t` and `LOCAL-t` colouring are the natural **C** members. A transformer layer can attend over a clause–variable incidence structure, so k rounds of propagation should fit within O(k) layers. This needs a RASP-L construction (O6).
2. **Lower bounds for local computation** (Kuhn, Moscibroda & Wattenhofer 2016) [A]. They give "the first poly-logarithmic lower bound on such local computation" for minimum vertex cover, minimum dominating set, maximum matching and MIS.
3. **Low-degree and OGP barriers for "simple" algorithms on random instances** (Gamarnik, Jagannath & Wein 2020; Wein 2022; Bresler & Huang 2021) [A]. Low-degree polynomials and low-depth circuits cannot beat half-optimal independent sets, or the about 4.911·2^k log k / k density for k-SAT.
4. **P-completeness of standard greedy outputs.** All of these are verified in the Greenlaw–Hoover–Ruzzo compendium (TR91-11), which was read this session [R]:
   - **LFMIS** (Cook 1985). The compendium adds that "determining the ith node chosen by any deterministic sequential algorithm" for LFMIS is also complete, and that "computing or approximating the size" of the LFMIS is P-complete.
   - **LF Δ+1 vertex colouring** (Luby 1984): "examining each vertex in order and coloring it with the smallest available color". This is our `FIRST-FIT`.
   - **Nearest-neighbour TSP heuristic**: "a greedy heuristic that always chooses the nearest unvisited vertex". This is our `NN-from-0`.
   - **First-fit-decreasing bin packing** (Anderson, Mayr & Warmuth 1989). The same paper gives an NC algorithm matching FFD's *performance bound* [S]: the *guarantee* is parallelisable even though the *output* is not.
   - **General list scheduling.**
   - **Unit resolution and Horn unit resolution** (Jones & Laaser 1976). This makes our unbounded `UP` S.
   - **Relaxed consistent labelling** (Kasif): discrete relaxation / arc consistency [S, R].
   - **Linear programming.**
   - **Superincreasing knapsack** (remark under A.8.5).
5. **Random order helps.** Sequential greedy MIS and matching have O(log² n) dependence depth under a random order on any graph, with output "the same result as the sequential greedy algorithms" (Blelloch, Fineman & Shun 2012) [A]. Luby's MIS algorithm [M] is the classic NC MIS (it computes *a* maximal independent set, not the lexicographically first).
6. **Local search trajectories are worse than P-complete in general.** Finding the local optimum that standard local search reaches from a given start is PSPACE-complete for local max-cut (Schäffer & Yannakakis 1991) [S]. Finding *some* local optimum is PLS-complete.
7. **Streaming and sketching.** For Max-CSPs there is a dichotomy: either polylog-space linear sketches suffice for a given approximation, or o(√n) space is impossible (Chou et al. 2024) [A]. Max-CUT streaming lower bounds: Kapralov, Khanna & Sudan 2015 [M].

### What follows for the zoo (interpretation)

- **The output of a fixed-order greedy is S, but the greedy's *quality* may be L.** FFD shows the guarantee is achievable in NC while the exact output is P-complete. Our identification scores *outputs*, so a no-CoT model can reproduce FFD's *ratio* but not FFD's *packing* at scale. Exact-trace agreement with a P-complete heuristic in direct-answer mode at large n is therefore evidence *against* the model computing that heuristic. The agreement must come from a shallower procedure that coincides with it on those items.
- **Within knapsack, `RATIO` splits into C and S members** (our derivation).
  - `RATIO-PREFIX` (sort by ratio; take items until the first one that doesn't fit) needs only sorting plus prefix sums and threshold.
  - `RATIO-SKIP` (skip items that don't fit and continue) solves superincreasing knapsack exactly when run in decreasing-weight order. Superincreasing knapsack is P-complete, so computing `RATIO-SKIP`'s output is P-hard.

  The C label for `RATIO-PREFIX` rests on sorting being in TC⁰, which is unverified here.
- **`UP-k` is C for constant k; `UP` to fixpoint is S.** This matches DESIGN's "C for small k", and now has a citation (compendium A.6.1–A.6.2).
- **ETR and MM:** the depth is the number of sequential premise updates. They are constant at a fixed premise count and sequential along a premise-count sweep. Label them relative to the size parameter of the sweep.

### Proposed three-way class

| Class | Definition | Members | Evidence |
|---|---|---|---|
| **C** | O(1) rounds independent of n | A-class cues; C0 one-shot scoring; `UP-k`, `BP-t`, `LOCAL-t` for constant k, t; single-sample `RANDOM`; `RATIO-PREFIX` (if sorting ∈ TC⁰) | Sato et al. 2019; DESIGN O2 (TC⁰) |
| **L** | polylog(n) rounds, i.e. looped transformers or CoT of O(log n) steps | `RANDOM-ORDER-FIRST-FIT`, random-order greedy MIS / matching; Luby-style MIS; approximate positive LP | Blelloch et al. 2012; Luby 1986; Luby & Nisan 1993 |
| **S** | Inherently sequential: P-complete output, or exponential | `FIRST-FIT`, `NN-from-0`, `GREEDY`*, `UP` (fixpoint), arc consistency, exact LP, `RATIO-SKIP`, FFD, `WALK-k`/`2OPT-k` (k growing), `DPLL-b` | Compendium A.2.1, A.2.6, A.2.12, A.4.3, A.4.7, A.6.1–2, A.6.4; Schäffer & Yannakakis 1991; pBT lower bounds |

\* `GREEDY` (SAT, mention order, never backtrack) has no direct P-completeness result found. Its S label is by analogy with LFMIS and LF colouring.

---

## Key sources

| Citation | Link | Claim (tag) | How we'd use it |
|---|---|---|---|
| Pearl, J. (1983). *On the Discovery and Generation of Certain Heuristics.* AI Magazine 4(1):23–33 | https://ftp.cs.ucla.edu/pub/stat_ser/r39-reprint.pdf | Heuristics come from simplified models: relaxed (constraint deletion; admissible and consistent), over-constrained (upper bounds) and probabilistic. Mechanical generation by deleting constraints until the model is semi-decomposable; greedy is optimal under commutativity. [R] | Theory 1, the main generator. Relax vs restrict maps to omission vs commission. |
| Pearl, J. (1984). *Heuristics: Intelligent Search Strategies for Computer Problem Solving.* Addison-Wesley | https://doi.org/10.1016/s0736-5853(86)80081-8 (review record) | Book-length treatment; only book reviews were found [M] | Cite the 1983 paper for specific claims |
| Alekhnovich, Borodin, Buresh-Oppenheim, Impagliazzo, Magen & Pitassi (2011). *Toward a Model for Backtracking and Dynamic Programming.* Computational Complexity 20:679–740 | https://doi.org/10.1007/s00037-011-0028-y · https://www.cs.toronto.edu/~toni/Papers/backtracking-dp.pdf | pBT generalises priority algorithms and simple DP and encompasses DPLL in many settings. Width and order lower bounds for knapsack, interval scheduling and SAT. [R] | Theory 2: the template for C and D classes, with impossibility predictions |
| Borodin, Nielsen & Rackoff (2003). *(Incremental) Priority Algorithms.* Algorithmica 37:295–326 | https://doi.org/10.1007/s00453-003-1036-3 | A formal model of greedy-like (myopic) algorithms with fixed vs adaptive priorities [S] | Defines the C (constructive) class and the `PRIORITY(order, score, rule)` family |
| Sato, Yamada & Kashima (2019). *Approximation Ratios of Graph Neural Networks for Combinatorial Problems.* NeurIPS | https://arxiv.org/abs/1905.10261 | GNN classes equal constant-round local-algorithm classes. Optimal ratios (Δ+1 for dominating set, 2 for vertex cover); no better than greedy without extra features. [R] | Grounds class C for message-passing heuristics |
| Greenlaw, Hoover & Ruzzo (1991). *A Compendium of Problems Complete for P* (TR91-11, U. Alberta); book: *Limits to Parallel Computation* (OUP 1995) | https://doi.org/10.7939/R39Z90F7X · https://doi.org/10.1093/oso/9780195085914.001.0001 | P-complete: LFMIS, LF Δ+1 colouring, NN-TSP heuristic, FFD bin packing, list scheduling, unit resolution, Horn, relaxed consistent labelling, LP, superincreasing knapsack [R] | Citable S labels for `FIRST-FIT`, `NN-from-0`, `UP`, `RATIO-SKIP`; depth-stress gadgets |
| Cook, S. A. (1985). *A taxonomy of problems with fast parallel algorithms.* Information and Control 64:2–22 | https://doi.org/10.1016/s0019-9958(85)80041-3 | LFMIS is P-complete (via the compendium) [M/S] | Canonical citation for "lexicographic greedy is inherently sequential" |
| Blelloch, Fineman & Shun (2012). *Greedy Sequential Maximal Independent Set and Matching are Parallel on Average.* SPAA | https://arxiv.org/abs/1202.3205 | Random-order greedy MIS has O(log² n) dependence depth on any graph, with the same output as sequential [A] | Grounds the proposed L class; `RANDOM-ORDER-FIRST-FIT` |
| Anderson, Mayr & Warmuth (1989). *Parallel approximation algorithms for bin packing.* Information and Computation | https://doi.org/10.1016/0890-5401(89)90003-5 | FFD is P-complete, yet an NC algorithm achieves FFD's performance bound [S] | Output vs guarantee distinction for C/S claims |
| Kasif, S. (1990). *On the parallel complexity of discrete relaxation in constraint satisfaction networks.* AIJ 45(3) | https://doi.org/10.1016/0004-3702(90)90009-o | Arc consistency is P-complete [S] | S label for propagation-to-fixpoint in CSP domains |
| Jones & Laaser (1976). *Complete problems for deterministic polynomial time.* TCS | https://doi.org/10.1016/0304-3975(76)90068-2 | Unit resolution is P-complete (compendium A.6.1) [S] | `UP` vs `UP-k` |
| Schäffer, A. A. (with Yannakakis) (1991). *Simple Local Search Problems that are Hard to Solve.* SIAM J. Comput. 20(1) | https://doi.org/10.1137/0220004 | Local max-cut (flip) is PLS-complete; the "standard algorithm problem" is PSPACE-complete [S] | S label for local-search trajectories (`WALK-k`, `2OPT-k`) |
| Johnson, Papadimitriou & Yannakakis (1988). *How easy is local search?* JCSS | https://doi.org/10.1016/0022-0000(88)90046-3 | Defines PLS [M] | Formal model for class F |
| Bresler & Huang (2021). *The Algorithmic Phase Transition of Random k-SAT for Low Degree Polynomials.* FOCS | https://arxiv.org/abs/2106.02129 | Low-degree polynomials (incl. Fix, few-round BP/SP decimation, local algorithms) fail above (1+o(1))κ*·2^k log k / k, κ* ≈ 4.911; Fix works to (1−o(1))·2^k log k / k [A] | Class-C barrier on random SAT; threshold signature |
| Gamarnik, Jagannath & Wein (2020). *Low-Degree Hardness of Random Optimization Problems* (journal title: *Hardness of Random Optimization Problems for Boolean Circuits, Low-Degree Polynomials, and Langevin Dynamics*). FOCS | https://arxiv.org/abs/2004.12063 | Low-degree polynomials, low-depth circuits and Langevin dynamics fail near-optimality via OGP and stability [A] | Formal "constant-depth can't" result |
| Gamarnik, D. (2021). *The overlap gap property: A topological barrier to optimizing over random structures.* PNAS | https://doi.org/10.1073/pnas.2108492118 · https://arxiv.org/abs/2109.14409 | OGP rules out algorithms with input stability [A] | Theory of when C-class and local-search heuristics fail |
| Gamarnik & Sudan (2017). *Limits of local algorithms over sparse random graphs.* Annals of Probability | https://arxiv.org/abs/1304.1831 · https://doi.org/10.1214/16-aop1114 | Local algorithms' independent sets are a 1/2 + 1/(2√2) factor below the maximum, via clustering [A] | LOCAL-class error signature |
| Wein, A. S. (2022). *Optimal low-degree hardness of maximum independent set.* Math. Stat. & Learning | https://arxiv.org/abs/2010.06563 | Low-degree polynomials reach half-optimal independent sets, no more; this generalises Rahman–Virág for local algorithms [A] | Same |
| Achlioptas & Coja-Oghlan (2008). *Algorithmic Barriers from Phase Transitions.* FOCS | https://arxiv.org/abs/0803.2122 | Known algorithms colour random graphs with 2χ colours; the solution-space geometry changes exactly there; analogous transitions for k-SAT [A] | Threshold signature for greedy colouring |
| Krzakala, Montanari, Ricci-Tersenghi, Semerjian & Zdeborová (2007). *Gibbs states and the set of solutions of random CSPs.* PNAS | https://arxiv.org/abs/cond-mat/0612365 | Clustering then condensation; local MCMC works up to clustering, BP up to condensation, SP may go beyond [A] | Ordering of the E and F classes by threshold |
| Achlioptas & Sorkin (2000). *Optimal myopic algorithms for random 3-SAT.* FOCS | https://researchonline.lse.ac.uk/id/eprint/35848 | Optimal algorithms in the unit-clause framework establish r₃ > 3.26 [A] | Threshold for `UC`/`GUC`/`UP+GUESS` |
| Achlioptas, D. (2001). *Lower bounds for random 3-SAT via differential equations.* TCS | https://doi.org/10.1016/s0304-3975(01)00159-1 | UNIT CLAUSE succeeds with positive probability below 8/3; differential-equation analysis of myopic algorithms [S] | Same |
| Coja-Oghlan, A. (2017). *Belief Propagation Guided Decimation Fails on Random Formulas.* JACM | https://doi.org/10.1145/3005398 · https://arxiv.org/abs/1007.1328 | BP-guided decimation fails at m/n of order 2^k/k [S] | Threshold for `BP-DEC` |
| Bogdanov & Trevisan (2006). *Average-Case Complexity.* FnT TCS | https://arxiv.org/abs/cs/0606037 | Formal definitions: heuristic algorithm (error δ), errorless heuristic (⊥), HeurP, AvgP [R] | The formal definition of "heuristic" for DESIGN §3 |
| Russell & Subramanian (1995). *Provably Bounded-Optimal Agents.* JAIR | https://doi.org/10.1613/jair.133 | Bounded optimality: the program solves the constrained optimisation set by architecture and environment [A] | Theory 3; justifies O6's objective |
| Lieder & Griffiths (2020). *Resource-rational analysis.* Behavioral and Brain Sciences 43 | https://doi.org/10.1017/s0140525x1900061x | The rational use of limited resources as a unifying principle [A] | Theory 3 |
| Şimşek, Ö. (2013). *Linear decision rule as aspiration for simple decision heuristics.* NeurIPS | https://proceedings.neurips.cc/paper/2013/hash/e48e13207341b6bffb7fb1622282247b-Abstract.html | Dominance, cumulative dominance and noncompensatoriness make simple rules equal to the linear rule; prevalent in 51 datasets [R] | Environment manipulations; when cue heuristics win |
| Martignon & Hoffrage (2002). *Fast, frugal, and fit.* Theory and Decision 52:29–71 | https://doi.org/10.1023/a:1015516217425 | Lexicographic equals linear under noncompensatory binary weights (via Şimşek) [S] | Same |
| Gigerenzer & Goldstein (1996). *Reasoning the fast and frugal way.* Psych. Review | https://doi.org/10.1037/0033-295x.103.4.650 | Take-the-best and fast and frugal models [M] | Class A |
| Kahneman & Frederick (2002). *Representativeness Revisited: Attribute Substitution in Intuitive Judgment.* In *Heuristics and Biases*, CUP | https://doi.org/10.1017/cbo9780511808098.004 | A computationally complex target attribute is replaced by an accessible heuristic attribute [S] | Generator for class A; `TEXTBOOK-TRANSFER` as substitution |
| Helmert & Domshlak (2009). *Landmarks, Critical Paths and Abstractions: What's the Difference Anyway?* ICAPS | https://doi.org/10.1609/icaps.v19i1.13370 | Relaxation, critical-path, abstraction and landmark heuristics are closely related; dominance results; LM-cut [S] | Lattice and dominance view of Pearl-style relaxations |
| Pommerening, Röger, Helmert & Bonet (2014). *LP-Based Heuristics for Cost-Optimal Planning.* ICAPS | https://doi.org/10.1609/icaps.v24i1.13621 | The operator-counting LP unifies landmark, state-equation and post-hoc heuristics [S] | Relaxations as LP constraints: combinable zoo members |
| Blum & Roli (2003). *Metaheuristics in Combinatorial Optimization: Overview and Conceptual Comparison.* ACM Comput. Surv. 35(3):268–308 | https://doi.org/10.1145/937503.937505 | Intensification and diversification (the "I&D frame") as the organising forces of metaheuristics [S] | Parameters of class F |
| Hoos & Stützle (2004). *Stochastic Local Search: Foundations and Applications.* Morgan Kaufmann | https://www.cs.ubc.ca/~hoos/SLS-Book/about.html | Systematic SLS treatment (SAT, CSP, TSP, scheduling) [A] | Reference implementations for F |
| Williamson & Shmoys (2011). *The Design of Approximation Algorithms.* CUP | https://www.designofapproxalgs.com/ | Organised by technique: greedy and local search, DP, LP/SDP, randomisation; hardness of approximation [A] | Supports treating "guarantee" as an axis |
| Burke, Gendreau, Hyde, Kendall, Ochoa, Özcan & Qu (2013). *Hyper-heuristics: a survey of the state of the art.* JORS; and Burke et al. (2010). *A Classification of Hyper-heuristic Approaches.* Handbook of Metaheuristics | https://doi.org/10.1057/jors.2013.71 | Selection vs generation; constructive vs perturbative; with or without learning [S] | Class I; LLM-designed heuristics are "generation" hyper-heuristics |
| Rice, J. R. (1976). *The Algorithm Selection Problem.* Advances in Computers 15 | https://doi.org/10.1016/s0065-2458(08)60520-3 | Problem, feature, algorithm and performance spaces; a selection mapping [S] | Feature-dependent mixture weights in O3 |
| Xu, Hutter, Hoos & Leyton-Brown (2008). *SATzilla.* JAIR | https://doi.org/10.1613/jair.2490 | Portfolio-based algorithm selection for SAT [M] | Class I; feature sets for SAT items |
| Håstad, J. (2001). *Some optimal inapproximability results.* JACM 48(4) | https://doi.org/10.1145/502090.502098 | 7/8 is optimal for MAX-E3-SAT unless P = NP; random assignment achieves it [S] | `RANDOM` baseline and diagnostic |
| Raghavendra, P. (2008). *Optimal algorithms and inapproximability results for every CSP?* STOC | https://doi.org/10.1145/1374376.1374414 | Under the UGC a generic SDP is optimal for every CSP [S] | Upper anchor for relaxation-class heuristics |
| Yau, Karalias, Lu, Xu & Jegelka (2024). *Are Graph Neural Networks Optimal Approximation Algorithms?* | https://arxiv.org/abs/2310.00526 | Polynomial-sized message passing can represent the UGC-optimal algorithms for Max-CSP (OptGNN) [A] | Bridge between B3 and E |
| Spielman & Teng (2004). *Smoothed analysis of algorithms.* JACM | https://arxiv.org/abs/cs/0111050 | Max over inputs of expected performance under perturbation; the simplex method is polynomial in this sense [A] | Why local search works on typical items |
| Wolpert & Macready (1997). *No free lunch theorems for optimization.* IEEE TEC 1(1):67–82 | https://doi.org/10.1109/4235.585893 | No algorithm is better on average over all problems [S] | Distribution-relative reporting |
| Romera-Paredes et al. (2024). *Mathematical discoveries from program search with large language models* (FunSearch). Nature | https://doi.org/10.1038/s41586-023-06924-6 · https://pmc.ncbi.nlm.nih.gov/articles/PMC10794145 | The discovered bin-packing heuristic packs into the tightest bin "only if the fit is tight", avoiding small gaps; search favours "shorter programs" and "low Kolmogorov complexity" [R] | Generator for bounded-optimal zoo members; ties to O6's MDL |
| Liu et al. (2024). *Evolution of Heuristics* (EoH). ICML, PMLR 235 | https://proceedings.mlr.press/v235/liu24bs.html | Co-evolves natural-language "thoughts" and code; beats FunSearch with fewer queries [A] | Same |
| Ye et al. (2024). *ReEvo: LLMs as Hyper-Heuristics with Reflective Evolution.* NeurIPS | https://arxiv.org/abs/2402.01145 | "Language Hyper-Heuristics"; reflective evolution across heuristic types [A] | Same |
| Quan, Sun & López-Ibáñez (2025). *Re-evaluating LLM-based Heuristic Search: A Case Study on the 3D Packing Problem* | https://arxiv.org/abs/2509.02297 | The LLM "concentrated its efforts almost exclusively on refining the scoring function" in a greedy solver; performance on par with human greedy [A] | Evidence that LLM heuristics are priority-function choices inside templates |
| Sim, Renau & Hart (2025). *Beyond the Hype: Benchmarking LLM-Evolved Heuristics for Bin Packing.* EvoApplications | https://arxiv.org/abs/2501.11411 | "most of the LLM heuristics do not generalise well" [A] | Caution for using LLM search as a generator |
| Xu et al. (2020). *What Can Neural Networks Reason About?* ICLR | https://arxiv.org/abs/1905.13211 | Algorithmic alignment: GNNs align with DP; better alignment lowers sample complexity [A] | A rival complexity measure for O6/H2 |
| Selsam et al. (2019). *Learning a SAT Solver from Single-Bit Supervision* (NeuroSAT). ICLR | https://arxiv.org/abs/1802.03685 | Solves larger and harder problems "by simply running for more iterations"; not competitive with SOTA [A] | A learned E-class solver whose depth scales with iterations, an analogue of CoT |

Also verified this session (metadata [M] unless noted), for use as needed:

- Edmonds 1971, *Matroids and the greedy algorithm*, Math. Prog., doi 10.1007/bf01584082.
- Nemhauser, Wolsey & Fisher 1978, Math. Prog., doi 10.1007/bf01588971.
- Feige 1998, *A threshold of ln n for approximating set cover*, JACM, doi 10.1145/285055.285059.
- Arora, Lund, Motwani, Sudan & Szegedy 1998, JACM, doi 10.1145/278298.278306.
- Englert, Röglin & Vöcking 2014, *Worst Case and Probabilistic Analysis of the 2-Opt Algorithm for the TSP*, Algorithmica, doi 10.1007/s00453-013-9801-4.
- Roughgarden (ed.) 2021, *Beyond the Worst-Case Analysis of Algorithms*, CUP, doi 10.1017/9781108637435 [A: arXiv 2007.13241].
- Impagliazzo 1995, *A personal view of average-case complexity*, doi 10.1109/sct.1995.514853.
- Mézard, Parisi & Zecchina 2002, Science, doi 10.1126/science.1073287.
- Monasson et al. 1999, Nature, doi 10.1038/22055.
- Rahman & Virág 2017, *Local algorithms for independent sets are half-optimal*, AoP, doi 10.1214/16-aop1094.
- Kuhn, Moscibroda & Wattenhofer 2016, *Local Computation: Lower and Upper Bounds*, JACM, arXiv 1011.5470 [A].
- Luby 1986, SICOMP, doi 10.1137/0215074.
- Luby & Nisan 1993, STOC, doi 10.1145/167088.167211.
- Chou, Golovnev, Sudan & Velusamy 2024, *Sketching Approximability of All Finite CSPs*, JACM, doi 10.1145/3649435 [A: arXiv 2105.01161].
- Kapralov, Khanna & Sudan 2015, SODA, doi 10.1137/1.9781611973730.84.
- Gomes, Selman, Crato & Kautz 2000, JAR, doi 10.1023/a:1006314320276.
- Gomes & Selman 2001, *Algorithm portfolios*, AIJ, doi 10.1016/s0004-3702(00)00081-3.
- Kerschke, Hoos, Neumann & Trautmann 2019, Evol. Comput., doi 10.1162/evco_a_00242.
- Bengio, Lodi & Prouvost 2021, EJOR, doi 10.1016/j.ejor.2020.07.063.
- Cappart et al. 2021/2023, arXiv 2102.09544.
- Dai, Khalil et al. 2017, arXiv 1704.01665.
- Kool, van Hoof & Welling 2019, arXiv 1803.08475.
- Gasse et al. 2019, arXiv 1906.01629.
- Dudzik & Veličković 2022, arXiv 2203.15544.
- Angelini & Ricci-Tersenghi 2023, *Modern GNNs do worse than classical greedy algorithms … MIS*, Nat. Mach. Intell., doi 10.1038/s42256-022-00589-y.
- Boettcher 2023, *Inability of a GNN heuristic to outperform greedy algorithms …*, Nat. Mach. Intell., doi 10.1038/s42256-022-00587-0.
- Novikov et al. 2025, *AlphaEvolve*, arXiv 2506.13131.
- Liu et al. 2024, *A Systematic Survey on LLMs for Algorithm Design*, arXiv 2410.14716.
- Hart, Nilsson & Raphael 1968, doi 10.1109/tssc.1968.300136.
- Bonet & Geffner 2001, *Planning as heuristic search*, AIJ, doi 10.1016/s0004-3702(01)00108-4.
- Prieditis 1993, *Machine discovery of effective admissible heuristics*, Machine Learning, doi 10.1023/a:1022875501978 [S].
- Newell & Simon, *Computer Science as Empirical Inquiry: Symbols and Search* (Turing lecture; reprint doi 10.1145/1283920.1283930).
- Gigerenzer & Brighton 2009, *Homo Heuristicus*, topiCS, doi 10.1111/j.1756-8765.2008.01006.x.
- Tversky & Kahneman 1974 (reprint doi 10.1017/cbo9780511809477.002).
- Lieder & Griffiths 2017, *Strategy selection as rational metareasoning*, Psych. Rev., doi 10.1037/rev0000075.
- Romanycia & Pelletier 1985, *What is a heuristic?*, Comput. Intell., doi 10.1111/j.1467-8640.1985.tb00058.x.
- Hromkovič, *Algorithmics for Hard Problems* (Springer EATCS; "Heuristics" chapter doi 10.1007/978-3-662-05269-3_6).
- Sörensen, *Metaheuristics—the metaphor exposed*, ITOR, doi 10.1111/itor.12001.
- Schöning 1999, FOCS, doi 10.1109/sffcs.1999.814612.
- Paturi, Pudlák & Zane 1997, *Satisfiability Coding Lemma*, FOCS, doi 10.1109/sfcs.1997.646146.
- van Rooij, Wright & Wareham 2012, Synthese, doi 10.1007/s11229-010-9847-7.

---

## Suggested changes to DESIGN.md

### §3 O3: definitions

1. **Adopt the Bogdanov–Trevisan definitions** next to the current one:
   - a heuristic has error δ_h(D) on our item distribution D;
   - an *errorless* heuristic abstains (⊥) instead of erring.

   Then state that §5.5's "declared impossible" category is modelled as ⊥, and that every heuristic's δ is reported *per distribution* (NFL).
2. **Replace the binary C/S expressibility class with a depth class d_h(n) ∈ {C, L, S}**, defined against the size parameter n of the sweep:
   - **C:** O(1) rounds;
   - **L:** polylog rounds;
   - **S:** inherently sequential.

   Add an **"Evidence"** column citing the result behind each label (P-completeness entry, local-algorithm correspondence, or "by analogy").

### §3 O3: zoo table edits

3. **Add a "Family" column** with values A–I from the taxonomy above, and parametrise families:
   - `PRIORITY(order, score, rule)` covers `GREEDY`, `FIRST-FIT`, `RANDOM-ORDER-FIRST-FIT`, `DSATUR`, `LARGEST-FIRST`, `RATIO`, `VALUE`, `LARGEST-FIT`, `NN-*` and `INPUT-ORDER`.
   - `RESTRICT(selector)` covers `FIRST` and `MATCH` (and `MM`/`ETR` as model-set restrictions).
   - `SCORE(statistic)` covers `POLARITY`, `MOMS`, `PURE-LITERAL` and `FREQ`. Note that `FREQ` in entailment and `POLARITY` in SAT are the same family, which is useful for H4's cross-domain test.
   - `LOCAL-SEARCH(nbhd, noise, k)` covers `WALK-k` and `2OPT-k`.
   - `SEARCH(b, branching, default)` covers `DPLL-b`. `UP+GUESS` is its b = 0 member when the default fill matches, so merge or explicitly tie them.
4. **Reclassify, with citations:**

   | Entry | New label | Basis |
   |---|---|---|
   | `FIRST-FIT` | S | LF Δ+1 colouring is P-complete (compendium A.2.6) |
   | `NN-from-0` | S | NN-TSP heuristic is P-complete (A.2.12) |
   | `UP-k` | C for constant k | Unbounded UP and Horn are P-complete (A.6.1–2), so fixpoint UP is S |
   | `RANDOM-ORDER-FIRST-FIT` | L (provisional) | By analogy with random-order greedy MIS (Blelloch et al. 2012) |
   | `POLARITY`, `MOMS`, `PURE-LITERAL` | C (one shot) | TC⁰ because they count; *iterated* pure-literal elimination is S |
   | `ETR`, `MM` | "S in #premises, C at fixed size" | Depth equals the number of sequential updates |
   | `RATIO` | Split into `RATIO-PREFIX` (C, if sorting ∈ TC⁰) and `RATIO-SKIP` (S) | Superincreasing knapsack is P-complete |
5. **Annotate each entry's "How it errs" with three fields:**
   - soundness: sound / unsound;
   - feasibility: always-feasible / may be infeasible, and *which constraint type* it violates;
   - decision bias: toward YES / NO / two-sided.

   Add a **random-instance threshold** where theory gives one (UC about 8/3, myopic 3.26, colouring about 2χ), and otherwise "simulate".
6. **Add missing members:**
   - **E-class (new, C):** `BP-t` and `WP-t`, i.e. t rounds then threshold the marginals, for SAT, coloring and entailment-as-SAT. `LOCAL-t` coloring. Decimating versions `BP-DEC` and `SP-DEC` are S.
   - **H-class:** `RANDOM` (uniform assignment or answer; the 7/8 diagnostic) and `SAMPLE-m` (entailment: sample m models of the premises and conclude C if it holds in all of them; commission on items with rare counter-models).
   - **B1 relaxations (sound / omission):**
     - `PREMISE-SUBSET(sel)` and `RES-w` (generalising `UP-k`) for entailment;
     - `2SAT-CORE` for SAT;
     - `MST-TOUR` / assignment-based tours for TSP.
   - **B4 restrictions (commission):** `CLOSED-WORLD` and `BICONDITIONAL`.
   - **C2 myopic SAT rules:** `UC`, `GUC`, `SC` (shortest-clause), whose thresholds are analysed.
   - **Width-2 pBT:** `RATIO+BEST-SINGLE` (the knapsack 1/2-approximation).
   - **C4 online:** `ONLINE-STATE(k)`, premise-at-a-time update with bounded state. ETR is one instance; this makes order-reversal predictions explicit.
7. **Split `HALLUC-CONSTRAINT`** into:
   - *systematic* relaxations or restrictions, with a selector rule (drop late or long-range edges; add an edge between co-mentioned nodes), which are heuristics in families B1 and B4;
   - *random* perception noise, which is a nuisance model.

   Similarly, mark `TEXTBOOK-TRANSFER` as A3 (problem substitution, after Kahneman & Frederick).

### §3 O3: identification method additions

8. **Threshold-knee signature.** For random 3-SAT and coloring, simulate each zoo heuristic's success-vs-density curve on our own generator. Compare the knee of the model's error-vs-density curve with each curve, centred on the budget line n\*.
9. **Depth-stress items (tests C vs S directly).** The P-completeness reductions (NAND-CVP gadgets for NN-TSP, LF colouring and unit resolution) build instances where reproducing the heuristic's output requires evaluating a circuit of chosen depth. Prediction: in direct-answer mode, agreement with an S heuristic falls with gadget depth; with CoT, it recovers as tokens scale. This is the cleanest available test of the C/S labels.
10. **Violation-profile likelihood.** For infeasible answers, model *which* constraints are violated. This distinguishes relaxation members (a systematic violation class) from `NOISY-EXACT` (uniform) and from local search (few, scattered violations).
11. **Feature-dependent mixture weights.** Generalise π_h to π_h(φ(x)) = softmax(w_h·φ(x)). This is Rice's algorithm-selection model and Lieder–Griffiths strategy selection, and it tests H4 directly.
12. **Environment manipulations** (ecological rationality). Vary D, e.g. planted polarity bias, or noncompensatory clause structure, so that the bounded-optimal heuristic changes. Then test whether mixture weights track it.

### §3 O6

13. **Program spaces from paradigm models.** Give each zoo member a RASP-L *template*: a scoring sub-program (usually C) plus a control structure, which is one of:
    - none (C0);
    - a t-round local loop (E);
    - a priority loop (C1/C2);
    - a branching loop (D);
    - a flip loop (F).

    Pre-register the rival complexity measures that come with lower-bound theory: pBT width, LOCAL rounds, polynomial degree, alongside sensitivity, min-degree and depth.
14. **Add a depth constraint to the MDL objective:** P\* = argmin |P| + λ·err(P) subject to depth(P) ≤ d. Here d is the number of layers in direct-answer mode and grows with CoT length. Justify it as bounded optimality (Russell & Subramanian; Lieder & Griffiths), not as Occam alone. Then prediction 3 (thinking budget moves weight from C to S) becomes a consequence of relaxing d.
15. **Add a prediction (H7).** In direct-answer mode, no heuristic whose output is P-complete (`FIRST-FIT`, `NN-from-0`, `UP` to fixpoint, `RATIO-SKIP`) is matched above chance on depth-stress items at large n. With CoT, the match appears once tokens ≳ the heuristic's sequential depth. A falsifier would be strong direct-answer agreement on deep gadgets, which would mean the labels or our understanding of the model are wrong.
16. **Generate frontier candidates by constrained program search.** Use FunSearch or EoH restricted to C or S templates on our item distribution to populate the empirical length–error(–depth) Pareto frontier. Note the caveats: LLM search tends to refine scoring functions within greedy templates (Quan et al. 2025), and its results generalise poorly (Sim et al. 2025).
17. **Add these references to §10:** Pearl 1983; Alekhnovich et al. 2011; Borodin, Nielsen & Rackoff 2003; Sato et al. 2019; Greenlaw, Hoover & Ruzzo 1991/1995; Blelloch et al. 2012; Bresler & Huang 2021; Gamarnik, Jagannath & Wein 2020; Bogdanov & Trevisan 2006; Russell & Subramanian 1995; Lieder & Griffiths 2020; Şimşek 2013.

---

## Unverified / leads

These were recalled but not found or read this session. Don't cite them until they are checked.

- **Chvátal & Szemerédi (1988)**, *Many hard examples for resolution*: exponential resolution lower bounds for random k-SAT. Relevant to D-class truncation on UNSAT items.
- **Ben-Sasson & Wigderson (2001)**, *Short proofs are narrow*: the width–size relation; would ground `RES-w`.
- **Sorting is in TC⁰** (Chandra, Stockmeyer & Vishkin 1984). Needed for the C label of `RATIO-PREFIX` and of sort-based TSP rules.
- **Majority / counting is not in AC⁰** (Furst, Saxe & Sipser; Håstad 1986), and **approximate counting is in AC⁰** (Ajtai). These matter for whether counting heuristics (`FREQ`, `DENSITY`, `POLARITY`) fit DESIGN O2's constant-precision AC⁰ case.
- **Exact thresholds for k = 3:** GUC/SC about 3.003 (Frieze & Suen 1996); 3.52 (Kaporis, Kirousis & Lalas; Hajiaghayi & Sorkin, the latter seen only in a search snippet); WalkSAT empirically about 4.2.
- **The PPZ algorithm** (random variable order; set forced literals, else random): success probability about 2^{−(1−1/k)n}. It would make `UP+GUESS` with random order a named, analysed member. Schöning's random walk: (4/3)^n for 3-SAT. Only metadata was verified for both.
- **Raghavan & Thompson (1987)**, randomised rounding; **Goemans & Williamson (1995)**, the 0.878 MAX-CUT SDP. Not looked up.
- **Davis & Impagliazzo (2009)**, *Models of greedy algorithms for graph problems*; **Borodin et al.**, priority models with advice and randomised priority algorithms (Angelopoulos & Borodin 2010, seen in Crossref only).
- **Barak & Steurer (2014)** on sum-of-squares as a model of "relaxation-based" algorithms; Grigoriev and Schoenebeck SoS lower bounds for random k-SAT.
- **Online coloring lower bounds:** Lovász, Saks & Trotter 1989; Halldórsson & Szegedy 1994. **Borodin & El-Yaniv 1998** was found only via a review record.
- **Sharpened NFL** (Schumacher, Vose & Whitley 2001): NFL holds iff the function set is closed under permutation.
- **Pólya (1945)** *How to Solve It*; **Newell & Simon (1972)** *Human Problem Solving* (GPS, means-ends analysis); **Simon (1955)** bounded rationality. Not looked up.
- **Kilby, Slaney, Thiébaux & Walsh (2005)**, *Backbones and backdoors in satisfiability* (AAAI). The Crossref query returned unrelated records.
- **Courcelle's theorem**; Downey & Fellows; Cygan et al. (2015) *Parameterized Algorithms*. Not looked up.
- **Mézard & Montanari (2009)**, *Information, Physics, and Computation*; Yedidia, Freeman & Weiss on BP and the Bethe free energy. Not looked up.
- **Platzman & Bartholdi** space-filling-curve TSP. A possible C-class TSP member (sort-based), if sorting ∈ TC⁰.
- **Whether MST is in NC.** Needed for the depth label of `MST-TOUR`.
- **The Hoos & Stützle formal definition of SLS** and the Blum & Roli classification dimensions (trajectory vs population, memory, and so on). The Blum & Roli PDF returned 404; only the abstract-level "I&D frame" was confirmed.
- **The Gigerenzer & Brighton (2009) bias–variance argument.** The abstract could not be fetched (403 and a cookie wall).
- **arXiv 2605.29649** (June 2026): an LLM-evolved heuristic reportedly rediscovered First-Fit's core logic. Seen only as a search snippet.
- **Lead worth following:** a RASP-L or transformer construction showing that k rounds of unit propagation or BP over a clause–variable incidence fit in O(k) layers. That would turn the Sato et al. GNN result into a transformer result for our encoding.
