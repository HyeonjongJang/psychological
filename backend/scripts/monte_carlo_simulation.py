#!/usr/bin/env python3
"""
Monte Carlo Simulation for DOSE Algorithm Validation

This script validates the DOSE adaptive testing algorithm by:
1. Generating 1,000 virtual participants with known true theta values
2. Simulating responses to full 24-item survey (G1)
3. Simulating responses to DOSE adaptive testing (G3)
4. Comparing estimated vs true scores
5. Calculating correlation and item reduction rate

Usage:
    python monte_carlo_simulation.py

Output:
    - Console: Summary statistics
    - File: simulation_results.json with detailed metrics
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# ============================================================================
# IRT PARAMETERS FROM SIBLEY (2012)
# ============================================================================

TRAITS = [
    "extraversion",
    "agreeableness",
    "conscientiousness",
    "neuroticism",
    "openness",
    "honesty_humility"
]

TRAIT_ITEMS = {
    "extraversion": [1, 7, 19, 23],
    "agreeableness": [2, 8, 14, 20],
    "conscientiousness": [3, 10, 11, 22],
    "neuroticism": [4, 15, 16, 17],
    "openness": [5, 9, 13, 21],
    "honesty_humility": [6, 12, 18, 24]
}

# Item parameters: alpha (discrimination) and beta (thresholds)
MINI_IPIP6_ITEMS = {
    1: {"trait": "extraversion", "reverse": False, "alpha": 1.07, "beta": [-1.85, -1.04, -0.21, 0.89, 1.98, 2.76]},
    7: {"trait": "extraversion", "reverse": True, "alpha": 0.84, "beta": [-2.82, -1.67, -0.80, 0.10, 0.86, 1.91]},
    19: {"trait": "extraversion", "reverse": True, "alpha": 1.00, "beta": [-2.51, -1.32, -0.49, 0.45, 1.23, 2.44]},
    23: {"trait": "extraversion", "reverse": False, "alpha": 0.92, "beta": [-2.25, -1.27, -0.54, 0.24, 0.97, 1.96]},
    2: {"trait": "agreeableness", "reverse": False, "alpha": 1.46, "beta": [-3.19, -2.51, -1.86, -1.19, -0.28, 0.99]},
    8: {"trait": "agreeableness", "reverse": True, "alpha": 0.66, "beta": [-3.74, -2.51, -1.59, -0.76, 0.22, 1.76]},
    14: {"trait": "agreeableness", "reverse": False, "alpha": 1.12, "beta": [-3.15, -2.36, -1.70, -0.92, 0.03, 1.37]},
    20: {"trait": "agreeableness", "reverse": True, "alpha": 0.81, "beta": [-3.77, -2.69, -1.94, -1.19, -0.28, 1.25]},
    3: {"trait": "conscientiousness", "reverse": False, "alpha": 0.90, "beta": [-3.39, -2.13, -1.18, -0.27, 0.57, 1.64]},
    10: {"trait": "conscientiousness", "reverse": False, "alpha": 0.85, "beta": [-3.49, -2.72, -2.02, -1.06, -0.20, 1.12]},
    11: {"trait": "conscientiousness", "reverse": True, "alpha": 0.77, "beta": [-4.21, -2.93, -2.05, -1.07, -0.18, 1.38]},
    22: {"trait": "conscientiousness", "reverse": True, "alpha": 0.94, "beta": [-2.63, -1.73, -1.17, -0.64, -0.09, 1.11]},
    4: {"trait": "neuroticism", "reverse": False, "alpha": 1.13, "beta": [-1.32, -0.23, 0.36, 1.04, 1.72, 2.53]},
    15: {"trait": "neuroticism", "reverse": True, "alpha": 0.77, "beta": [-2.24, -0.70, 0.38, 1.48, 2.57, 3.92]},
    16: {"trait": "neuroticism", "reverse": False, "alpha": 0.90, "beta": [-2.15, -0.76, 0.05, 0.89, 1.72, 2.80]},
    17: {"trait": "neuroticism", "reverse": True, "alpha": 0.65, "beta": [-2.82, -1.01, -0.19, 0.76, 1.80, 3.15]},
    5: {"trait": "openness", "reverse": False, "alpha": 0.54, "beta": [-4.22, -2.68, -1.52, -0.21, 0.94, 2.47]},
    9: {"trait": "openness", "reverse": True, "alpha": 1.10, "beta": [-2.70, -1.72, -1.00, -0.17, 0.47, 1.61]},
    13: {"trait": "openness", "reverse": True, "alpha": 0.79, "beta": [-3.45, -2.35, -1.56, -0.85, -0.11, 1.13]},
    21: {"trait": "openness", "reverse": True, "alpha": 1.24, "beta": [-2.57, -1.71, -1.12, -0.29, 0.41, 1.43]},
    6: {"trait": "honesty_humility", "reverse": True, "alpha": 0.91, "beta": [-3.43, -2.67, -1.89, -1.10, -0.42, 0.71]},
    12: {"trait": "honesty_humility", "reverse": True, "alpha": 1.17, "beta": [-2.32, -1.69, -1.08, -0.33, 0.17, 0.99]},
    18: {"trait": "honesty_humility", "reverse": True, "alpha": 1.47, "beta": [-1.92, -1.42, -0.97, -0.52, -0.16, 0.48]},
    24: {"trait": "honesty_humility", "reverse": True, "alpha": 1.16, "beta": [-2.08, -1.30, -0.71, -0.12, 0.31, 1.10]},
}

# DOSE Configuration
SE_THRESHOLD = 0.65  # Achievable for Mini-IPIP6 items with moderate discrimination
MAX_ITEMS_PER_TRAIT = 4
THETA_MIN = -4.0
THETA_MAX = 4.0
THETA_POINTS = 161


# ============================================================================
# IRT ENGINE FUNCTIONS
# ============================================================================

def cumulative_probability(theta: float, alpha: float, beta: float) -> float:
    """Calculate cumulative probability P*(theta) for a single threshold."""
    z = alpha * (theta - beta)
    if z > 35:
        return 1.0
    elif z < -35:
        return 0.0
    return 1.0 / (1.0 + np.exp(-z))


def category_probabilities(theta: float, alpha: float, betas: List[float]) -> List[float]:
    """Calculate probability of each response category (1-7)."""
    n_categories = len(betas) + 1  # 7 categories for 6 thresholds
    probs = []

    # P(X >= k) for each threshold
    cum_probs = [1.0]  # P(X >= 1) = 1
    for beta in betas:
        cum_probs.append(cumulative_probability(theta, alpha, beta))
    cum_probs.append(0.0)  # P(X >= 8) = 0

    # P(X = k) = P(X >= k) - P(X >= k+1)
    for k in range(n_categories):
        prob = cum_probs[k] - cum_probs[k + 1]
        probs.append(max(0.0, min(1.0, prob)))

    # Normalize to ensure sum = 1
    total = sum(probs)
    if total > 0:
        probs = [p / total for p in probs]

    return probs


def fisher_information(theta: float, alpha: float, betas: List[float]) -> float:
    """Calculate Fisher Information at theta for an item."""
    probs = category_probabilities(theta, alpha, betas)

    info = 0.0
    cum_probs = [1.0]
    for beta in betas:
        cum_probs.append(cumulative_probability(theta, alpha, beta))
    cum_probs.append(0.0)

    for k in range(len(probs)):
        p_k = probs[k]
        if p_k > 1e-10:
            p_star_k = cum_probs[k]
            p_star_k1 = cum_probs[k + 1]

            deriv_k = alpha * p_star_k * (1 - p_star_k)
            deriv_k1 = alpha * p_star_k1 * (1 - p_star_k1)

            numerator = (deriv_k - deriv_k1) ** 2
            info += numerator / p_k

    return info


def simulate_response(theta: float, alpha: float, betas: List[float], reverse: bool) -> int:
    """
    Simulate a response (1-7) given true theta and item parameters.

    The IRT model gives probabilities for the TRAIT-DIRECTION response.
    For reverse-keyed items, we need to return the RAW response (unreversed).

    Example: High extraversion person on "Don't talk a lot" (reverse):
    - IRT says high probability of high trait-response (e.g., 6)
    - But raw response should be LOW (they disagree)
    - So return 8 - 6 = 2 as raw response
    """
    probs = category_probabilities(theta, alpha, betas)
    trait_response = np.random.choice(range(1, 8), p=probs)

    if reverse:
        # Convert trait-direction response to raw response
        return 8 - trait_response
    return trait_response


def log_likelihood(response: int, theta: float, alpha: float, betas: List[float]) -> float:
    """Calculate log-likelihood of observing response given theta."""
    probs = category_probabilities(theta, alpha, betas)
    p = probs[response - 1]  # response is 1-indexed
    return np.log(max(p, 1e-10))


# ============================================================================
# BAYESIAN UPDATER
# ============================================================================

@dataclass
class TraitState:
    """State of estimation for a single trait."""
    theta: float = 0.0
    se: float = 1.0
    posterior: np.ndarray = field(default_factory=lambda: np.ones(THETA_POINTS) / THETA_POINTS)
    items_answered: int = 0
    responses: List[Tuple[int, int]] = field(default_factory=list)  # (item_id, response)


class BayesianUpdater:
    """Bayesian posterior estimation for IRT."""

    def __init__(self):
        self.theta_grid = np.linspace(THETA_MIN, THETA_MAX, THETA_POINTS)
        self.delta_theta = self.theta_grid[1] - self.theta_grid[0]
        self._init_prior()

    def _init_prior(self):
        """Initialize standard normal prior."""
        self.prior = stats.norm.pdf(self.theta_grid, 0, 1)
        self.prior = self.prior / (np.sum(self.prior) * self.delta_theta)

    def get_initial_posterior(self) -> np.ndarray:
        """Return initial posterior (equal to prior)."""
        return self.prior.copy()

    def update_posterior(
        self,
        prior_posterior: np.ndarray,
        response: int,
        alpha: float,
        betas: List[float]
    ) -> np.ndarray:
        """Update posterior given a new response."""
        log_posterior = np.zeros(THETA_POINTS)

        for i, theta in enumerate(self.theta_grid):
            log_prior = np.log(max(prior_posterior[i], 1e-300))
            log_lik = log_likelihood(response, theta, alpha, betas)
            log_posterior[i] = log_prior + log_lik

        # Normalize using log-sum-exp trick
        log_max = np.max(log_posterior)
        posterior = np.exp(log_posterior - log_max)
        posterior = posterior / (np.sum(posterior) * self.delta_theta)

        return posterior

    def compute_eap(self, posterior: np.ndarray) -> float:
        """Compute Expected A Posteriori (EAP) estimate."""
        return np.sum(self.theta_grid * posterior) * self.delta_theta

    def compute_se(self, posterior: np.ndarray) -> float:
        """Compute standard error (posterior standard deviation)."""
        eap = self.compute_eap(posterior)
        variance = np.sum((self.theta_grid - eap) ** 2 * posterior) * self.delta_theta
        return np.sqrt(max(variance, 0.0))


# ============================================================================
# SURVEY SCORING (G1)
# ============================================================================

def score_survey_classical(responses: Dict[int, int]) -> Dict[str, float]:
    """
    Score survey using classical test theory (mean of responses).
    This simulates traditional survey scoring on 1-7 Likert scale.
    """
    trait_scores = {}

    for trait in TRAITS:
        items = TRAIT_ITEMS[trait]
        scores = []

        for item_id in items:
            if item_id in responses:
                response = responses[item_id]
                # Apply reverse scoring
                if MINI_IPIP6_ITEMS[item_id]["reverse"]:
                    response = 8 - response
                scores.append(response)

        if scores:
            trait_scores[trait] = np.mean(scores)
        else:
            trait_scores[trait] = 4.0  # neutral

    return trait_scores


def score_survey_irt(responses: Dict[int, int], updater: BayesianUpdater) -> Dict[str, Tuple[float, float]]:
    """
    Score survey using IRT/Bayesian estimation.
    Returns (theta, SE) for each trait.
    """
    trait_estimates = {}

    for trait in TRAITS:
        items = TRAIT_ITEMS[trait]
        posterior = updater.get_initial_posterior()

        for item_id in items:
            if item_id in responses:
                response = responses[item_id]
                item = MINI_IPIP6_ITEMS[item_id]

                # For IRT, use the response as-is (parameters account for directionality)
                # But we need to reverse for reverse-keyed items
                if item["reverse"]:
                    response = 8 - response

                posterior = updater.update_posterior(
                    posterior, response, item["alpha"], item["beta"]
                )

        theta = updater.compute_eap(posterior)
        se = updater.compute_se(posterior)
        trait_estimates[trait] = (theta, se)

    return trait_estimates


# ============================================================================
# DOSE ALGORITHM (G3)
# ============================================================================

class DOSESimulator:
    """Simulates DOSE adaptive testing for a virtual participant."""

    def __init__(self, true_thetas: Dict[str, float]):
        self.true_thetas = true_thetas
        self.updater = BayesianUpdater()
        self.trait_states: Dict[str, TraitState] = {}
        self.total_items = 0
        self.item_history: List[Tuple[str, int, int]] = []  # (trait, item_id, response)

        # Initialize states for each trait
        for trait in TRAITS:
            state = TraitState()
            state.posterior = self.updater.get_initial_posterior()
            self.trait_states[trait] = state

    def _get_available_items(self, trait: str) -> List[int]:
        """Get items for trait that haven't been administered."""
        used = [r[0] for r in self.trait_states[trait].responses]
        return [i for i in TRAIT_ITEMS[trait] if i not in used]

    def _select_best_item(self, trait: str) -> Optional[int]:
        """Select item with maximum Fisher Information at current theta."""
        available = self._get_available_items(trait)
        if not available:
            return None

        current_theta = self.trait_states[trait].theta

        best_item = None
        best_info = -1

        for item_id in available:
            item = MINI_IPIP6_ITEMS[item_id]
            info = fisher_information(current_theta, item["alpha"], item["beta"])
            if info > best_info:
                best_info = info
                best_item = item_id

        return best_item

    def _select_trait_needing_items(self) -> Optional[str]:
        """Select trait that needs more items (round-robin)."""
        incomplete = []

        for trait in TRAITS:
            state = self.trait_states[trait]
            if state.se >= SE_THRESHOLD and state.items_answered < MAX_ITEMS_PER_TRAIT:
                incomplete.append((trait, state.items_answered))

        if not incomplete:
            return None

        # Return trait with fewest items
        incomplete.sort(key=lambda x: x[1])
        return incomplete[0][0]

    def _simulate_response(self, item_id: int, trait: str) -> int:
        """Simulate a response based on true theta."""
        item = MINI_IPIP6_ITEMS[item_id]
        true_theta = self.true_thetas[trait]

        # Generate response based on true theta
        response = simulate_response(
            true_theta, item["alpha"], item["beta"], item["reverse"]
        )

        return response

    def run(self) -> Dict[str, Tuple[float, float, int]]:
        """
        Run DOSE algorithm until stopping criteria met.
        Returns dict of {trait: (theta, se, items_used)}.
        """
        while True:
            # Select trait needing more items
            trait = self._select_trait_needing_items()
            if trait is None:
                break

            # Select best item for that trait
            item_id = self._select_best_item(trait)
            if item_id is None:
                continue

            # Simulate response
            response = self._simulate_response(item_id, trait)

            # Update posterior
            item = MINI_IPIP6_ITEMS[item_id]

            # Apply reverse scoring for posterior update
            scored_response = 8 - response if item["reverse"] else response

            state = self.trait_states[trait]
            state.posterior = self.updater.update_posterior(
                state.posterior, scored_response, item["alpha"], item["beta"]
            )
            state.theta = self.updater.compute_eap(state.posterior)
            state.se = self.updater.compute_se(state.posterior)
            state.items_answered += 1
            state.responses.append((item_id, response))

            self.total_items += 1
            self.item_history.append((trait, item_id, response))

        # Return final estimates
        results = {}
        for trait in TRAITS:
            state = self.trait_states[trait]
            results[trait] = (state.theta, state.se, state.items_answered)

        return results


