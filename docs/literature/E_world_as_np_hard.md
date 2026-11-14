> Research-agent report written 2026-11-13 for the literature review in [../LITERATURE.md](../LITERATURE.md). Every source was found by web search or fetch during the review, and the report tags how each was checked. Treat details as leads to confirm before citing.

# E. The world as NP-hard: frameworks, catalogue and counterarguments (feeds O1)

*Literature review part E for "Heuristics Under Hardness" (DESIGN.md §3, O1). Compiled 2026-11-13.*

**Method note.** Sources were found and checked in this session with WebSearch (until the shared session budget ran out partway through), then with known-record lookups: Crossref and Semantic Scholar by DOI, the arXiv API, Europe PMC, and direct PDF reads. Every citation below was found in this session. When a complexity claim comes from an abstract, a TLDR or another paper's description, rather than from the full text, the row is marked **(abs)** or **(2°)**. Works that were recalled but not checked are listed under *Unverified / leads*.

**Read closely** (full text or the relevant sections): van Rooij 2015 (CogSci); van Rooij, Evans, Müller, Gedge & Wareham 2008 (analogy, parameterized analysis); Kwisthout, Wareham & van Rooij 2011 (Bayesian approximation); Roughgarden 2019 (CACM); Lieder & Griffiths 2020 (BBS target article, response and commentaries); Duchnowski, Pavlick & Koller 2025 (EHOP intro and dataset); Williams, Gomes & Selman 2003 (abstract and intro); Bogdanov & Trevisan 2006 (ch. 1 and ch. 5); Aaronson 2011 (§§2, 3.1, 5, 11).

---

## Summary

- **The strongest form of O1 is a generality argument, not a list.** The cognitive-science literature finds NP-hard computational-level theories across "perception, language, reasoning, categorisation, decision making, and motor planning". It reads this ubiquity as "a natural consequence of attempting to scale one's computational-level models to general domains" (van Rooij 2015). Two other fields say the same: "Most interesting AI formalisms for reasoning, planning, and learning have been shown to be worst-case intractable" (Williams, Gomes & Selman 2003), and "optimization problems are more likely to be NP-hard than not" (Roughgarden 2019). An LLM sold as a general-purpose reasoner and agent is the limiting case of domain generality.
- **Logical deduction is the *least* hard of the reasoning modes, so lean on the others.** Entailment is coNP-complete (Cook 1971). Abduction is "harder than deduction" (Eiter & Gottlob 1995). Belief-network inference is NP-hard, and so is approximating it (Cooper 1990; Dagum & Luby 1993). Finding a most probable explanation is NP-hard, and so is approximating it (Kwisthout et al. 2011). STRIPS planning is PSPACE-complete (Bylander 1994). Equilibria are PPAD-complete (Daskalakis et al.; Chen, Deng & Teng). Andrew's "logical reasoning is obviously one way" is right, but it is the weakest example to lead with.
- **Satisficing doesn't escape.** For many everyday tasks even *feasibility* is NP-complete: timetabling (Even, Itai & Shamir 1976), configuration (SAT), Minesweeper consistency (Kaye 2000), Latin-square completion (Colbourn 1984). Many approximations are NP-hard too: Bayesian inference, MPE, Tetris. "Just find a good-enough answer" doesn't remove the hardness.
- **There is direct human evidence that instance-level computational hardness predicts error.** Human accuracy on knapsack instances falls with their computer-science complexity (Murawski & Bossaerts 2016). Task-independent hardness metrics predict both time and accuracy across three cognitive tasks (Franco et al. 2022). Most models of decision-making "are intractable from a computational perspective" (Bossaerts & Murawski 2017). This is the human analogue of our O1 + O3 link.
- **Bounded rationality supplies the "heuristics as response" vocabulary,** from Simon 1955, through Gigerenzer's adaptive toolbox and Russell & Subramanian's bounded optimality, to Lieder & Griffiths' resource-rational analysis. Lieder & Griffiths explicitly motivate it with intractability (citing van Rooij 2008 and Bossaerts & Murawski 2017). The van Rooij group's counter is that *choosing or adapting* heuristics is itself intractable, which only relocates the problem to the evolutionary or training level (Rich et al. 2019, 2020; Otworowska et al. 2018). That maps neatly onto our O6: training is the adaptation process.
- **Parameterized complexity is the best tool for saying *which* aspect of a real task is hard,** and it gives us hardness dials. Structure mapping is fixed-parameter tractable in the number of objects but not in arity, height or flatness (van Rooij et al. 2008). MPE becomes tractable at bounded treewidth (Kwisthout et al. 2011).
- **The strongest counterargument is distributional: real instances often have structure that makes them easy.** Examples are backdoors (Williams et al. 2003), community structure (Ansótegui et al. 2019), "clustering is difficult only when it does not matter" (Daniely, Linial & Saks 2012), perturbation stability and smoothed analysis (Roughgarden; Spielman & Teng). Best reply, in three parts:
  1. Structure is *not sufficient* in theory (Mull, Fremont & Seshia 2016).
  2. Solvers that exploit structure take millions of steps, far beyond an LLM's token budget.
  3. O1 should therefore be stated as *budget-relative* distributional hardness, which we measure.
- **Recent LLM work (2023–2026) already asserts the premise.** EHOP opens "Many real world tasks that people face in their personal and professional lives are NP hard optimization problems". The premise is also behind NPHardEval, NPPC, NATURAL PLAN, TravelPlanner and LLMFP. Sikka & Sikka (2025) and van Rooij et al. (2024) make complexity arguments about LLM agents and AI-by-learning. None of these papers *defends* O1 carefully, which leaves room for our page.
- **Top suggested edit:** restate O1 as a three-layer claim (worst-case cores → generality → measured, budget-relative tail), give every row of the O1 table a citation, and add rows from law, medicine, economics and perception.

---

## Frameworks for O1

### F1. Computational-level intractability analysis (the Tractable Cognition thesis)

**What the sources claim.**

- *The Tractable Cognition thesis.* "Human cognitive capacities are constrained by computational tractability." Formalised as P-Cognition, it may be "overly restrictive", so van Rooij proposes the FPT-Cognition thesis instead (van Rooij 2008, abstract).
- *Marr's levels.* A computational-level theory is a function T: I → O. If T is NP-hard, every algorithm needs super-polynomial time on infinitely many inputs (assuming P ≠ NP). van Rooij's illustration: a 2ⁿ algorithm doing 1000 steps per second takes 12 days at n = 30 and 35 millennia at n = 50 (van Rooij 2015, building on Marr 1982).
- *Ubiquity.* "Many computational-level theories in cognitive science are NP-hard", across perception, language, reasoning, categorisation, decision-making and motor planning. This is "a natural consequence of attempting to scale one's computational-level models to general domains" (van Rooij 2015).
- *Overgeneralisation.* An NP-hard theory T′ may be an *overgeneralisation* of the true capacity. The accurate theory may be a tractable but still fairly general restriction of it (van Rooij 2015).
- *The textbook.* *Cognition and Intractability* (van Rooij, Blokpoel, Kwisthout & Wareham 2019) covers classical and parameterized analysis for cognitive scientists, with a compendium of complexity results (Appendix C).

