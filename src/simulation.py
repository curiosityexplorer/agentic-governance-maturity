"""
AAGMM Simulation Engine
========================
Core simulation framework for the Agentic AI Governance Maturity Model (AAGMM).

Simulates enterprise multi-agent environments under five governance maturity levels
(Ad-hoc, Reactive, Defined, Managed, Optimized) across 12 governance domains.

Measures:
    - Sprawl Index (SI)
    - Risk Incident Rate (RIR)
    - Effective Task Completion Rate (ETCR)
    - Governance Cost Ratio (GCR)
    - Delegation Safety Rate (DSR)
    - Net Business Value (NBV)

Reference:
    Acharya, V. (2026). "Governing the Agentic Enterprise: A Governance Maturity
    Model for Managing AI Agent Sprawl in Business Operations." AI (MDPI).

License: Apache 2.0
"""

import random
import math
import json
import csv
import os
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

__version__ = "1.0.0"
__author__ = "Vivek Acharya"

SEED = 42


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Agent:
    """Represents a single AI agent in the enterprise simulation."""
    agent_id: str
    function: str
    capability: str
    registered: bool = False
    has_identity: bool = False
    scoped_permissions: bool = False
    observable: bool = False
    policy_enforced: bool = False
    lifecycle_managed: bool = False
    is_shadow: bool = False
    is_orphaned: bool = False
    is_duplicate: bool = False
    risk_tier: int = 0  # 0=unclassified, 1=low, 2=medium, 3=high
    actions_taken: int = 0
    violations: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0


@dataclass
class GovernanceConfig:
    """Configuration for a governance maturity level."""
    level: int
    name: str
    agent_registry: bool = False
    identity_management: bool = False
    access_control_scoped: bool = False
    observability: bool = False
    policy_enforcement: bool = False
    automated_policy: bool = False
    hitl_breakpoints: bool = False
    sprawl_detection: bool = False
    audit_trails: bool = False
    risk_classification: bool = False
    incident_response: bool = False
    lifecycle_automation: bool = False
    continuous_improvement: bool = False
    predictive_sprawl: bool = False
    governance_as_code: bool = False


# ============================================================
# CONSTANTS
# ============================================================

GOVERNANCE_LEVELS = {
    1: GovernanceConfig(1, "Ad-hoc"),
    2: GovernanceConfig(2, "Reactive",
        agent_registry=True, incident_response=True),
    3: GovernanceConfig(3, "Defined",
        agent_registry=True, identity_management=True,
        access_control_scoped=True, observability=True,
        policy_enforcement=True, hitl_breakpoints=True,
        audit_trails=True, risk_classification=True,
        incident_response=True),
    4: GovernanceConfig(4, "Managed",
        agent_registry=True, identity_management=True,
        access_control_scoped=True, observability=True,
        policy_enforcement=True, automated_policy=True,
        hitl_breakpoints=True, sprawl_detection=True,
        audit_trails=True, risk_classification=True,
        incident_response=True, lifecycle_automation=True),
    5: GovernanceConfig(5, "Optimized",
        agent_registry=True, identity_management=True,
        access_control_scoped=True, observability=True,
        policy_enforcement=True, automated_policy=True,
        hitl_breakpoints=True, sprawl_detection=True,
        audit_trails=True, risk_classification=True,
        incident_response=True, lifecycle_automation=True,
        continuous_improvement=True, predictive_sprawl=True,
        governance_as_code=True),
}

BUSINESS_FUNCTIONS = [
    "customer_service", "finance", "hr", "it_ops", "supply_chain"
]

AGENT_CAPABILITIES = {
    "customer_service": [
        "ticket_routing", "sentiment_analysis", "response_generation",
        "escalation_handler", "faq_responder", "feedback_collector"
    ],
    "finance": [
        "invoice_processing", "expense_approval", "financial_reporting",
        "fraud_detection", "budget_forecasting", "payment_reconciliation"
    ],
    "hr": [
        "resume_screening", "onboarding_assistant", "leave_management",
        "performance_review", "training_recommender", "policy_qa"
    ],
    "it_ops": [
        "incident_triage", "log_analysis", "deployment_automation",
        "access_provisioning", "monitoring_alerter", "patch_management"
    ],
    "supply_chain": [
        "demand_forecasting", "inventory_optimizer", "supplier_evaluator",
        "order_tracking", "logistics_planner", "quality_inspector"
    ],
}

