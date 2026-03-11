#!/usr/bin/env python3
"""
test_simulation.py
==================
Unit tests for the AAGMM simulation framework.

Usage:
    python -m pytest tests/test_simulation.py -v
    # or without pytest:
    python tests/test_simulation.py
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from simulation import (
    EnterpriseSimulation, GOVERNANCE_LEVELS, BUSINESS_FUNCTIONS,
    AGENT_CAPABILITIES, run_single, SEED
)


class TestGovernanceConfig(unittest.TestCase):
    """Test governance level configurations."""

    def test_five_levels_exist(self):
        self.assertEqual(len(GOVERNANCE_LEVELS), 5)
        for i in range(1, 6):
            self.assertIn(i, GOVERNANCE_LEVELS)

    def test_level1_has_no_controls(self):
        g = GOVERNANCE_LEVELS[1]
        self.assertFalse(g.agent_registry)
        self.assertFalse(g.identity_management)
        self.assertFalse(g.policy_enforcement)

    def test_level5_has_all_controls(self):
        g = GOVERNANCE_LEVELS[5]
        self.assertTrue(g.agent_registry)
        self.assertTrue(g.identity_management)
        self.assertTrue(g.access_control_scoped)
        self.assertTrue(g.observability)
        self.assertTrue(g.policy_enforcement)
        self.assertTrue(g.automated_policy)
        self.assertTrue(g.sprawl_detection)
        self.assertTrue(g.continuous_improvement)
        self.assertTrue(g.predictive_sprawl)
        self.assertTrue(g.governance_as_code)

    def test_progressive_controls(self):
        """Higher levels should have >= controls of lower levels."""
        for l in range(1, 5):
            lower = GOVERNANCE_LEVELS[l]
            higher = GOVERNANCE_LEVELS[l + 1]
            lower_fields = {k: v for k, v in lower.__dict__.items()
                           if isinstance(v, bool) and v}
            higher_fields = {k: v for k, v in higher.__dict__.items()
                            if isinstance(v, bool) and v}
            self.assertGreaterEqual(len(higher_fields), len(lower_fields),
                                    f"L{l+1} should have >= controls than L{l}")


class TestSimulation(unittest.TestCase):
    """Test simulation engine core functionality."""

    def test_deterministic_seed(self):
        """Same seed should produce identical results."""
        r1 = run_single("greenfield", 3, 30, 100, trial=0)
        r2 = run_single("greenfield", 3, 30, 100, trial=0)
        self.assertEqual(r1["net_business_value"], r2["net_business_value"])
        self.assertEqual(r1["sprawl_index"], r2["sprawl_index"])

    def test_different_seeds_differ(self):
        """Different trials should produce different results."""
        r1 = run_single("greenfield", 3, 30, 500, trial=0)
        r2 = run_single("greenfield", 3, 30, 500, trial=1)
        # Very unlikely to be identical with different seeds
        self.assertTrue(
            r1["net_business_value"] != r2["net_business_value"] or
            r1["sprawl_index"] != r2["sprawl_index"]
        )

    def test_agents_deployed(self):
        sim = EnterpriseSimulation(3, "greenfield", num_agents=30, num_tasks=10)
        sim.deploy_agents()
        self.assertGreater(len(sim.agents), 0)

    def test_shadow_agents_decrease_with_level(self):
        """Higher governance should produce fewer shadow agents."""
        shadow_counts = {}
        for level in [1, 3, 5]:
            sim = EnterpriseSimulation(level, "greenfield",
                                       num_agents=30, num_tasks=10, seed=42)
            sim.deploy_agents()
            shadows = sum(1 for a in sim.agents if a.is_shadow)
            shadow_counts[level] = shadows
        self.assertGreater(shadow_counts[1], shadow_counts[5])

    def test_metrics_computed(self):
        """Metrics should contain all expected keys."""
        sim = EnterpriseSimulation(3, "greenfield", num_agents=20, num_tasks=100)
        sim.deploy_agents()
        sim.orphan_agents()
        sim.run_tasks()
        m = sim.compute_metrics()

        expected_keys = [
            "governance_level", "governance_name", "scenario",
            "sprawl_index", "risk_incident_rate",
            "effective_task_completion", "governance_cost_ratio",
            "delegation_safety_rate", "net_business_value",
        ]
        for k in expected_keys:
            self.assertIn(k, m, f"Missing metric: {k}")

    def test_nbv_in_valid_range(self):
        """NBV should be between 0 and 1."""
        for level in range(1, 6):
            r = run_single("greenfield", level, 30, 200, trial=0)
            self.assertGreaterEqual(r["net_business_value"], 0)
            self.assertLessEqual(r["net_business_value"], 1)

    def test_sprawl_index_in_valid_range(self):
        for level in range(1, 6):
            r = run_single("greenfield", level, 30, 200, trial=0)
            self.assertGreaterEqual(r["sprawl_index"], 0)
            self.assertLessEqual(r["sprawl_index"], 1)


class TestGovernanceOutcomes(unittest.TestCase):
    """Test that higher governance levels produce better outcomes."""

    def setUp(self):
        """Run experiments for all levels, averaging 10 trials."""
        self.level_results = {}
        for level in range(1, 6):
            nbvs = []
            sis = []
            rirs = []
            for trial in range(10):
                r = run_single("greenfield", level, 30, 500, trial=trial)
                nbvs.append(r["net_business_value"])
                sis.append(r["sprawl_index"])
                rirs.append(r["risk_incident_rate"])
            self.level_results[level] = {
                "nbv": sum(nbvs) / len(nbvs),
                "si": sum(sis) / len(sis),
                "rir": sum(rirs) / len(rirs),
            }

    def test_nbv_increases_with_level(self):
        for l in range(1, 5):
            self.assertLess(
                self.level_results[l]["nbv"],
                self.level_results[l+1]["nbv"],
                f"NBV should increase from L{l} to L{l+1}"
            )

    def test_sprawl_decreases_with_level(self):
        for l in range(1, 5):
            self.assertGreater(
                self.level_results[l]["si"],
                self.level_results[l+1]["si"],
                f"Sprawl should decrease from L{l} to L{l+1}"
            )

    def test_risk_decreases_with_level(self):
        for l in range(1, 5):
            self.assertGreater(
                self.level_results[l]["rir"],
                self.level_results[l+1]["rir"],
                f"Risk should decrease from L{l} to L{l+1}"
            )


class TestAllScenarios(unittest.TestCase):
    """Test that all five scenarios run without errors."""

    def test_all_scenarios_complete(self):
        scenarios = {
            "greenfield": (30, 100),
            "scaling": (50, 200),
            "cross_functional": (35, 150),
            "adversarial": (30, 100),
            "optimization": (40, 150),
        }
        for name, (agents, tasks) in scenarios.items():
            for level in range(1, 6):
                r = run_single(name, level, agents, tasks, trial=0)
                self.assertIn("net_business_value", r,
                              f"Failed for {name} L{level}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