**Key citations.** van Rooij 2008; van Rooij 2015; van Rooij et al. 2019; Kwisthout et al. 2011; van Rooij, Wright & Wareham 2012; Marr 1982 (as used by van Rooij 2015).

**How we'd use it (interpretation).** This is the spine of O1. Treat "what an LLM is asked to do" in a domain as a computational-level function. Then argue:

1. The functions people want general-purpose reasoners and agents to compute (entailment, explanation, planning, scheduling, configuration) are NP-hard or worse when stated in full generality.
2. A model with a token budget therefore cannot compute them exactly on all inputs. That is O2.
3. So the scientific question is *which tractable function it computes instead*. That is O3.

The overgeneralisation idea is the honest caveat. The "real" task may be a tractable restriction. Parameterized complexity (F4) is how we test that.

### F2. Reduction-based catalogues: real tasks contain NP-hard cores

**What the sources claim.**

- *The canonical machinery and catalogue.* Cook (1971) and Karp (1972) supply the reductions; Garey & Johnson (1979) the catalogue.
- *Domain results*, of which the catalogue below lists about 40, including:
  - "all the common timetable problems are NP-complete" (Even, Itai & Shamir 1976);
  - NP-completeness "for a large number of" machine scheduling problems (Lenstra, Rinnooy Kan & Brucker 1977);
  - HP protein folding is NP-complete (Berger & Leighton 1998);
  - two-player Nash equilibrium is PPAD-complete (Chen, Deng & Teng 2009);
  - partial and full regulatory compliance are NP-complete and coNP-complete (Colombo Tosatto, Governatori & Kelsen 2015).
- *Breadth.* Aaronson (2011, §3.1) lists Sudoku, jigsaw puzzles, TSP and SAT. He says NP-complete problems from physics, biology and industrial optimisation are "identical from the standpoint of polynomial-time computation".
- *Physical processes.* Aaronson (2005) argues that no physical process (soap bubbles, protein folding, quantum computing and so on) is likely to solve NP-complete problems efficiently.

**Key citations.** Cook 1971; Karp 1972; Garey & Johnson 1979; the catalogue rows below; Aaronson 2005 and 2011; Kendall, Parkes & Spoerer 2008 (puzzle survey).

**How we'd use it.** This is the catalogue table in the paper. Two framing points matter:

- **Mark feasibility versus optimisation versus approximation per row.** That pre-empts the "people only satisfice" objection: for timetabling, configuration and Minesweeper the *feasibility* question is already NP-complete.
- **Use the Aaronson (2005) point against "nature solves it, so it's easy".** Proteins fold quickly even though HP folding is NP-complete. The resolution is that the instances nature presents are not worst-case. That leads straight into F5.

### F3. Bounded rationality, bounded optimality and resource-rational analysis

**What the sources claim.**

- **Simon (1955)** set up the behavioural model of rational choice under limited capacity, including satisficing. Lieder & Griffiths quote him: "we must be prepared to accept the possibility that what we call 'the environment' may lie, in part, within the skin of the biological organism".
- **Gigerenzer & Goldstein (1996)** and **Gigerenzer & Gaissmaier (2011)**: heuristics are "efficient cognitive processes … that ignore part of the information". How well they work in an uncertain world "is an empirical rather than an a priori issue".
- **Russell & Subramanian (1995)**: perfect rationality "imposes fundamentally unsatisfiable requirements". An agent is *bounded-optimal* if its program solves the constrained optimisation problem set by its architecture and task environment.
- **Lieder & Griffiths (2020)**, BBS target article:
  - "computing exact solutions to the problems people purportedly solve is often computationally intractable (Van Rooij 2008)";
  - "approximations are necessary because the computational complexity of decision-making in the real world far exceeds cognitive capacity (Bossaerts & Murawski 2017)", and people cope "through efficient heuristics and habits".
  - In their response they concede that ideal resource rationality "would require optimal meta-decision-making which is even more computationally intractable than optimal decision-making itself".
- **Gershman, Horvitz & Tenenbaum (2015)**: "computational rationality" is a convergent paradigm across AI, cognitive science and neuroscience. **Griffiths, Lieder & Goodman (2015)**: levels of analysis between computational and algorithmic.
- **Bossaerts & Murawski (2017)**: "the rationality principle … does not take into account the difficulty of finding the best option". They propose computational complexity theory to quantify decision difficulty, and say "most models of decision-making, and metacognition, are intractable".
- **The van Rooij group's critique:**
  - The adaptive toolbox "has not yet tamed the intractability demon", which hides in the assumption that ecological rationality comes from adaptation (Otworowska et al. 2018).
  - Adaptation that guarantees even minimal rationality "requires astronomical computational resources" (Rich et al. 2019).
  - For resource-rationality, the adaptive toolbox and massive modularity alike, the challenge is "only relocated from the cognitive level to the evolutionary level" (Rich et al. 2020).

**How we'd use it (interpretation).**

- **Vocabulary and pedigree.** "Heuristics are the bounded-optimal response to intractability" is a 70-year-old claim about humans. We test it for LLMs, where the procedure is actually inspectable (O5).
- **A cross-species analogue.** The human evidence (Murawski & Bossaerts 2016; Franco et al. 2022) gives O1 a human counterpart, and suggests borrowing their instance-hardness metrics.
- **A bridge to O6.** The Rich et al. relocation argument maps onto training: SGD on pretraining data is the "adaptation process". Their result predicts that training can't guarantee selecting the *best* heuristic. Our two-part-MDL hypothesis (H2) is a claim about *which* heuristic it selects anyway. Worth one sentence in the paper; it turns a critique into a prediction.

### F4. Parameterized complexity: which aspect of a real task makes it hard

**What the sources claim.**

- **The method.** A problem is fixed-parameter tractable for parameter set K if it is solvable in f(K)·n^c time. A *source of complexity* is a minimal K for which it is FPT (van Rooij et al. 2008, Definitions 1–3).
- **Analogy (structure-mapping theory):**
  - fp-intractable for {height, arity, predicate-label frequency, non-root predicates};
  - fp-intractable for flatness;
  - **fp-tractable for the number of objects o**.

  So the arity bound "assumed by Halford et al. (1998) is insufficient to yield analogical mappings computationally tractable" (van Rooij et al. 2008).
- **Bayesian MPE.** Tractable when the network has bounded treewidth: "tractability is achieved not by giving up on the 'exactness' … but by explicating that the modeled process operate on restricted domains" (Kwisthout et al. 2011).
- **Surveys.** van Rooij & Wareham (2008) review applications across perception, action and higher cognition. van Rooij 2008 argues for FPT-Cognition as the tractability criterion.

**How we'd use it.**

- **Methodology for "how to frame a real problem formally".** Write the computational-level function, list candidate parameters (variables, clause density, treewidth, number of objects, plan length, colours), and find which parameter's growth drives intractability.
- **Hardness dials.** These parameters become the sweep axes of O1 step 2 and the size axis of O2's budget line.
- **A pre-emptive answer to "your items are artificially hard".** We vary the source-of-complexity parameter on purpose and report the curve.

### F5. Beyond worst-case: distributional and budget-relative hardness

**What the sources claim.**