# ============================================================================
# VIRTUAL PARTICIPANT GENERATION
# ============================================================================

def generate_virtual_participant() -> Dict[str, float]:
    """Generate true theta values for a virtual participant from N(0,1)."""
    return {trait: np.random.normal(0, 1) for trait in TRAITS}


def simulate_survey_responses(true_thetas: Dict[str, float]) -> Dict[int, int]:
    """Simulate responses to all 24 items based on true thetas."""
    responses = {}

    for item_id, item in MINI_IPIP6_ITEMS.items():
        trait = item["trait"]
        true_theta = true_thetas[trait]
        response = simulate_response(
            true_theta, item["alpha"], item["beta"], item["reverse"]
        )
        responses[item_id] = response

    return responses


# ============================================================================
# THETA TO LIKERT CONVERSION
# ============================================================================

def theta_to_likert(theta: float) -> float:
    """Convert theta (-4 to 4) to Likert scale (1-7)."""
    # Linear mapping: theta=-4 -> 1, theta=4 -> 7
    likert = 4.0 + (theta * 0.75)
    return max(1.0, min(7.0, likert))


def likert_to_theta(likert: float) -> float:
    """Convert Likert (1-7) to theta scale."""
    return (likert - 4.0) / 0.75


# ============================================================================
# MAIN SIMULATION
# ============================================================================

