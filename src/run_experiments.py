#!/usr/bin/env python3
"""
run_experiments.py
==================
Orchestrates the full AAGMM experimental pipeline:
  1. Runs 750 simulation trials (5 scenarios x 5 levels x 30 trials)
  2. Computes aggregated statistics with 95% CIs
  3. Runs pairwise statistical tests (Welch's t-test, Cohen's d)
  4. Saves all results to results/ directory

Usage:
    python src/run_experiments.py [--trials 30] [--seed 42] [--output results/]
"""

import argparse
import json
import csv
import math
import os
import statistics
import sys
import time
from collections import defaultdict
from itertools import combinations

# Ensure src/ is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulation import run_single, SEED

# ============================================================
# SCENARIO DEFINITIONS
# ============================================================
SCENARIOS = {
    "greenfield":      {"num_agents": 30, "num_tasks": 1000},
    "scaling":         {"num_agents": 50, "num_tasks": 2000},
    "cross_functional": {"num_agents": 35, "num_tasks": 1500},
    "adversarial":     {"num_agents": 30, "num_tasks": 1000},
    "optimization":    {"num_agents": 40, "num_tasks": 1500},
}

METRICS_KEYS = [
    "sprawl_index", "risk_incident_rate", "effective_task_completion",
    "governance_cost_ratio", "time_to_value_days", "delegation_safety_rate",
    "net_business_value", "shadow_agents", "duplicate_agents",
    "orphaned_agents", "total_violations"
]


def run_all_experiments(num_trials: int = 30, seed: int = SEED,
                        verbose: bool = True) -> list:
    """Run all scenario-level combinations with multiple trials."""
    all_results = []
    total = len(SCENARIOS) * 5 * num_trials
    count = 0
    start = time.time()

    for scenario_name, params in SCENARIOS.items():
        for level in range(1, 6):
            for trial in range(num_trials):
                result = run_single(
                    scenario=scenario_name,
                    gov_level=level,
                    num_agents=params["num_agents"],
                    num_tasks=params["num_tasks"],
                    trial=trial,
                )
                all_results.append(result)
                count += 1

            if verbose:
                r = all_results[-1]
                print(f"  [{count}/{total}] {scenario_name} L{level}: "
                      f"SI={r['sprawl_index']:.3f} "
                      f"RIR={r['risk_incident_rate']:.1f} "
                      f"ETCR={r['effective_task_completion']:.3f} "
                      f"NBV={r['net_business_value']:.3f}")

    elapsed = time.time() - start
    if verbose:
        print(f"\nCompleted {count} runs in {elapsed:.1f}s")
    return all_results


def compute_aggregated(results: list) -> list:
    """Group by (level, scenario) and compute mean/std/CI."""
    groups = defaultdict(list)
    for r in results:
        key = (r["governance_level"], r["governance_name"], r["scenario"])
        groups[key].append(r)

    aggregated = []
    for (level, name, scenario), trials in sorted(groups.items()):
        agg = {
            "governance_level": level,
            "governance_name": name,
            "scenario": scenario,
            "n_trials": len(trials),
        }
        for mk in METRICS_KEYS:
            values = [t[mk] for t in trials]
            m = statistics.mean(values)
            s = statistics.stdev(values) if len(values) > 1 else 0.0
            ci = 1.96 * s / math.sqrt(len(values))
            agg[f"{mk}_mean"] = round(m, 4)
            agg[f"{mk}_std"] = round(s, 4)
            agg[f"{mk}_ci95"] = round(ci, 4)
        aggregated.append(agg)
    return aggregated


def compute_cross_level_summary(results: list) -> list:
    """Compute summary across all scenarios per governance level."""
    groups = defaultdict(list)
    for r in results:
        groups[r["governance_level"]].append(r)

    summary = []
    for level in sorted(groups.keys()):
        trials = groups[level]
        s = {
            "governance_level": level,
            "governance_name": trials[0]["governance_name"],
            "n_observations": len(trials),
        }
        for mk in METRICS_KEYS:
            values = [t[mk] for t in trials]
            m = statistics.mean(values)
            sd = statistics.stdev(values)
            s[f"{mk}_mean"] = round(m, 4)
            s[f"{mk}_std"] = round(sd, 4)
            s[f"{mk}_ci95"] = round(1.96 * sd / math.sqrt(len(values)), 4)
        summary.append(s)
    return summary


def run_statistical_tests(results: list) -> dict:
    """Pairwise Welch's t-test + Cohen's d on Net Business Value."""
    groups = defaultdict(list)
    for r in results:
        groups[r["governance_level"]].append(r["net_business_value"])

    comparisons = {}
    for l1, l2 in combinations(sorted(groups.keys()), 2):
        v1, v2 = groups[l1], groups[l2]
        n1, n2 = len(v1), len(v2)
        m1, m2 = statistics.mean(v1), statistics.mean(v2)
        s1, s2 = statistics.stdev(v1), statistics.stdev(v2)

        se = math.sqrt(s1**2 / n1 + s2**2 / n2)
        t_stat = (m2 - m1) / se if se > 0 else 0

        # Welch-Satterthwaite degrees of freedom
        num = (s1**2 / n1 + s2**2 / n2) ** 2
        denom = ((s1**2 / n1)**2 / (n1 - 1) +
                 (s2**2 / n2)**2 / (n2 - 1))
        df = num / denom if denom > 0 else 1

        # Cohen's d
        pooled = math.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
        d = (m2 - m1) / pooled if pooled > 0 else 0

        # p-value (normal approximation for large samples)
        z = abs(t_stat)
        p_val = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))

        comparisons[f"L{l1}_vs_L{l2}"] = {
            f"mean_L{l1}": round(m1, 4),
            f"mean_L{l2}": round(m2, 4),
            "difference": round(m2 - m1, 4),
            "t_statistic": round(t_stat, 4),
            "df": round(df, 1),
            "p_value": round(p_val, 8),
            "cohens_d": round(d, 4),
            "significant_p005": p_val < 0.05,
            "significant_p001": p_val < 0.01,
        }
    return comparisons