- **Roughgarden (2019):**
  - For LP, clustering, caching and neural-net training, worst-case analysis "does not provide any helpful advice".
  - Clustering objectives are almost all NP-hard, yet Lloyd's algorithm works on real data. Hence "clustering is hard only when it doesn't matter" (Daniely, Linial & Saks 2012).
  - Perturbation-stable instances are polynomial-time solvable. Such assumptions are "justified with a plausible narrative about why 'real-world instances' might satisfy it".
- **Spielman & Teng (2004):** smoothed analysis shows that simplex runs in polynomial time under small Gaussian perturbations.
- **Bogdanov & Trevisan (2006), ch. 5:**
  - "The worst-case NP hardness of computational problems does not always reflect their perceived difficulty in practice."
  - One explanation is that hard instances may be infeasible to *generate*.
  - The right model of "instances that occur" is a polynomial-time *samplable* distribution, (NP, PSamp).
  - The Impagliazzo–Levin completeness theorem links this to the uniform distribution. Easiness on average for samplable distributions is an open question tied to one-way functions.
- **Levin (1986):** average-case completeness.
- **Industrial SAT:**
  - Small backdoors explain solvers' good scaling on practical instances (Williams et al. 2003).
  - Industrial instances have high modularity; random instances lack it (Ansótegui et al. 2019).
  - Community structure "is not sufficient to explain the success of CDCL in practice", and random modular instances have exponentially long resolution proofs (Mull et al. 2016).

**How we'd use it (interpretation).** This is where O1 should end up. The defensible empirical claim isn't "real tasks are NP-hard", which is a property of the problem class. It is:

> For an agent with budget B, a task distribution D is *effectively hard* to the extent that a non-negligible mass of D cannot be answered correctly by any procedure we know that runs within B.

Three things follow:

- **The budget gap answers the industrial-SAT objection.** Industrial instances are easy for CDCL with 10⁶–10⁹ propagations, not for a model with 10³–10⁵ reasoning tokens.
- **The definition is measurable,** and our three hardness axes already measure it: solver, proof and heuristic-relative hardness.
- **The samplable-distribution framing gives a precise "world" model.** The world is a bounded process that generates instances. Whether such worlds are easy on average is an open complexity question, not a settled fact either way.

---

## Catalogue

Legend:

- **(abs)**: claim checked in the abstract or TLDR only.
- **(2°)**: claim as stated by another verified paper.
- **feas / opt / approx**: hardness holds for the feasibility, optimisation or approximation version.