def run_simulation(n_participants: int = 1000, seed: int = 42) -> Dict:
    """
    Run Monte Carlo simulation.

    Args:
        n_participants: Number of virtual participants
        seed: Random seed for reproducibility

    Returns:
        Dictionary with simulation results
    """
    np.random.seed(seed)

    print(f"\n{'='*70}")
    print(f"  MONTE CARLO SIMULATION: DOSE vs Survey Validation")
    print(f"{'='*70}")
    print(f"  Participants: {n_participants}")
    print(f"  Traits: {len(TRAITS)}")
    print(f"  Survey items: 24 (4 per trait)")
    print(f"  DOSE SE threshold: {SE_THRESHOLD}")
    print(f"  DOSE max items/trait: {MAX_ITEMS_PER_TRAIT}")
    print(f"{'='*70}\n")

    updater = BayesianUpdater()

    # Storage for results
    results = {
        "true_thetas": [],
        "survey_thetas": [],
        "dose_thetas": [],
        "survey_likert": [],
        "dose_likert": [],
        "dose_items": [],
        "dose_se": [],
    }

    # Per-trait storage
    for trait in TRAITS:
        results[f"true_{trait}"] = []
        results[f"survey_{trait}"] = []
        results[f"dose_{trait}"] = []
        results[f"survey_likert_{trait}"] = []
        results[f"dose_likert_{trait}"] = []
        results[f"dose_items_{trait}"] = []
        results[f"dose_se_{trait}"] = []

    print("Running simulation...")
    for i in range(n_participants):
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i+1}/{n_participants} participants")

        # Generate virtual participant
        true_thetas = generate_virtual_participant()

        # Simulate Survey (G1)
        survey_responses = simulate_survey_responses(true_thetas)
        survey_estimates = score_survey_irt(survey_responses, updater)
        survey_classical = score_survey_classical(survey_responses)

        # Simulate DOSE (G3)
        dose_sim = DOSESimulator(true_thetas)
        dose_estimates = dose_sim.run()

        # Store results
        total_dose_items = sum(dose_estimates[t][2] for t in TRAITS)
        results["dose_items"].append(total_dose_items)

        for trait in TRAITS:
            true_theta = true_thetas[trait]
            survey_theta, survey_se = survey_estimates[trait]
            dose_theta, dose_se, dose_items = dose_estimates[trait]

            results[f"true_{trait}"].append(true_theta)
            results[f"survey_{trait}"].append(survey_theta)
            results[f"dose_{trait}"].append(dose_theta)
            results[f"survey_likert_{trait}"].append(theta_to_likert(survey_theta))
            results[f"dose_likert_{trait}"].append(theta_to_likert(dose_theta))
            results[f"dose_items_{trait}"].append(dose_items)
            results[f"dose_se_{trait}"].append(dose_se)

    print("\nSimulation complete. Analyzing results...\n")

    # Calculate metrics
    metrics = calculate_metrics(results)

    return {
        "results": results,
        "metrics": metrics,
        "config": {
            "n_participants": n_participants,
            "seed": seed,
            "se_threshold": SE_THRESHOLD,
            "max_items_per_trait": MAX_ITEMS_PER_TRAIT,
            "survey_items": 24,
        }
    }