TASK_DIFFICULTIES = {
    "simple": 0.40,
    "moderate": 0.35,
    "complex": 0.20,
    "critical": 0.05,
}

SHADOW_PROBABILITIES = {1: 0.35, 2: 0.25, 3: 0.12, 4: 0.05, 5: 0.02}
ORPHAN_RATES = {1: 0.15, 2: 0.10, 3: 0.06, 4: 0.03, 5: 0.01}
BASE_GOVERNANCE_COSTS = {1: 0.02, 2: 0.06, 3: 0.12, 4: 0.18, 5: 0.16}
TTV_BASE = {1: 2, 2: 5, 3: 10, 4: 14, 5: 12}
REWORK_MULTIPLIER = {1: 2.5, 2: 1.8, 3: 1.2, 4: 1.05, 5: 1.0}

VIOLATION_TYPES = [
    "data_boundary", "permission_exceed", "compliance_gap",
    "unauthorized_action", "pii_exposure"
]
VIOLATION_WEIGHTS = [0.25, 0.20, 0.25, 0.15, 0.15]


# ============================================================
# SIMULATION ENGINE
# ============================================================

class EnterpriseSimulation:
    """
    Simulates an enterprise multi-agent environment under a specific
    governance maturity level and scenario configuration.

    Parameters
    ----------
    governance_level : int
        AAGMM maturity level (1-5).
    scenario : str
        Scenario name (greenfield, scaling, cross_functional, adversarial, optimization).
    num_agents : int
        Number of base agents to deploy.
    num_tasks : int
        Number of tasks to simulate.
    seed : int
        Random seed for reproducibility.
    """

    def __init__(self, governance_level: int, scenario: str,
                 num_agents: int = 30, num_tasks: int = 1000,
                 seed: int = SEED):
        self.rng = random.Random(seed + governance_level * 100 + hash(scenario) % 1000)
        self.gov = GOVERNANCE_LEVELS[governance_level]
        self.scenario = scenario
        self.num_agents = num_agents
        self.num_tasks = num_tasks
        self.agents: List[Agent] = []
        self.metrics: Dict = {}
        self.violations_log: List[Dict] = []
        self.delegation_chains: List[Dict] = []

    def deploy_agents(self) -> None:
        """Deploy agents with sprawl characteristics based on governance level."""
        agent_id = 0
        for func in BUSINESS_FUNCTIONS:
            base_count = self.num_agents // len(BUSINESS_FUNCTIONS)
            caps = AGENT_CAPABILITIES[func]
            for i in range(base_count):
                cap = caps[i % len(caps)]
                agent = Agent(agent_id=f"agent_{agent_id:03d}",
                              function=func, capability=cap)
                self._apply_governance(agent)
                self._apply_sprawl_characteristics(agent, func, cap)
                self.agents.append(agent)
                agent_id += 1

        # Shadow agents
        num_shadows = int(self.num_agents * SHADOW_PROBABILITIES[self.gov.level])
        for _ in range(num_shadows):
            func = self.rng.choice(BUSINESS_FUNCTIONS)
            cap = self.rng.choice(AGENT_CAPABILITIES[func])
            agent = Agent(agent_id=f"shadow_{agent_id:03d}",
                          function=func, capability=cap, is_shadow=True)
            self.agents.append(agent)
            agent_id += 1

    def _apply_governance(self, agent: Agent) -> None:
        """Apply governance controls to an agent based on maturity level."""
        if self.gov.agent_registry:
            agent.registered = True
        if self.gov.identity_management:
            agent.has_identity = True
        if self.gov.access_control_scoped:
            agent.scoped_permissions = True
        if self.gov.observability:
            agent.observable = True
        if self.gov.policy_enforcement:
            agent.policy_enforced = True
        if self.gov.lifecycle_automation:
            agent.lifecycle_managed = True
        if self.gov.risk_classification:
            agent.risk_tier = self.rng.choice([1, 2, 2, 3])

    def _apply_sprawl_characteristics(self, agent: Agent,
                                      func: str, cap: str) -> None:
        """Determine if agent is a duplicate; governance may prevent it."""
        existing_caps = [(a.function, a.capability)
                         for a in self.agents if not a.is_shadow]
        if (func, cap) in existing_caps:
            if self.gov.sprawl_detection:
                if self.rng.random() < 0.85:
                    return
            elif self.gov.agent_registry:
                if self.rng.random() < 0.30:
                    return
            agent.is_duplicate = True

    def orphan_agents(self) -> None:
        """Simulate agent orphaning over time."""
        orphan_rate = ORPHAN_RATES[self.gov.level]
        for agent in self.agents:
            if self.rng.random() < orphan_rate:
                agent.is_orphaned = True
                if self.gov.lifecycle_automation and self.rng.random() < 0.80:
                    agent.is_orphaned = False

    def run_tasks(self) -> None:
        """Execute task workload across all active agents."""
        active_agents = [a for a in self.agents if not a.is_orphaned]
        if not active_agents:
            return

        for task_idx in range(self.num_tasks):
            diff = self._sample_difficulty()
            agent = self.rng.choice(active_agents)
            success, violation = self._execute_task(agent, diff, task_idx)
            agent.actions_taken += 1

            if success:
                agent.tasks_completed += 1
            else:
                agent.tasks_failed += 1

            if violation:
                agent.violations += 1
                self.violations_log.append({
                    "task_idx": task_idx,
                    "agent_id": agent.agent_id,
                    "difficulty": diff,
                    "violation_type": violation,
                })

            # Inter-agent delegation for complex/critical tasks
            if diff in ["complex", "critical"] and self.rng.random() < 0.4:
                delegate = self.rng.choice(active_agents)
                chain_safe = self._check_delegation(agent, delegate)
                self.delegation_chains.append({
                    "from": agent.agent_id,
                    "to": delegate.agent_id,
                    "safe": chain_safe,
                    "task_idx": task_idx,
                })

    def _sample_difficulty(self) -> str:
        """Sample task difficulty from the defined distribution."""
        r = self.rng.random()
        cumulative = 0.0
        for diff, prob in TASK_DIFFICULTIES.items():
            cumulative += prob
            if r <= cumulative:
                return diff
        return "simple"

    def _execute_task(self, agent: Agent, difficulty: str,
                      task_idx: int) -> Tuple[bool, Optional[str]]:
        """Execute a task; return (success, violation_type_or_None)."""
        base_success = {
            "simple": 0.92, "moderate": 0.80,
            "complex": 0.65, "critical": 0.50
        }[difficulty]

        gov_bonus = 0.0
        if agent.policy_enforced:
            gov_bonus += 0.05
        if agent.observable:
            gov_bonus += 0.03
        if agent.scoped_permissions:
            gov_bonus += 0.04
        if self.gov.continuous_improvement:
            gov_bonus += 0.03
        if self.gov.governance_as_code:
            gov_bonus += 0.02
        if agent.is_shadow:
            gov_bonus -= 0.15
        if agent.is_duplicate:
            gov_bonus -= 0.05

        success_prob = min(0.99, max(0.10, base_success + gov_bonus))
        success = self.rng.random() < success_prob

        # Violation probability
        base_violation = {
            "simple": 0.02, "moderate": 0.05,
            "complex": 0.10, "critical": 0.18
        }[difficulty]

        violation_reduction = 0.0
        if agent.policy_enforced:
            violation_reduction += 0.40
        if agent.scoped_permissions:
            violation_reduction += 0.25
        if self.gov.automated_policy:
            violation_reduction += 0.20
        if self.gov.audit_trails:
            violation_reduction += 0.10
        if agent.is_shadow:
            violation_reduction -= 0.30

        effective_rate = base_violation * max(0.05, 1 - violation_reduction)
        violation = None
        if self.rng.random() < effective_rate:
            violation = self.rng.choices(VIOLATION_TYPES,
                                         weights=VIOLATION_WEIGHTS)[0]
            if self.gov.incident_response and self.rng.random() < 0.3:
                violation = None

        return success, violation

    def _check_delegation(self, source: Agent, target: Agent) -> bool:
        """Check whether a delegation chain is safe."""
        if self.gov.level >= 4:
            return (source.scoped_permissions and
                    target.scoped_permissions and not target.is_shadow)
        elif self.gov.level >= 3:
            return not target.is_shadow
        else:
            return self.rng.random() < 0.6

    def compute_metrics(self) -> Dict:
        """Compute all business outcome metrics."""
        total_agents = len(self.agents)
        shadow_agents = [a for a in self.agents if a.is_shadow]
        duplicate_agents = [a for a in self.agents if a.is_duplicate]
        orphaned_agents = [a for a in self.agents if a.is_orphaned]

        total_actions = sum(a.actions_taken for a in self.agents)
        total_completed = sum(a.tasks_completed for a in self.agents)
        total_failed = sum(a.tasks_failed for a in self.agents)
        total_violations = sum(a.violations for a in self.agents)

        # Sprawl Index
        si = (len(shadow_agents) + len(duplicate_agents) +
              len(orphaned_agents)) / max(1, total_agents)

        # Risk Incident Rate (per 1000 actions)
        rir = (total_violations / max(1, total_actions)) * 1000

        # Effective Task Completion Rate
        effective = max(0, total_completed - total_violations)
        etcr = effective / max(1, self.num_tasks)

        # Governance Cost Ratio
        gcr = BASE_GOVERNANCE_COSTS[self.gov.level]

        # Time-to-Value
        ttv = TTV_BASE[self.gov.level] * REWORK_MULTIPLIER[self.gov.level]

        # Delegation Safety Rate
        safe_del = sum(1 for d in self.delegation_chains if d["safe"])
        total_del = len(self.delegation_chains)
        dsr = safe_del / max(1, total_del)

        # Net Business Value (composite)
        norm_rir = min(1.0, rir / 100)
        nbv = (0.30 * etcr + 0.20 * (1 - si) + 0.20 * (1 - norm_rir) +
               0.15 * dsr + 0.15 * (1 - gcr))

        self.metrics = {
            "governance_level": self.gov.level,
            "governance_name": self.gov.name,
            "scenario": self.scenario,
            "total_agents": total_agents,
            "active_agents": total_agents - len(orphaned_agents),
            "shadow_agents": len(shadow_agents),
            "duplicate_agents": len(duplicate_agents),
            "orphaned_agents": len(orphaned_agents),
            "sprawl_index": round(si, 4),
            "total_actions": total_actions,
            "total_completed": total_completed,
            "total_failed": total_failed,
            "total_violations": total_violations,
            "risk_incident_rate": round(rir, 2),
            "effective_task_completion": round(etcr, 4),
            "governance_cost_ratio": round(gcr, 4),
            "time_to_value_days": round(ttv, 1),
            "delegation_safety_rate": round(dsr, 4),
            "total_delegations": total_del,
            "safe_delegations": safe_del,
            "net_business_value": round(nbv, 4),
        }
        return self.metrics


def run_single(scenario: str, gov_level: int, num_agents: int,
               num_tasks: int, trial: int) -> Dict:
    """Run a single simulation trial."""
    sim = EnterpriseSimulation(
        governance_level=gov_level, scenario=scenario,
        num_agents=num_agents, num_tasks=num_tasks,
        seed=SEED + trial * 7919
    )
    sim.deploy_agents()
    sim.orphan_agents()
    sim.run_tasks()
    metrics = sim.compute_metrics()
    metrics["trial"] = trial
    return metrics