| # | Real-world task | Formal problem | Complexity | Citation | Link |
|---|---|---|---|---|---|
| 1 | School/exam timetabling (teachers × classes × periods) | Gotlieb's timetable problem | NP-complete even in "a very primitive version"; "all the common timetable problems are NP-complete"; polynomial if every teacher is binary (feas) | Even, Itai & Shamir (1976). SIAM J. Comput. 5(4):691–703 | https://doi.org/10.1137/0205048 |
| 2 | Factory / job-shop / machine scheduling | Machine scheduling (single, parallel, flow and job shop) | NP-complete for "a large number" of variants (opt) (abs) | Lenstra, Rinnooy Kan & Brucker (1977). Annals of Discrete Math. 1:343–362 | https://doi.org/10.1016/S0167-5060(08)70743-X |
| 3 | Delivery routes, vehicle and crew routing | Vehicle routing / TSP variants | NP-hard; review of hardness and approximation bounds (opt) (abs) | Lenstra & Rinnooy Kan (1981). Networks 11(2):221–227 | https://doi.org/10.1002/net.3230110211 |
| 4 | Airline crew scheduling | Crew pairing / rostering (set-partitioning style) | NP-hard optimisation (2°: EHOP intro) | Gopalakrishnan & Johnson (2005). Annals of OR 140; cited by Duchnowski et al. 2025 | https://doi.org/10.1007/s10479-005-3975-3 |
| 5 | Birthday parties without exes; student groups without friends; taekwondo warm-up rooms | Graph coloring (min colours) | NP-hard (opt) | Duchnowski, Pavlick & Koller (2025). EHOP. EMNLP 2025 (Findings) | https://arxiv.org/abs/2502.13776 |
| 6 | Sightseeing in limited hours; party decoration budget; lemonade stand | 0-1 knapsack | NP-hard (opt) | Duchnowski, Pavlick & Koller (2025) | https://arxiv.org/abs/2502.13776 |
| 7 | Daily task ordering with switch costs; UN delegates around a table; errands | TSP | NP-hard (opt) | Duchnowski, Pavlick & Koller (2025) | https://arxiv.org/abs/2502.13776 |
| 8 | Organ donation / kidney exchange | Cycle/chain packing with length cap | NP-hard (2°: EHOP intro cites it as an NP-hard real-world task) | Abraham, Blum & Sandholm (2007). ACM EC '07, 295–304 | https://doi.org/10.1145/1250910.1250954 |
| 9 | Medical residency matching with couples | Hospitals/Residents with Couples (HRC) | NP-hard in general (Ronn 1990, as stated in the intro); still NP-hard under strong restrictions (feas) | Csáji, Manlove, McBride & Trimble (2024). IJCAI-24 | https://www.ijcai.org/proceedings/2024/302 |
| 10 | Car/product configuration consistency | Boolean constraint satisfaction (SAT) | NP-complete (SAT); handled in industry by a modified SAT checker (feas) | Sinz, Kaiser & Küchlin (2003). AI EDAM 17(1):75–97; Cook (1971) | https://doi.org/10.1017/S0890060403171065 |
| 11 | "Does this conclusion follow from these premises?" | Propositional entailment (complement of SAT) | coNP-complete | Cook (1971). STOC '71 | https://doi.org/10.1145/800157.805047 |
| 12 | Hardware/software verification against temporal specs | LTL satisfiability / model checking | PSPACE-complete with X, U, S operators; NP-complete for F only (abs) | Sistla & Clarke (1985). J. ACM 32(3):733–749 | https://doi.org/10.1145/3828.3837 |
| 13 | Bounded verification ("can the system reach a bad state in k steps?") | Bounded model checking reduced to SAT | in NP for each bound; solved with SAT procedures | Biere, Cimatti, Clarke & Zhu (1999). *Symbolic Model Checking without BDDs* (tech. report / TACAS) | https://doi.org/10.21236/ADA360973 |
| 14 | Checking a business process against regulations (contracts, compliance) | Compliance with conditional obligations with deadlines | partial compliance NP-complete; full compliance and non-compliance coNP-complete | Colombo Tosatto, Governatori & Kelsen (2015). IEEE Trans. Services Computing 8(6):958–970 | https://publications.uni.lu/handle/10993/19564 |
| 15 | Evaluating a legal or policy argument: is this argument accepted on every coherent reading? | Abstract argumentation: sceptical acceptance / coherence (preferred semantics) | Π₂ᵖ-complete (abs) | Dunne & Bench-Capon (2002). Artificial Intelligence 141 | https://doi.org/10.1016/S0004-3702(02)00261-8 |
| 16 | Medical diagnosis with multiple simultaneous disorders | Abduction: most plausible hypothesis set explaining all data; generalised set cover | NP-hard in general (abs) | Bylander, Allemang, Tanner & Josephson (1991). AIJ 49:25–60; Reggia, Nau & Wang (1983). IJMMS 19 | https://doi.org/10.1016/0004-3702(91)90005-5 · https://doi.org/10.1016/S0020-7373(83)80065-0 |
| 17 | Explaining symptoms from a logical domain theory | Logic-based abduction (propositional) | "abduction is harder than deduction" (above NP for basic minimality criteria) (abs) | Eiter & Gottlob (1995). J. ACM 42(1):3–42 | https://doi.org/10.1145/200836.200838 |
| 18 | Probabilistic diagnosis / prediction with a causal model | Belief-network inference | NP-hard (exact); approximating it is also NP-hard (approx) (abs) | Cooper (1990). AIJ 42:393–405; Dagum & Luby (1993). AIJ 60:141–153 | https://doi.org/10.1016/0004-3702(90)90060-D · https://doi.org/10.1016/0004-3702(93)90036-B |
| 19 | "What is the best explanation?" (perception, theory of mind, language) | Most probable explanation (MPE) | NP-hard; approximating it NP-hard; NP-hard even to find an assignment with probability ≥ q; tractable at bounded treewidth | Kwisthout, Wareham & van Rooij (2011). Cognitive Science 35(5):779–784; Kwisthout (2011). IJAR 52(9) | https://doi.org/10.1111/j.1551-6709.2011.01182.x |
| 20 | Updating beliefs on new information; counterfactuals | Propositional belief revision / update | intractable; complexity results for major operators (exact class not re-read) (abs) | Eiter & Gottlob (1992). AIJ 57:227–270 | https://doi.org/10.1016/0004-3702(92)90018-S |
| 21 | Making analogies (e.g. atom ↔ solar system) | Structure mapping (Gentner's SMT) | NP-hard; FPT in number of objects; fp-intractable in arity, height, flatness | van Rooij, Evans, Müller, Gedge & Wareham (2008). CogSci 2008 (venue: see Unverified) | https://www.fim.uni-passau.de/fileadmin/dokumente/fakultaeten/fim/lehrstuhl/muller/Analogical.pdf |
| 22 | Judging which beliefs/explanations hang together | Coherence maximisation (positive/negative constraint satisfaction ≡ Hopfield harmony maximisation) | intractable (NP-hard) (2°: van Rooij & Wareham) | Thagard & Verbeurgt (1998). Cognitive Science 22(1); van Rooij & Wareham (2012). J. Math. Psych. 56(4) | https://doi.org/10.1207/s15516709cog2201_1 · https://doi.org/10.1016/j.jmp.2012.05.002 |
| 23 | Finding a target in a cluttered scene | Unbounded visual search | computationally intractable (NP-complete) (abs) | Tsotsos (1990). BBS 13(3):423–445 | https://doi.org/10.1017/S0140525X00079577 |
| 24 | Grouping things into categories | Clustering (k-means, k-median, …) | "Almost all natural optimization problems that are defined over clusterings are NP-hard" | Roughgarden (2019). CACM 62(3):88–96 | https://arxiv.org/abs/1806.09817 |
| 25 | Planning a sequence of actions to a goal | Propositional STRIPS plan existence | PSPACE-complete in general; NP-hard or polynomial under restrictions (abs) | Bylander (1994). AIJ 69:165–204 | https://doi.org/10.1016/0004-3702(94)90081-7 |
| 26 | Hierarchical / open-ended planning | Domain-independent planning with operators, function symbols etc. | from decidable to undecidable depending on restrictions (title-level) | Erol, Nau & Subrahmanian (1995). AIJ 76:75–88 | https://doi.org/10.1016/0004-3702(94)00080-K |
| 27 | Blocksworld, multi-agent task allocation (LLM planning benchmarks) | Optimal Blocksworld; task allocation via TSP | NP-hard (2°: as classified by LLMFP; Blocksworld via Gupta & Nau 1992) | Hao, Zhang & Fan (2024). LLMFP. arXiv 2410.12112 | https://arxiv.org/abs/2410.12112 |
| 28 | Learning human-like cognition from data | "AI-by-learning" | intractable (formal proof claimed) (abs) | van Rooij, Guest, Adolfi, de Haan, Kolokolova & Rich (2024). Comput. Brain & Behav. 7:616–636 | https://doi.org/10.1007/s42113-024-00217-5 |
| 29 | Acquiring a good toolbox of heuristics by adaptation or learning | Adaptation for ecological rationality | intractable; "robust property of adaptation" (abs) | Rich, Blokpoel, de Haan, Otworowska, Sweers, Wareham & van Rooij (2019). Synthese 198:5749–5784 | https://doi.org/10.1007/s11229-019-02431-2 |
| 30 | Deciding what changes after an action (relevance) | Frame problem (no single formal class) | "starts to look computationally intractable" if all beliefs are checked | Shanahan (2016 rev.). *The Frame Problem*. SEP | https://plato.stanford.edu/entries/frame-problem/ |
| 31 | Everyday choice under a budget (lab task) | 0-1 knapsack | NP-hard; human accuracy falls with instance complexity | Murawski & Bossaerts (2016). Scientific Reports 6:34851 | https://doi.org/10.1038/srep34851 |
| 32 | Strategic interaction (bargaining, markets, games) | Nash equilibrium of a two-player game | PPAD-complete (zero-sum is in P via LP) | Chen, Deng & Teng (2009). J. ACM 56(3); Daskalakis, Goldberg & Papadimitriou (2009). SIAM J. Comput. 39(1); Aaronson (2011) §11.2 | https://doi.org/10.1145/1516512.1516516 · https://doi.org/10.1137/070699652 |
| 33 | Spectrum / procurement auctions with bundle bids | Combinatorial-auction winner determination | intractable in general; tractable for some bid structures (abs) | Rothkopf, Pekeč & Harstad (1998). Management Science 44(8); Sandholm (2002). AIJ 135 | https://doi.org/10.1287/mnsc.44.8.1131 · https://doi.org/10.1016/S0004-3702(01)00159-X |
| 34 | Running an election under a fair rule | Winner determination for Dodgson's (Lewis Carroll's) rule | computationally prohibitive; "impracticality theorems" for fair voting schemes (abs) | Bartholdi, Tovey & Trick (1989). Social Choice and Welfare 6(2):157–165 | https://doi.org/10.1007/BF00303169 |
| 35 | Trading on past prices | Market efficiency (weak form) | markets are efficient iff P = NP | Maymin (2011). Algorithmic Finance 1(1):1–11 | https://doi.org/10.3233/AF-2011-007 |
| 36 | Pricing / auditing bundled derivatives (CDOs) | Detecting tampered ("lemon") bundles | computationally hard; derivatives can *amplify* information asymmetry (specific assumption: see Unverified) (abs) | Arora, Barak, Brunnermeier & Ge (2011). CACM 54(5):101–107 | https://doi.org/10.1145/1941487.1941511 |
| 37 | Protein structure prediction | HP-model folding (3D) | NP-complete (title) | Berger & Leighton (1998). J. Comput. Biol. 5(1):27–40; Crescenzi et al. (1998). J. Comput. Biol. 5(3) | https://doi.org/10.1089/cmb.1998.5.27 · https://doi.org/10.1089/cmb.1998.5.423 |
| 38 | Minesweeper | Minesweeper consistency | NP-complete (feas) | Kaye (2000). Mathematical Intelligencer 22(2) | https://doi.org/10.1007/BF03025367 |
| 39 | Sudoku-type puzzles | Partial Latin-square completion | NP-complete (feas) (abs) | Colbourn (1984). Discrete Applied Math. 8(1):25–30; Kendall, Parkes & Spoerer (2008) survey, ICGA J. 31(1) | https://doi.org/10.1016/0166-218X(84)90075-1 · https://doi.org/10.3233/ICG-2008-31103 |
| 40 | Tetris (offline, known piece sequence) | Maximise cleared rows / survival | NP-hard, even to approximate (approx) (title) | Demaine, Hohenberger & Liben-Nowell (2003). COCOON; journal version Breukelaar et al. (2004) IJCGA 14 | https://doi.org/10.1007/3-540-45071-8_36 |
| 41 | Classic video games (Mario, Zelda, Metroid, Pokémon) | Level reachability | "computationally hard" (title; per-game classes not re-read) | Aloupis, Demaine, Guo & Viglietta (2015). Theor. Comput. Sci. 586:135–160 | https://doi.org/10.1016/j.tcs.2015.02.037 |
| 42 | Travel, meeting and calendar planning by LLM agents | Multi-constraint scheduling/planning (our reading: CSP-like) | benchmarks report low solve rates; neither paper claims a complexity class, the class is our interpretation | Zheng et al. (2024). NATURAL PLAN, arXiv 2406.04520; Xie et al. (2024). TravelPlanner, ICML 2024, arXiv 2402.01622 | https://arxiv.org/abs/2406.04520 · https://arxiv.org/abs/2402.01622 |