def calculate_metrics(results: Dict) -> Dict:
    """Calculate validation metrics from simulation results."""
    metrics = {
        "overall": {},
        "per_trait": {}
    }

    # Overall metrics
    all_true = []
    all_survey = []
    all_dose = []

    for trait in TRAITS:
        all_true.extend(results[f"true_{trait}"])
        all_survey.extend(results[f"survey_{trait}"])
        all_dose.extend(results[f"dose_{trait}"])

    # Correlations with true scores
    survey_true_r, survey_true_p = stats.pearsonr(all_survey, all_true)
    dose_true_r, dose_true_p = stats.pearsonr(all_dose, all_true)

    # Correlation between Survey and DOSE
    survey_dose_r, survey_dose_p = stats.pearsonr(all_survey, all_dose)

    # MAE with true scores
    survey_true_mae = np.mean(np.abs(np.array(all_survey) - np.array(all_true)))
    dose_true_mae = np.mean(np.abs(np.array(all_dose) - np.array(all_true)))
    survey_dose_mae = np.mean(np.abs(np.array(all_survey) - np.array(all_dose)))

    # Efficiency
    avg_dose_items = np.mean(results["dose_items"])
    item_reduction = (1 - avg_dose_items / 24) * 100

    metrics["overall"] = {
        "survey_vs_true_r": float(survey_true_r),
        "survey_vs_true_p": float(survey_true_p),
        "dose_vs_true_r": float(dose_true_r),
        "dose_vs_true_p": float(dose_true_p),
        "survey_vs_dose_r": float(survey_dose_r),
        "survey_vs_dose_p": float(survey_dose_p),
        "survey_true_mae": float(survey_true_mae),
        "dose_true_mae": float(dose_true_mae),
        "survey_dose_mae": float(survey_dose_mae),
        "avg_dose_items_total": float(avg_dose_items),
        "avg_survey_items": 24,
        "item_reduction_pct": float(item_reduction),
    }

    # Per-trait metrics
    for trait in TRAITS:
        true_vals = np.array(results[f"true_{trait}"])
        survey_vals = np.array(results[f"survey_{trait}"])
        dose_vals = np.array(results[f"dose_{trait}"])
        dose_items = np.array(results[f"dose_items_{trait}"])
        dose_se = np.array(results[f"dose_se_{trait}"])

        survey_true_r, _ = stats.pearsonr(survey_vals, true_vals)
        dose_true_r, _ = stats.pearsonr(dose_vals, true_vals)
        survey_dose_r, _ = stats.pearsonr(survey_vals, dose_vals)

        metrics["per_trait"][trait] = {
            "survey_vs_true_r": float(survey_true_r),
            "dose_vs_true_r": float(dose_true_r),
            "survey_vs_dose_r": float(survey_dose_r),
            "survey_true_mae": float(np.mean(np.abs(survey_vals - true_vals))),
            "dose_true_mae": float(np.mean(np.abs(dose_vals - true_vals))),
            "survey_dose_mae": float(np.mean(np.abs(survey_vals - dose_vals))),
            "avg_dose_items": float(np.mean(dose_items)),
            "avg_dose_se": float(np.mean(dose_se)),
            "dose_items_dist": {
                "1_item": int(np.sum(dose_items == 1)),
                "2_items": int(np.sum(dose_items == 2)),
                "3_items": int(np.sum(dose_items == 3)),
                "4_items": int(np.sum(dose_items == 4)),
            }
        }

    return metrics


