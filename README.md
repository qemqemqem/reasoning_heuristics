# reasoning_heuristics

**Heuristics Under Hardness: how do language models answer problems they cannot solve exactly?**

Many reasoning tasks are NP-hard or coNP-hard in general, and language models answer them with bounded computation. So on hard instances they must be using heuristics. This project tries to identify which heuristics, by:
- discriminating between competing candidate heuristics using models' answers, especially their errors;
- looking for the same heuristics inside open-weight models;
- situating them in RASP-L.

Start with the design document, [docs/DESIGN.md](docs/DESIGN.md). The literature review behind it is [docs/LITERATURE.md](docs/LITERATURE.md), and [docs/PAPER_SKELETON.md](docs/PAPER_SKELETON.md) sketches the paper we expect to write.

The per-heuristic eval designs and example question libraries are in [docs/verticals/](docs/verticals/) and [data/examples/](data/examples/). The Phase 1 scope and costs are in [docs/SCOPE.md](docs/SCOPE.md).

Theoretical priors for each heuristic family, written before any data, are in [docs/theory/](docs/theory/README.md): what transformers can compute, what RASP-L simplicity predicts they learn, and what LLMs are already known to do.

This follows on from the 2025 ETR study ([arXiv 2506.11128](https://arxiv.org/abs/2506.11128)). Its code is in [Oxford-HAI-Lab/etr_case_generator](https://github.com/Oxford-HAI-Lab/etr_case_generator).