Rows 1–10, 14, 15 and 32–36 are the most "real-world" and the least obviously reasoning tasks. Rows 11 and 16–30 are the cognitive capacities. Rows 37–41 are puzzles and games, with easy-to-check answers. Rows 5–7, 27 and 42 are already LLM benchmarks.

---

## Counterarguments and replies

**C1. "NP-hardness is worst case; real instances are easy."** This is the strongest objection.

*Sources for:*
- backdoors explain why solvers handle million-variable practical instances (Williams et al. 2003);
- industrial SAT has high modularity (Ansótegui et al. 2019);
- "clustering is difficult only when it does not matter" (Daniely et al. 2012);
- perturbation stability and smoothed analysis (Roughgarden 2019; Spielman & Teng 2004);
- worst-case hardness "does not always reflect … difficulty in practice" (Bogdanov & Trevisan 2006).

*Replies:*
1. **Structure isn't sufficient.** Community structure is not enough to explain CDCL's success, and random modular instances still need exponential resolution proofs (Mull et al. 2016).
2. **"Easy" means easy for CDCL with enormous step counts.** The relevant comparison for an LLM is its token budget. O2 already makes the budget line the unit.
3. **State O1 distributionally and measure it.** Our three hardness axes report the hard *tail* of realistic distributions. The design already notes that most real graph and proof instances fall within reasoning models' range, with a long tail outside (Rameshkumar et al. 2025).
4. **Whether natural samplable distributions are easy on average is an open problem** tied to cryptography (Bogdanov & Trevisan ch. 5). Neither side can assume it.

**C2. "People and agents satisfice; they don't need optimal answers."** (Simon 1955; Gigerenzer & Gaissmaier 2011.)

*Reply:*
- For many rows *feasibility* is already NP-complete: timetabling, configuration, Minesweeper, Latin squares, HRC.
- Approximation is often NP-hard too: belief-network inference, MPE, Tetris. "Approximation by itself cannot guarantee tractability" (Kwisthout et al. 2011).
- In our design, satisficing heuristics are exactly the objects of study. The objection becomes the research question.

**C3. "Heuristics don't escape intractability; invoking them is explanatorily dysfunctional."** (van Rooij, Wright & Wareham 2012.)

*Reply* (refines the existing DESIGN text): we do not claim that heuristic h computes the intractable f. We claim that the model computes some tractable h ≠ f, and we *identify which h* from the instances where h and f disagree. That is the computational-level theory revision they recommend. We report the unexplained mass rather than assuming h explains everything.

**C4. "The intractable formalisation is an overgeneralisation; the real task is a tractable restriction."** (van Rooij 2015.)

*Reply:* agreed in principle, and parameterized analysis tells us which restriction (F4). Our sweeps vary the source-of-complexity parameter, so we report *where along that parameter* models switch from exact to heuristic behaviour. If real use sits in the tractable region, that is a finding too.