def print_summary_table(summary: list) -> None:
    """Print a formatted summary table."""
    print("\n" + "=" * 100)
    print("CROSS-LEVEL SUMMARY (All Scenarios Combined)")
    print("=" * 100)
    header = (f"{'Level':<14} {'Sprawl':>10} {'Risk/1K':>10} "
              f"{'Completion':>12} {'Gov Cost':>10} {'TTV(d)':>8} "
              f"{'Deleg Safe':>12} {'NBV':>10}")
    print(header)
    print("-" * 100)
    for s in summary:
        print(f"L{s['governance_level']} {s['governance_name']:<10} "
              f"{s['sprawl_index_mean']:>10.4f} "
              f"{s['risk_incident_rate_mean']:>10.2f} "
              f"{s['effective_task_completion_mean']:>12.4f} "
              f"{s['governance_cost_ratio_mean']:>10.4f} "
              f"{s['time_to_value_days_mean']:>8.1f} "
              f"{s['delegation_safety_rate_mean']:>12.4f} "
              f"{s['net_business_value_mean']:>10.4f}")


def print_pairwise_table(tests: dict) -> None:
    """Print pairwise comparison results."""
    print("\n" + "=" * 90)
    print("PAIRWISE COMPARISONS (Net Business Value - Welch's t-test)")
    print("=" * 90)
    for comp, v in tests.items():
        sig = "***" if v["significant_p001"] else ("*" if v["significant_p005"] else "ns")
        print(f"  {comp}: delta={v['difference']:+.4f}, "
              f"t={v['t_statistic']:.2f}, p={v['p_value']:.8f}, "
              f"d={v['cohens_d']:.3f} {sig}")


def save_results(output_dir: str, raw: list, aggregated: list,
                 summary: list, tests: dict) -> None:
    """Save all results to disk."""
    os.makedirs(os.path.join(output_dir, "raw"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "aggregated"), exist_ok=True)

    # Raw JSON
    with open(os.path.join(output_dir, "raw", "raw_results.json"), "w") as f:
        json.dump(raw, f, indent=2)

    # Raw CSV
    if raw:
        keys = raw[0].keys()
        with open(os.path.join(output_dir, "raw", "raw_results.csv"), "w",
                  newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(raw)

    # Aggregated
    with open(os.path.join(output_dir, "aggregated",
              "scenario_level_aggregated.json"), "w") as f:
        json.dump(aggregated, f, indent=2)

    # Cross-level summary
    with open(os.path.join(output_dir, "aggregated",
              "cross_level_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    # Statistical tests
    with open(os.path.join(output_dir, "aggregated",
              "statistical_tests.json"), "w") as f:
        json.dump(tests, f, indent=2)

    # Human-readable summary
    with open(os.path.join(output_dir, "aggregated",
              "summary_table.txt"), "w") as f:
        f.write("AAGMM Cross-Level Summary\n")
        f.write("=" * 90 + "\n")
        f.write(f"{'Level':<14} {'Sprawl':>10} {'Risk/1K':>10} "
                f"{'Completion':>12} {'Gov Cost':>10} "
                f"{'Deleg Safe':>12} {'NBV':>10}\n")
        f.write("-" * 90 + "\n")
        for s in summary:
            f.write(f"L{s['governance_level']} {s['governance_name']:<10} "
                    f"{s['sprawl_index_mean']:>10.4f} "
                    f"{s['risk_incident_rate_mean']:>10.2f} "
                    f"{s['effective_task_completion_mean']:>12.4f} "
                    f"{s['governance_cost_ratio_mean']:>10.4f} "
                    f"{s['delegation_safety_rate_mean']:>12.4f} "
                    f"{s['net_business_value_mean']:>10.4f}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Run AAGMM experiments")
    parser.add_argument("--trials", type=int, default=30,
                        help="Trials per condition (default: 30)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Base random seed (default: 42)")
    parser.add_argument("--output", type=str, default="results",
                        help="Output directory (default: results/)")
    args = parser.parse_args()

    print("=" * 60)
    print("AAGMM EXPERIMENTAL SIMULATION")
    print("=" * 60)
    print(f"Seed: {args.seed}")
    print(f"Trials per condition: {args.trials}")
    print(f"Total conditions: 5 levels x 5 scenarios = 25")
    print(f"Total simulation runs: {5 * 5 * args.trials}")
    print(f"Output: {args.output}/")
    print("=" * 60)

    print("\n[1/4] Running experiments...")
    raw = run_all_experiments(num_trials=args.trials, seed=args.seed)

    print("\n[2/4] Computing aggregated statistics...")
    agg = compute_aggregated(raw)

    print("[3/4] Computing cross-level summary...")
    summary = compute_cross_level_summary(raw)
    print_summary_table(summary)

    print("\n[4/4] Running statistical tests...")
    tests = run_statistical_tests(raw)
    print_pairwise_table(tests)

    print(f"\nSaving results to {args.output}/...")
    save_results(args.output, raw, agg, summary, tests)

    print("\n" + "=" * 60)
    print("ALL EXPERIMENTS COMPLETE")
    print("=" * 60)
    print(f"  Raw results:    {args.output}/raw/raw_results.{{json,csv}}")
    print(f"  Aggregated:     {args.output}/aggregated/")
    print(f"  Stats tests:    {args.output}/aggregated/statistical_tests.json")
    print(f"  Summary table:  {args.output}/aggregated/summary_table.txt")


if __name__ == "__main__":
    main()
