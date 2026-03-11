#!/usr/bin/env python3
"""
generate_figures.py
===================
Generates publication-quality figures for the AAGMM paper.

Usage:
    python src/generate_figures.py [--results results/] [--output results/figures/]

Requires: matplotlib (pip install matplotlib)
"""

import argparse
import json
import os
import sys

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
except ImportError:
    print("ERROR: matplotlib is required. Install with: pip install matplotlib")
    sys.exit(1)


# Style constants
COLORS = {1: "#E74C3C", 2: "#E67E22", 3: "#F1C40F", 4: "#2ECC71", 5: "#3498DB"}
LEVEL_NAMES = {1: "L1 Ad-hoc", 2: "L2 Reactive", 3: "L3 Defined",
               4: "L4 Managed", 5: "L5 Optimized"}
plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
})


def load_data(results_dir: str):
    summary_path = os.path.join(results_dir, "aggregated", "cross_level_summary.json")
    agg_path = os.path.join(results_dir, "aggregated", "scenario_level_aggregated.json")
    with open(summary_path) as f:
        summary = json.load(f)
    with open(agg_path) as f:
        aggregated = json.load(f)
    return summary, aggregated


def fig1_nbv_bar(summary, output_dir):
    """Figure 1: Net Business Value by Governance Level."""
    levels = [s["governance_level"] for s in summary]
    nbv = [s["net_business_value_mean"] for s in summary]
    ci = [s["net_business_value_ci95"] for s in summary]
    colors = [COLORS[l] for l in levels]
    labels = [LEVEL_NAMES[l] for l in levels]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, nbv, yerr=ci, color=colors, edgecolor="white",
                  linewidth=1.5, capsize=5, error_kw={"linewidth": 1.5})
    ax.set_ylabel("Net Business Value (NBV)")
    ax.set_title("Net Business Value by Governance Maturity Level")
    ax.set_ylim(0, 1.05)
    for bar, val in zip(bars, nbv):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig1_nbv_by_level.png"), dpi=300)
    plt.savefig(os.path.join(output_dir, "fig1_nbv_by_level.pdf"))
    plt.close()
    print("  Created: fig1_nbv_by_level.{png,pdf}")


def fig2_metrics_radar(summary, output_dir):
    """Figure 2: Multi-metric comparison across levels."""
    metrics = ["sprawl_index_mean", "risk_incident_rate_mean",
               "effective_task_completion_mean", "delegation_safety_rate_mean",
               "net_business_value_mean"]
    metric_labels = ["Sprawl\nIndex", "Risk\nIncidents", "Task\nCompletion",
                     "Delegation\nSafety", "Net Business\nValue"]

    fig, axes = plt.subplots(1, 5, figsize=(16, 4), sharey=False)
    for idx, (mk, label) in enumerate(zip(metrics, metric_labels)):
        ax = axes[idx]
        vals = [s[mk] for s in summary]
        colors = [COLORS[s["governance_level"]] for s in summary]
        labels = [f"L{s['governance_level']}" for s in summary]
        bars = ax.bar(labels, vals, color=colors, edgecolor="white", linewidth=1)
        ax.set_title(label, fontsize=10)
        ax.tick_params(axis="x", labelsize=9)
        if "sprawl" in mk or "risk" in mk:
            ax.invert_yaxis() if False else None  # lower is better shown normally
    plt.suptitle("Business Outcome Metrics Across Governance Maturity Levels",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig2_metrics_comparison.png"),
                dpi=300, bbox_inches="tight")
    plt.savefig(os.path.join(output_dir, "fig2_metrics_comparison.pdf"),
                bbox_inches="tight")
    plt.close()
    print("  Created: fig2_metrics_comparison.{png,pdf}")


def fig3_sprawl_risk(summary, output_dir):
    """Figure 3: Sprawl Index and Risk Incident Rate decline."""
    levels = [s["governance_level"] for s in summary]
    si = [s["sprawl_index_mean"] for s in summary]
    si_ci = [s["sprawl_index_ci95"] for s in summary]
    rir = [s["risk_incident_rate_mean"] for s in summary]
    rir_ci = [s["risk_incident_rate_ci95"] for s in summary]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    x = range(len(levels))
    labels = [LEVEL_NAMES[l] for l in levels]

    color1 = "#E74C3C"
    ax1.errorbar(x, si, yerr=si_ci, color=color1, marker="o", linewidth=2,
                 markersize=8, capsize=4, label="Sprawl Index")
    ax1.set_ylabel("Sprawl Index", color=color1, fontsize=12)
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_ylim(-0.02, 0.6)

    ax2 = ax1.twinx()
    color2 = "#3498DB"
    ax2.errorbar(x, rir, yerr=rir_ci, color=color2, marker="s", linewidth=2,
                 markersize=8, capsize=4, label="Risk Incidents/1K")
    ax2.set_ylabel("Risk Incidents per 1,000 Actions", color=color2, fontsize=12)
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim(-2, 70)

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_title("Sprawl Index and Risk Incident Rate by Governance Level")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig3_sprawl_risk_decline.png"), dpi=300)
    plt.savefig(os.path.join(output_dir, "fig3_sprawl_risk_decline.pdf"))
    plt.close()
    print("  Created: fig3_sprawl_risk_decline.{png,pdf}")