**C5. "Choosing heuristics is itself intractable; you've only relocated the problem."** (Otworowska et al. 2018; Rich et al. 2019, 2020; Lieder & Griffiths' own concession about meta-decision-making.)

*Reply:* for LLMs the relocation is real and is the point of O6. Training is the adaptation process. It spends enormous compute and still isn't guaranteed to find the best heuristic. H2 predicts *which* one it lands on, the two-part-MDL optimum among short programs. Zhou et al. themselves say minimum RASP-L length is likely intractable to compute (see report D).

**C6. "LLMs can call a solver; hardness is irrelevant with tools."**

*Reply:*
- The NPPC authors report that tool-augmented LLMs still cannot fully solve NP-complete problems in general: tools speed up subroutines but don't change the exponential worst case (from their abstract and summary; not read in full).
- The bottleneck moves to *formalisation*. EHOP's ILP-Python condition degrades slowest with size, but it still depends on translating costumed problems correctly. LLMFP makes formalisation the whole method.
- Tool-free behaviour is what governs the formalisation step, self-verification, and cases where no solver applies. We disable tools to see the procedure (DESIGN O2 rules).

**C7. "At realistic sizes, exponential doesn't bite."** (Aaronson 2011 §2 and §5.2: constants can matter, but asymptotics have "explanatory force until proven otherwise".)

*Reply:* van Rooij 2015's numbers show 2ⁿ blowing up between n = 30 and n = 50. For an LLM the budget is tokens, and O2's n\* makes this concrete per model. EHOP and NPHardEval already see degradation at small sizes.

**C8. "Most LLM use isn't combinatorial."**

*Reply:* O1 doesn't need *most* tasks to be NP-hard. It needs (a) a substantial class of deployed tasks with NP-hard cores, and (b) the core of reasoning itself to be among them. For (a): agentic planning, scheduling, configuration, compliance, diagnosis (TravelPlanner, NATURAL PLAN, EHOP). For (b): entailment, abduction, belief revision, explanation.

---

## Key sources

| Citation | Link | Claim (as the source states it) | How we'd use it |
|---|---|---|---|
| **van Rooij (2008).** *The Tractable Cognition Thesis.* Cognitive Science 32(6):939–984 | https://doi.org/10.1080/03640210801897856 | Cognitive capacities are constrained by tractability. P-Cognition may be overly restrictive; argues for FPT-Cognition | F1/F4 anchor; the "tractability as theory constraint" premise |
| **van Rooij (2015).** *How the curse of intractability can be cognitive science's blessing.* Proc. CogSci 37 (read closely) | https://escholarship.org/uc/item/8v6066wt | NP-hard theories are ubiquitous across perception, language, reasoning, categorisation, decisions and motor planning. That is "a natural consequence" of domain generality. Intractable theories may be overgeneralisations | The generality argument for O1 (quote it); the C4 caveat |
| **van Rooij, Blokpoel, Kwisthout & Wareham (2019).** *Cognition and Intractability.* Cambridge UP | https://doi.org/10.1017/9781107358331 | Textbook on classical and parameterized complexity for cognition; compendium of results (App. C) | Methods reference; source of further catalogue rows |
| **van Rooij, Wright & Wareham (2012).** Synthese 187(2):471–487 | https://doi.org/10.1007/s11229-010-9847-7 | Heuristic explanations of intractable f are "dysfunctional"; rebuts five objections; proposes computational-level theory revision (abs) | C3; already in DESIGN |
| **van Rooij, Evans, Müller, Gedge & Wareham (2008).** *Identifying sources of intractability in cognitive models* (analogy; read closely) | https://www.fim.uni-passau.de/fileadmin/dokumente/fakultaeten/fim/lehrstuhl/muller/Analogical.pdf | SMT is NP-hard; FPT in objects, not in arity, height or flatness | Worked example of F4 methodology |
| **van Rooij & Wareham (2008).** Computer Journal 51(3):385–404 | https://doi.org/10.1093/comjnl/bxm034 | Reviews parameterized complexity applications to perception, action and higher cognition (abs) | F4 survey cite |
| **Kwisthout, Wareham & van Rooij (2011).** Cognitive Science 35(5):779–784 (read closely) | https://doi.org/10.1111/j.1551-6709.2011.01182.x | MPE NP-hard; approximating it NP-hard; claims of tractable approximability "mathematically unfounded"; bounded treewidth gives tractability | C2 reply; F4 example |
| **Cooper (1990);** **Dagum & Luby (1993).** AIJ | https://doi.org/10.1016/0004-3702(90)90060-D · https://doi.org/10.1016/0004-3702(93)90036-B | Belief-network inference NP-hard; approximating it also NP-hard (abs) | Catalogue; C2 |
| **Eiter & Gottlob (1995).** J. ACM 42(1) | https://doi.org/10.1145/200836.200838 | "abduction is harder than deduction" (abs) | Shows deduction is the *weakest* hardness example |
| **Bylander (1994).** AIJ 69 | https://doi.org/10.1016/0004-3702(94)90081-7 | STRIPS plan existence PSPACE-complete; restrictions give NP-hard or polynomial (abs) | Planning row; fixes DESIGN's "PSPACE without the bound" cite |
| **Cook (1971).** STOC | https://doi.org/10.1145/800157.805047 | SAT NP-complete (so entailment coNP-complete) | Entailment row |
| **Even, Itai & Shamir (1976).** SIAM J. Comput. 5(4) | https://doi.org/10.1137/0205048 | "all the common timetable problems are NP-complete" | Best single real-world feasibility example |
| **Garey & Johnson (1979).** *Computers and Intractability.* W. H. Freeman (reviews located: Hartmanis 1982 SIAM Rev.; Book 1980 Bull. AMS) | https://doi.org/10.1137/1024022 | The standard NP-completeness catalogue (not re-read here) | Canonical "catalogue" cite |
| **Aaronson (2011).** *Why Philosophers Should Care About Computational Complexity.* arXiv 1108.1791 (2011); per the arXiv comment, "to appear in 'Computability: Gödel, Turing, Church, and beyond,' MIT Press" (read §§2, 3.1, 5, 11) | https://arxiv.org/abs/1108.1791 | Polynomial vs exponential as the efficiency line; logical omniscience; "it will often be computationally intractable" for agents "to act in accordance with classical economics"; 2-player Nash PPAD-complete | Philosophical framing; C7; economics |
| **Aaronson (2005).** *NP-complete Problems and Physical Reality.* ACM SIGACT News | https://arxiv.org/abs/quant-ph/0502072 | No physical proposal (soap bubbles, protein folding, quantum, …) likely solves NP-complete problems efficiently | Answers "nature solves it, so it's easy" |
| **Simon (1955).** Quarterly Journal of Economics 69(1):99ff | https://doi.org/10.2307/1884852 | Behavioural model of rational choice under limited capacity (satisficing) (title and secondary) | F3 origin |
| **Gigerenzer & Gaissmaier (2011).** Annual Rev. Psych. 62:451–482 | https://doi.org/10.1146/annurev-psych-120709-145346 | Heuristics ignore information; how well they do "is an empirical rather than an a priori issue" (abs) | F3; heuristics as adaptive |
| **Russell & Subramanian (1995).** JAIR 2:575–609 | https://doi.org/10.1613/jair.133 | Perfect rationality imposes "fundamentally unsatisfiable requirements"; define bounded optimality (abs) | F3: AI-side framing for LLMs |
| **Lieder & Griffiths (2020).** BBS 43:e1 (read closely) | https://doi.org/10.1017/S0140525X1900061X | Exact solutions are "often computationally intractable"; real-world decision complexity "far exceeds cognitive capacity"; optimal meta-decision is even more intractable | F3 core; C5 |
| **Bossaerts & Murawski (2017).** TICS 21(12):917–929 | https://doi.org/10.1016/j.tics.2017.09.005 | Complexity theory quantifies decision difficulty; human decisions are affected by it; most decision models are intractable (abs) | F3; human analogue of O1 |
| **Murawski & Bossaerts (2016).** Sci. Rep. 6:34851 | https://doi.org/10.1038/srep34851 | Human knapsack performance falls with computer-science complexity; partial overlap with computer algorithms (abs) | Human evidence; borrow instance-complexity metric |
| **Franco, Doroc, Yadav, Bossaerts & Murawski (2022).** Sci. Rep. 12 | https://doi.org/10.1038/s41598-022-16565-w | Task-independent instance-hardness metrics predict time and accuracy in three cognitive tasks (abs) | Template for heuristic-relative hardness axis |
| **Rich et al. (2019).** Synthese; **Rich, Blokpoel, de Haan & van Rooij (2020).** TopiCS 12(4); **Otworowska et al. (2018).** Cognitive Science 42(3) | https://doi.org/10.1007/s11229-019-02431-2 · https://doi.org/10.1111/tops.12506 · https://doi.org/10.1111/cogs.12530 | Adaptation that yields ecological rationality is intractable; resource rationality, adaptive toolbox and massive modularity only relocate intractability to the evolutionary level (abs) | C5; O6 bridge (training = adaptation) |
| **van Rooij et al. (2024).** *Reclaiming AI as a Theoretical Tool for Cognitive Science.* CBB 7:616–636 | https://doi.org/10.1007/s42113-024-00217-5 | Formal proof that creating human-like/-level cognition (by learning) is "intrinsically computationally intractable" (abs) | Context; likely reviewer-known; don't overclaim |
| **Roughgarden (2019).** *Beyond Worst-Case Analysis.* CACM 62(3) (read closely) | https://arxiv.org/abs/1806.09817 | Worst case is misleading for LP, clustering, caching; "optimization problems are more likely to be NP-hard than not"; stable and planted instances are tractable | F5; C1; generality quote |
| **Roughgarden (ed.) (2020).** *Beyond the Worst-Case Analysis of Algorithms.* CUP (intro chapter read) | https://arxiv.org/abs/2007.13241 | Parameterized, smoothed and semi-random analyses; Ch. 25 (Ganesh & Vardi) on SAT solvers' empirical success | F5 reference; lead to Ganesh & Vardi |
| **Spielman & Teng (2004).** J. ACM 51(3) | https://doi.org/10.1145/990308.990310 | Simplex has polynomial smoothed complexity (abs) | F5; C1 |
| **Bogdanov & Trevisan (2006).** *Average-Case Complexity.* FnT-TCS 2(1) (ch. 1 and 5 read) | https://arxiv.org/abs/cs/0606037 | Practical difficulty vs worst-case NP-hardness; samplable ensembles (NP, PSamp); Impagliazzo–Levin | F5 "world as samplable distribution" framing |
| **Levin (1986).** SIAM J. Comput. 15(1) | https://doi.org/10.1137/0215020 | Average-case complete problems (abs) | F5 background |
| **Williams, Gomes & Selman (2003).** IJCAI (read abstract and intro) | https://people.csail.mit.edu/rrw/backdoors.pdf | Small backdoors explain good scaling on practical instances; "Most interesting AI formalisms … worst-case intractable" | C1; generality quote; already in DESIGN |
| **Ansótegui, Bonet, Giráldez-Cru, Levy & Simon (2019).** JAIR 66:443–472 | https://arxiv.org/abs/1606.03329 | Industrial SAT has high modularity; random instances lack it; learnt clauses destroy it | C1; justify our items as deliberately unstructured |
| **Mull, Fremont & Seshia (2016).** SAT 2016 (LNCS), pp. 141–159 | https://doi.org/10.1007/978-3-319-40970-2_10 | Community structure is not sufficient to explain CDCL success; random modular UNSAT instances have exponential resolution proofs | Reply to C1 |
| **Daniely, Linial & Saks (2012).** arXiv 1205.4891 | https://arxiv.org/abs/1205.4891 | If a good clustering exists it can often be found efficiently; "clustering should not be considered a hard task" (abs) | Sharpest form of C1 |
| **Duchnowski, Pavlick & Koller (2025).** EHOP. EMNLP 2025 (Findings) (intro and dataset read) | https://arxiv.org/abs/2502.13776 | "Many real world tasks that people face … are NP hard optimization problems"; costumed and inverted variants; textbook framings solved best | Recent LLM statement of O1; catalogue rows 5–7 |
| **Fan et al. (2024).** NPHardEval. ACL 2024 | https://arxiv.org/abs/2312.14890 | Benchmark across P, NP-complete and NP-hard classes, updated monthly (abs) | LLM context |
| **Yang et al. (2025).** NPPC. TMLR | https://arxiv.org/abs/2504.11239 | Ever-scaling NP-complete benchmark; tools don't remove worst-case exponential cost (abs/summary) | C6 |
| **Hao, Zhang & Fan (2024).** LLMFP. arXiv 2410.12112 | https://arxiv.org/abs/2410.12112 | Many planning problems are optimisation problems at core; formalise, then solve (abs) | C6 (formalisation bottleneck); row 27 |
| **Zheng et al. (2024).** NATURAL PLAN; **Xie et al. (2024).** TravelPlanner, ICML | https://arxiv.org/abs/2406.04520 · https://arxiv.org/abs/2402.01622 | Realistic trip, meeting and calendar planning; GPT-4 solves 31% of trip planning (abs) | C8; agentic relevance |
| **Sikka & Sikka (2025).** *Hallucination Stations.* arXiv 2507.07505 (preprint) | https://arxiv.org/abs/2507.07505 | "beyond a certain complexity, LLMs are incapable of carrying out computational and agentic tasks or verifying their accuracy" (abs) | Cite cautiously as related; weak (6 pages, unreviewed) |
| **Shanahan (2016).** *The Frame Problem.* SEP | https://plato.stanford.edu/entries/frame-problem/ | Relevance can't be settled by appeal to relevance; exhaustive checking "starts to look computationally intractable" | Relevance/frame row; keep brief |
| **Colombo Tosatto, Governatori & Kelsen (2015).** IEEE TSC 8(6) | https://publications.uni.lu/handle/10993/19564 | Partial compliance NP-complete; full compliance coNP-complete | Law/contracts row |
| **Chen, Deng & Teng (2009).** J. ACM 56(3) | https://doi.org/10.1145/1516512.1516516 | Bimatrix Nash is PPAD-complete (abs) | Economics row |
| Andrew Keenan Richardson (2025). *Many Common Problems are NP-Hard.* Mechanistic Mind (blog) | https://mechanisticmind.substack.com/p/many-common-problems-are-np-hard | Meeting scheduling, seating charts, packing, errands, exam scheduling, Sudoku are NP-hard; linear compute increases won't reliably reach optima | Andrew's own prior statement of O1; the paper version should replace its Wikipedia links with the cites above |

---

## Suggested changes to DESIGN.md

All of these are for §3 O1. They are suggestions only; DESIGN.md has not been edited.

1. **Replace the "Claim, stated carefully" paragraph with a three-layer claim:**

   > **Claim.** (a) *Worst-case cores.* The formal problems underneath many everyday, professional and cognitive tasks are NP-hard or harder (coNP, Σ₂ᵖ/Π₂ᵖ, PSPACE, PPAD). For several of them even feasibility or approximation is hard. (b) *Generality.* The more general the class of tasks an agent must handle, the more surely that class contains intractable sub-problems. Cognitive science finds NP-hard computational-level theories across perception, reasoning, categorisation, decision-making and planning (van Rooij 2015). "Most interesting AI formalisms for reasoning, planning, and learning" are worst-case intractable (Williams et al. 2003). (c) *Effective hardness is budget-relative and distributional.* For an agent with budget B, a realistic distribution D is effectively hard to the extent that it has non-negligible mass on items that no known procedure within B answers correctly. (c) is what we measure; (a) and (b) are why we expect it to be non-zero.

2. **Give every row of the O1 table a citation, and add 4–6 non-puzzle rows.** Suggested additions from the catalogue:
   - timetabling (Even et al. 1976);
   - regulatory compliance (Colombo Tosatto et al. 2015);
   - medical abduction (Bylander et al. 1991);
   - Bayesian diagnosis (Cooper 1990; Dagum & Luby 1993);
   - Nash equilibrium (Chen, Deng & Teng 2009);
   - residency matching with couples (Csáji et al. 2024).

   Add a column for **feas / opt / approx**. Specific fixes to existing rows:
   - Planning: cite Bylander 1994.
   - Sudoku: cite Colbourn 1984 (Latin squares); Yato & Seta is still unverified.
   - Minesweeper: cite Kaye 2000.
   - Entailment: cite Cook 1971.
   - Monadic first-order logic (NEXPTIME) and register allocation: no source was found this session, so add one or drop the rows (see Unverified).

3. **Add one sentence on why logic isn't the headline.** For example: "Deduction is the mildest case; abduction, belief revision, probabilistic explanation, planning and equilibrium computation sit higher (Eiter & Gottlob 1995; Kwisthout et al. 2011; Bylander 1994; Chen et al. 2009)." This supports the entailment pilot and shows the project generalises.

4. **Add a "Frameworks" line of two or three sentences**, so readers see the pedigree. Suggested wording:
   - "Bounded rationality (Simon 1955), bounded optimality (Russell & Subramanian 1995) and resource-rational analysis (Lieder & Griffiths 2020) all treat heuristics as the response to intractability."
   - "Human accuracy falls with instance-level complexity (Murawski & Bossaerts 2016; Franco et al. 2022). We ask the same of LLMs, where the procedure can be inspected."

5. **Add parameterized complexity to "What we'll do" step 2.**
   - For each domain, name the source-of-complexity parameter (van Rooij & Wareham 2008) and sweep it.
   - Example parameters: variables and density for SAT; colours and degeneracy for colouring; capacity and correlation structure for knapsack; number of objects for structure-mapping-like items.
   - This turns C4 (overgeneralisation) into a measured curve.

6. **Expand the caveats** with:
   - Mull et al. 2016: structure doesn't by itself make SAT easy.
   - Ansótegui et al. 2019: random instances lack industrial structure. Say explicitly that our items are deliberately unstructured or near-threshold, so they sample the hard tail rather than typical industrial instances.
   - Bogdanov & Trevisan: whether naturally generated instances are easy on average is open.
   - The **budget-gap** point: easy for CDCL is not easy within an LLM's token budget.
   - The tools objection (NPPC; LLMFP), with the formalisation-bottleneck reply.

7. **Add the relocation objection, with an O6 link.** For example: "Choosing heuristics by adaptation is itself intractable (Rich et al. 2019, 2020). For LLMs, training is that adaptation process. H2 predicts which heuristic it selects anyway." This pre-empts a likely van-Rooij-school reviewer and strengthens O6.

8. **Keep O1 to a page** (the existing guidance). A suggested motivation paragraph for the paper, about 120 words:

   > Many tasks people ask reasoning systems to perform have NP-hard or harder formal cores: timetabling and scheduling, configuration, diagnosis and explanation, regulatory compliance, planning, and equilibrium computation [cites]. For several, even finding a feasible or approximately optimal answer is hard [cites]. Cognitive science reads this ubiquity as the price of generality: computational-level theories of general capacities are typically intractable [van Rooij 2015]. Worst-case hardness is not typical-case hardness, and structured instances are often easy [Williams et al.; Roughgarden]. But "easy" for a solver taking millions of steps is not easy for a model answering in a few thousand tokens. We therefore measure hardness relative to the model's budget, and ask what the model computes instead on the instances above it.

9. **Add the 15–20 most-used references from the key-sources table to §10.**

---

## Unverified / leads

These were recalled, or only partly confirmed. Check them before citing.

- **Yato & Seta (2003).** *Complexity and Completeness of Finding Another Solution and Its Application to Puzzles.* IEICE Trans. Fundamentals. The usual cite for generalised Sudoku (n²×n²) being NP-complete. Not found on Crossref in this session.
- **Gupta & Nau (1992).** *On the complexity of blocks-world planning.* AIJ. Optimal Blocksworld is NP-hard. Known here only via LLMFP's classification, from a search snippet.
- **Ronn (1990).** NP-completeness of HRC (J. Algorithms). Known only via Csáji et al. 2024.
- **Mancinelli, Boender, Di Cosmo, Vouillon, Durak & Leroy (2006).** ASE'06, https://doi.org/10.1109/ASE.2006.49. The bibliographic record is verified. The usual claim, that package installability is NP-complete, was **not** checked this session.
- **Arora, Barak, Brunnermeier & Ge (2011).** The record and general claim are verified. The specific hardness assumption (I recall a planted densest-subgraph conjecture) was not checked.
- **Eiter & Gottlob (1992).** The exact class (I recall Π₂ᵖ-completeness for several revision operators) was not checked.
- **Eiter & Gottlob (1995).** The exact Σ₂ᵖ-completeness statement is cut off in the abstract seen here.
- **Impagliazzo (1995).** *A personal view of average-case complexity* (Structure in Complexity Theory), https://doi.org/10.1109/SCT.1995.514853. The record is verified. The "five worlds" content (Algorithmica, Heuristica, Pessiland, Minicrypt, Cryptomania) was not read. "Are we in Heuristica?" is a natural way to phrase O1's open question.
- **Cherniak (1981).** *Minimal Rationality.* Mind 90(358), https://doi.org/10.1093/mind/XC.358.161. **Levesque (1988).** *Logic and the Complexity of Reasoning.* J. Phil. Logic 17(4), https://doi.org/10.1007/BF00297511. **Oaksford & Chater (1991).** *Against Logicist Cognitive Science.* Mind & Language 6(1), https://doi.org/10.1111/j.1468-0017.1991.tb00173.x. All records are verified, and the content was not read. These are the classic "logic-based cognition is intractable" sources, and van Rooij 2015 cites Oaksford & Chater (1998) for this argument. Good for Andrew's "logical reasoning" angle.
- **Monadic first-order satisfiability is NEXPTIME-complete** (DESIGN O1 table). I recall Lewis (1980), *Complexity results for classes of quantificational formulas*, JCSS. Not checked.
- **Register allocation as graph coloring** (DESIGN O1 table). I recall Chaitin et al. (1981). Not checked.
- **Rich, de Haan, Wareham & van Rooij (2021).** *How hard is cognitive science?* Proc. CogSci 43, https://escholarship.org/uc/item/8cr8x1c4 (record via PsyArXiv, https://doi.org/10.31234/osf.io/k79nv). The content was not read. It appears to argue that *finding* tractable computational-level theories is itself hard, which is relevant to "how to frame a real problem formally".
- **Ganesh & Vardi.** Ch. 25 of *Beyond the Worst-Case Analysis of Algorithms* (2020), on SAT solvers' empirical effectiveness. Existence is confirmed via Roughgarden's introduction; the exact title was not confirmed.
- **Veale & Keane (1997).** NP-hardness of structure mapping (IJCAI). Cited inside van Rooij et al. 2008; not located directly.
- **Venue of van Rooij, Evans, Müller, Gedge & Wareham (2008).** The PDF has no venue line. The format and date (April 2008, six pages) suggest Proc. CogSci 2008. Confirm before citing.
- **Marr (1982).** *Vision.* W. H. Freeman. Used here only as van Rooij 2015 uses it; no publisher page was fetched.
- **Leads for further rows (not searched before the search budget ran out):**
  - Chaitin register allocation;
  - Nisan & Ronen algorithmic mechanism design;
  - redistricting / gerrymandering hardness;
  - jigsaw puzzles (Demaine & Demaine 2007);
  - Kemeny ranking aggregation;
  - tax or benefit-eligibility rules as SAT/SMT;
  - Wareham's work on the intractability of action and motor planning;
  - Blokpoel et al. on recipient design and communication ("Intractability obstacles to explanations of communication", van de Braak et al., PsyArXiv 2024, https://doi.org/10.31234/osf.io/ep8qc; record seen, not read).
- **Not found in this session:** a 2026 paper arguing specifically that *agentic* LLM tasks are NP-hard as a class. The closest are Sikka & Sikka (2025, weak), ACONIC (Zhou et al. 2025, arXiv 2510.07772, which uses constraint-graph treewidth to decompose agent tasks) and LLMFP. The WebSearch budget ran out before a 2026-specific search could finish, so this gap may not be real.
