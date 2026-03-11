# AAGMM: Agentic AI Governance Maturity Model

**Governing the Agentic Enterprise: A Governance Maturity Model for Managing AI Agent Sprawl in Business Operations**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://python.org)
[![Reproducible](https://img.shields.io/badge/Seed-42-orange.svg)](#reproducibility)

---

## Overview

This repository contains the experimental framework, data, and results for the AAGMM paper, submitted to **MDPI AI** (Special Issue: *The Use of Artificial Intelligence in Business: Innovations, Applications and Impacts*).

The **Agentic AI Governance Maturity Model (AAGMM)** is a five-level governance framework spanning 12 domains, designed to help enterprises manage the uncontrolled proliferation of autonomous AI agents ("agent sprawl") in business operations. The model is grounded in NIST AI RMF 1.0 and ISO/IEC 42001.

### Key Results

| Metric | L1 (Ad-hoc) | L5 (Optimized) | Improvement |
|--------|:-----------:|:--------------:|:-----------:|
| Sprawl Index | 0.520 | 0.028 | **94.6% reduction** |
| Risk Incidents / 1K actions | 59.08 | 2.05 | **96.5% reduction** |
| Effective Task Completion | 0.699 | 0.930 | **+33.0%** |
| Delegation Safety Rate | 0.602 | 0.992 | **+64.8%** |
| Net Business Value | 0.625 | 0.944 | **+51.0%** |

All 10 pairwise comparisons between governance levels are significant at **p < 0.001** with large effect sizes (Cohen's d > 2.0).

---

## Repository Structure

```
agentic-governance-maturity/
├── src/
│   ├── simulation.py          # Core simulation engine
│   ├── run_experiments.py     # Experiment orchestrator (750 runs)
│   └── generate_figures.py    # Publication figure generator
├── tests/
│   └── test_simulation.py     # 15 unit tests
├── results/
│   ├── raw/
│   │   ├── raw_results.json   # All 750 trial results
│   │   └── raw_results.csv    # Same data in CSV format
│   ├── aggregated/
│   │   ├── cross_level_summary.json
│   │   ├── scenario_level_aggregated.json
│   │   ├── statistical_tests.json
│   │   └── summary_table.txt
│   └── figures/
│       ├── fig1_nbv_by_level.{png,pdf}
│       ├── fig2_metrics_comparison.{png,pdf}
│       ├── fig3_sprawl_risk_decline.{png,pdf}
│       ├── fig4_scenario_heatmap.{png,pdf}
│       └── fig5_cost_value_tradeoff.{png,pdf}
├── docs/
│   └── AAGMM_Paper_MDPI_AI.tex   # Full paper (LaTeX)
├── requirements.txt
├── CITATION.cff
├── LICENSE                    # Apache 2.0
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.8 or higher (no external dependencies for core simulation)
- `matplotlib` (optional, for figure generation only)

### Reproduce All Results

```bash
# Clone the repository
git clone https://github.com/curiosityexplorer/agentic-governance-maturity.git
cd agentic-governance-maturity

# Run all 750 experiments (takes ~5 seconds)
python src/run_experiments.py

# Run unit tests (15 tests)
python tests/test_simulation.py

# Generate publication figures (requires matplotlib)
pip install matplotlib
python src/generate_figures.py
```

### Custom Experiments

```bash
# Run with different trial count or seed
python src/run_experiments.py --trials 50 --seed 123 --output my_results/
```

### Use as a Library

```python
from src.simulation import EnterpriseSimulation, run_single

# Run a single trial
result = run_single(
    scenario="greenfield",
    gov_level=3,          # AAGMM Level 3 (Defined)
    num_agents=30,
    num_tasks=1000,
    trial=0
)
print(f"NBV: {result['net_business_value']}")
print(f"Sprawl: {result['sprawl_index']}")
print(f"Risk: {result['risk_incident_rate']}")

# Full simulation with access to agent-level data
sim = EnterpriseSimulation(
    governance_level=4,
    scenario="scaling",
    num_agents=50,
    num_tasks=2000,
    seed=42
)
sim.deploy_agents()
sim.orphan_agents()
sim.run_tasks()
metrics = sim.compute_metrics()
```

---

## Experimental Design

### Scenarios

| Scenario | Agents | Tasks | Primary Stress Test |
|----------|:------:|:-----:|---------------------|
| S1: Greenfield | 30 | 1,000 | Initial sprawl formation |
| S2: Scaling | 50 | 2,000 | Governance scalability |
| S3: Cross-Functional | 35 | 1,500 | Inter-department delegation |
| S4: Adversarial | 30 | 1,000 | Security governance |
| S5: Optimization | 40 | 1,500 | Portfolio management |

### Governance Levels

| Level | Name | Key Controls |
|:-----:|------|-------------|
| L1 | Ad-hoc | None |
| L2 | Reactive | Agent registry, incident response |
| L3 | Defined | + IAM, observability, policy enforcement, HITL, audit, risk classification |
| L4 | Managed | + Automated policy, sprawl detection, lifecycle automation |
| L5 | Optimized | + Continuous improvement, predictive sprawl, governance-as-code |

### Statistical Method

- 750 total runs (5 scenarios × 5 levels × 30 trials)
- Deterministic seeding (base seed = 42) for full reproducibility
- Welch's t-test with Cohen's d for pairwise comparisons
- 95% confidence intervals for all metrics

---

## Reproducibility

Every result in this repository is fully reproducible:

- **Seed**: All experiments use `seed = 42` as the base seed
- **Determinism**: Trial seeds are derived deterministically (`42 + trial * 7919`)
- **Zero external dependencies**: Core simulation uses only Python stdlib
- **Archived results**: Pre-computed results are included in `results/`

To verify reproducibility:
```bash
# Re-run experiments and compare
python src/run_experiments.py --output results_verify/
diff results/aggregated/cross_level_summary.json results_verify/aggregated/cross_level_summary.json
```

---

## Metrics Definitions

| Metric | Formula | Description |
|--------|---------|-------------|
| **Sprawl Index (SI)** | (shadow + duplicate + orphaned) / total agents | Fraction of agents contributing to sprawl |
| **Risk Incident Rate (RIR)** | violations / total_actions × 1000 | Compliance violations per 1,000 agent actions |
| **Effective Task Completion (ETCR)** | (completed − violations) / total_tasks | Tasks completed without governance violations |
| **Governance Cost Ratio (GCR)** | governance_overhead / operating_cost | Cost of governance as fraction of total cost |
| **Delegation Safety Rate (DSR)** | safe_delegations / total_delegations | Fraction of inter-agent delegations that are safe |
| **Net Business Value (NBV)** | 0.30·ETCR + 0.20·(1−SI) + 0.20·(1−RIR/100) + 0.15·DSR + 0.15·(1−GCR) | Weighted composite business value score |

---

## Citation

If you use this work, please cite:

```bibtex
@article{acharya2026aagmm,
  title={Governing the Agentic Enterprise: A Governance Maturity Model for Managing AI Agent Sprawl in Business Operations},
  author={Acharya, Vivek},
  journal={AI (MDPI)},
  year={2026},
  issn={2673-2688},
  note={Special Issue: The Use of Artificial Intelligence in Business}
}
```

---

## Author

**Vivek Acharya**
Independent Researcher, Boston, MA, USA
Email: vacharya@bu.edu
ORCID: [0009-0002-0860-9462](https://orcid.org/0009-0002-0860-9462)

---

## License

This project is licensed under the Apache License 2.0 — see [LICENSE](LICENSE) for details.