def fig4_scenario_heatmap(aggregated, output_dir):
    """Figure 4: NBV heatmap by scenario and level."""
    scenarios = ["greenfield", "scaling", "cross_functional", "adversarial", "optimization"]
    scenario_labels = ["Greenfield", "Scaling", "Cross-Func.", "Adversarial", "Optimization"]
    levels = [1, 2, 3, 4, 5]

    # Build matrix
    matrix = []
    for sc in scenarios:
        row = []
        for lv in levels:
            match = [a for a in aggregated
                     if a["scenario"] == sc and a["governance_level"] == lv]
            row.append(match[0]["net_business_value_mean"] if match else 0)
        matrix.append(row)

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=0.5, vmax=1.0)
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels([LEVEL_NAMES[l] for l in levels], fontsize=9)
    ax.set_yticks(range(len(scenarios)))
    ax.set_yticklabels(scenario_labels)
    ax.set_title("Net Business Value: Scenario × Governance Level")

    for i in range(len(scenarios)):
        for j in range(len(levels)):
            color = "white" if matrix[i][j] < 0.75 else "black"
            ax.text(j, i, f"{matrix[i][j]:.3f}", ha="center", va="center",
                    fontsize=10, fontweight="bold", color=color)

    plt.colorbar(im, ax=ax, label="NBV", shrink=0.8)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig4_scenario_heatmap.png"), dpi=300)
    plt.savefig(os.path.join(output_dir, "fig4_scenario_heatmap.pdf"))
    plt.close()
    print("  Created: fig4_scenario_heatmap.{png,pdf}")


def fig5_governance_cost_tradeoff(summary, output_dir):
    """Figure 5: Governance cost vs. NBV tradeoff."""
    levels = [s["governance_level"] for s in summary]
    gcr = [s["governance_cost_ratio_mean"] for s in summary]
    nbv = [s["net_business_value_mean"] for s in summary]

    fig, ax = plt.subplots(figsize=(7, 5))
    for i, lv in enumerate(levels):
        ax.scatter(gcr[i], nbv[i], s=200, c=COLORS[lv], edgecolors="black",
                   linewidth=1.5, zorder=5)
        ax.annotate(LEVEL_NAMES[lv], (gcr[i], nbv[i]),
                    textcoords="offset points", xytext=(10, 5), fontsize=9)
    ax.plot(gcr, nbv, "--", color="gray", alpha=0.5, linewidth=1)
    ax.set_xlabel("Governance Cost Ratio")
    ax.set_ylabel("Net Business Value")
    ax.set_title("Governance Investment vs. Business Value (Automation Dividend at L5)")
    ax.annotate("Automation\nDividend", xy=(0.16, 0.943),
                xytext=(0.12, 0.92), fontsize=9, color="#3498DB",
                arrowprops=dict(arrowstyle="->", color="#3498DB"))
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig5_cost_value_tradeoff.png"), dpi=300)
    plt.savefig(os.path.join(output_dir, "fig5_cost_value_tradeoff.pdf"))
    plt.close()
    print("  Created: fig5_cost_value_tradeoff.{png,pdf}")


def main():
    parser = argparse.ArgumentParser(description="Generate AAGMM paper figures")
    parser.add_argument("--results", default="results", help="Results directory")
    parser.add_argument("--output", default="results/figures", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    print("Loading data...")
    summary, aggregated = load_data(args.results)

    print("Generating figures...")
    fig1_nbv_bar(summary, args.output)
    fig2_metrics_radar(summary, args.output)
    fig3_sprawl_risk(summary, args.output)
    fig4_scenario_heatmap(aggregated, args.output)
    fig5_governance_cost_tradeoff(summary, args.output)
    print(f"\nAll figures saved to {args.output}/")


if __name__ == "__main__":
    main()