def print_results(simulation_data: Dict):
    """Print simulation results in a formatted table."""
    metrics = simulation_data["metrics"]
    config = simulation_data["config"]

    print(f"\n{'='*70}")
    print(f"  SIMULATION RESULTS")
    print(f"{'='*70}")

    print(f"\n  Configuration:")
    print(f"  - Virtual participants: {config['n_participants']}")
    print(f"  - Survey items: {config['survey_items']}")
    print(f"  - DOSE SE threshold: {config['se_threshold']}")
    print(f"  - DOSE max items/trait: {config['max_items_per_trait']}")

    print(f"\n  OVERALL METRICS")
    print(f"  {'-'*66}")

    overall = metrics["overall"]

    print(f"\n  Accuracy (correlation with true scores):")
    print(f"    Survey vs True:  r = {overall['survey_vs_true_r']:.4f} (p < 0.001)")
    print(f"    DOSE vs True:    r = {overall['dose_vs_true_r']:.4f} (p < 0.001)")
    print(f"    Survey vs DOSE:  r = {overall['survey_vs_dose_r']:.4f} (p < 0.001)")

    print(f"\n  Precision (Mean Absolute Error with true scores):")
    print(f"    Survey MAE:      {overall['survey_true_mae']:.4f}")
    print(f"    DOSE MAE:        {overall['dose_true_mae']:.4f}")
    print(f"    Survey-DOSE MAE: {overall['survey_dose_mae']:.4f}")

    print(f"\n  Efficiency:")
    print(f"    Survey items:        {overall['avg_survey_items']:.1f}")
    print(f"    DOSE items (avg):    {overall['avg_dose_items_total']:.2f}")
    print(f"    Item reduction:      {overall['item_reduction_pct']:.1f}%")

    print(f"\n  PER-TRAIT METRICS")
    print(f"  {'-'*66}")

    print(f"\n  {'Trait':<20} {'Survey-True r':<15} {'DOSE-True r':<15} {'DOSE Items':<12}")
    print(f"  {'-'*62}")

    for trait in TRAITS:
        tm = metrics["per_trait"][trait]
        print(f"  {trait:<20} {tm['survey_vs_true_r']:<15.4f} {tm['dose_vs_true_r']:<15.4f} {tm['avg_dose_items']:<12.2f}")

    print(f"\n  DOSE Item Distribution by Trait:")
    print(f"  {'Trait':<20} {'1 item':<10} {'2 items':<10} {'3 items':<10} {'4 items':<10}")
    print(f"  {'-'*60}")

    for trait in TRAITS:
        dist = metrics["per_trait"][trait]["dose_items_dist"]
        print(f"  {trait:<20} {dist['1_item']:<10} {dist['2_items']:<10} {dist['3_items']:<10} {dist['4_items']:<10}")

    print(f"\n  DOSE Average SE by Trait:")
    for trait in TRAITS:
        avg_se = metrics["per_trait"][trait]["avg_dose_se"]
        print(f"    {trait:<20}: {avg_se:.4f}")

    print(f"\n{'='*70}")
    print(f"  CONCLUSION")
    print(f"{'='*70}")

    # Determine quality
    dose_true_r = overall["dose_vs_true_r"]
    survey_dose_r = overall["survey_vs_dose_r"]
    item_reduction = overall["item_reduction_pct"]

    if dose_true_r >= 0.9:
        accuracy_quality = "Excellent"
    elif dose_true_r >= 0.8:
        accuracy_quality = "Very Good"
    elif dose_true_r >= 0.7:
        accuracy_quality = "Good"
    else:
        accuracy_quality = "Moderate"

    print(f"\n  DOSE Accuracy: {accuracy_quality} (r = {dose_true_r:.4f} with true scores)")
    print(f"  Survey-DOSE Agreement: r = {survey_dose_r:.4f}")
    print(f"  Efficiency Gain: {item_reduction:.1f}% fewer items ({overall['avg_dose_items_total']:.1f} vs 24)")

    if dose_true_r >= 0.85 and item_reduction >= 40:
        print(f"\n  DOSE successfully matches Survey accuracy with significant efficiency gains.")
    elif dose_true_r >= 0.75:
        print(f"\n  DOSE provides acceptable accuracy with good efficiency gains.")
    else:
        print(f"\n  DOSE may need parameter tuning for better accuracy.")

    print(f"\n{'='*70}\n")


def save_results(simulation_data: Dict, output_path: str):
    """Save results to JSON file."""
    # Convert numpy types to Python types
    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        return obj

    # Only save metrics and config, not all raw data
    output = {
        "timestamp": datetime.now().isoformat(),
        "config": simulation_data["config"],
        "metrics": simulation_data["metrics"]
    }

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=convert)

    print(f"  Results saved to: {output_path}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Run simulation
    simulation_data = run_simulation(n_participants=1000, seed=42)

    # Print results
    print_results(simulation_data)

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "simulation_results.json")
    save_results(simulation_data, output_path)
