"""
Bayesian Posterior Updater for Trait Estimation.

Implements Bayesian inference for updating trait estimates after each
response in the DOSE adaptive testing algorithm.

Prior: N(0, 1) - Standard normal distribution
Posterior: Updated using Bayes' theorem after each response
"""

import numpy as np
from scipy.stats import norm
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

from .irt_engine import IRTEngine, irt_engine
from ..core.mini_ipip6_data import MINI_IPIP6_ITEMS, TRAITS


@dataclass
class TraitState:
    """State for tracking a single trait's estimation."""
    trait: str
    theta_estimate: float = 0.0
    standard_error: float = 1.0
    posterior_mean: float = 0.0
    posterior_sd: float = 1.0
    responses: List[Tuple[int, int]] = field(default_factory=list)  # (item_number, response)
    items_used: List[int] = field(default_factory=list)
    total_information: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "trait": self.trait,
            "theta_estimate": self.theta_estimate,
            "standard_error": self.standard_error,
            "posterior_mean": self.posterior_mean,
            "posterior_sd": self.posterior_sd,
            "responses": self.responses,
            "items_used": self.items_used,
            "total_information": self.total_information,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "TraitState":
        """Reconstruct TraitState from dictionary."""
        return cls(
            trait=data["trait"],
            theta_estimate=data["theta_estimate"],
            standard_error=data["standard_error"],
            posterior_mean=data.get("posterior_mean", data["theta_estimate"]),
            posterior_sd=data.get("posterior_sd", data["standard_error"]),
            responses=[tuple(r) for r in data.get("responses", [])],
            items_used=data.get("items_used", []),
            total_information=data.get("total_information", 0.0),
        )


class BayesianUpdater:
    """
    Bayesian updater for trait estimation using posterior updates.

    Uses grid-based numerical integration for posterior computation.
    """

    def __init__(
        self,
        irt: IRTEngine = None,
        prior_mean: float = 0.0,
        prior_sd: float = 1.0,
        theta_min: float = -4.0,
        theta_max: float = 4.0,
        grid_points: int = 200
    ):
        """
        Initialize Bayesian updater.

        Args:
            irt: IRT engine instance
            prior_mean: Mean of prior distribution
            prior_sd: Standard deviation of prior
            theta_min: Minimum theta for grid
            theta_max: Maximum theta for grid
            grid_points: Number of grid points for integration
        """
        self.irt = irt or irt_engine
        self.prior_mean = prior_mean
        self.prior_sd = prior_sd

        # Theta grid for numerical integration
        self.theta_grid = np.linspace(theta_min, theta_max, grid_points)
        self.theta_step = self.theta_grid[1] - self.theta_grid[0]

    def initialize_trait_states(self) -> Dict[str, TraitState]:
        """
        Initialize state for all traits with N(0,1) prior.

        Returns:
            Dictionary mapping trait names to TraitState objects
        """
        return {
            trait: TraitState(
                trait=trait,
                theta_estimate=self.prior_mean,
                standard_error=self.prior_sd,
                posterior_mean=self.prior_mean,
                posterior_sd=self.prior_sd,
            )
            for trait in TRAITS
        }

    def prior_density(self, theta: float) -> float:
        """
        Calculate prior density at theta.

        Args:
            theta: Trait level

        Returns:
            Prior density value
        """
        return norm.pdf(theta, loc=self.prior_mean, scale=self.prior_sd)

    def log_prior(self, theta: float) -> float:
        """
        Calculate log prior density.

        Args:
            theta: Trait level

        Returns:
            Log prior density
        """
        return norm.logpdf(theta, loc=self.prior_mean, scale=self.prior_sd)

    def compute_posterior(
        self,
        responses: List[Tuple[int, int]],
        trait: str
    ) -> Tuple[np.ndarray, float, float]:
        """
        Compute posterior distribution for a trait given responses.

        Uses Bayes' theorem:
        P(theta | responses) proportional to P(responses | theta) * P(theta)

        Args:
            responses: List of (item_number, response_value) tuples
            trait: Trait name

        Returns:
            Tuple of (posterior_density_array, posterior_mean, posterior_sd)
        """
        # Initialize log posterior with log prior
        log_posterior = np.zeros_like(self.theta_grid)

        for theta_idx, theta in enumerate(self.theta_grid):
            # Log prior
            log_prior = self.log_prior(theta)

            # Log likelihood (sum over all responses)
            log_lik = 0.0
            for item_num, response in responses:
                item = MINI_IPIP6_ITEMS[item_num]

                # Handle reverse scoring for likelihood calculation
                effective_response = response
                if item["reverse_scored"]:
                    effective_response = 8 - response

                log_lik += self.irt.log_likelihood(
                    effective_response,
                    theta,
                    item["alpha"],
                    item["beta"]
                )

            log_posterior[theta_idx] = log_prior + log_lik

        # Convert from log scale and normalize
        # Subtract max for numerical stability before exponentiating
        log_posterior -= log_posterior.max()
        posterior = np.exp(log_posterior)

        # Normalize using trapezoidal integration
        # Use np.trapezoid (NumPy 2.0+) with fallback to np.trapz (NumPy 1.x)
        trapz_func = getattr(np, 'trapezoid', np.trapz)

        normalizing_constant = trapz_func(posterior, self.theta_grid)
        if normalizing_constant > 0:
            posterior = posterior / normalizing_constant
        else:
            # Fallback to prior if posterior computation fails
            posterior = np.array([
                self.prior_density(theta) for theta in self.theta_grid
            ])
            posterior = posterior / trapz_func(posterior, self.theta_grid)

        # Compute posterior mean
        posterior_mean = trapz_func(posterior * self.theta_grid, self.theta_grid)

        # Compute posterior variance and SD
        posterior_var = trapz_func(
            posterior * (self.theta_grid - posterior_mean) ** 2,
            self.theta_grid
        )
        posterior_sd = np.sqrt(max(posterior_var, 1e-10))

        return posterior, posterior_mean, posterior_sd

    def update_trait_state(
        self,
        trait_state: TraitState,
        item_number: int,
        response: int
    ) -> TraitState:
        """
        Update trait state after a new response.

        Args:
            trait_state: Current trait state
            item_number: Item that was administered
            response: Response value (1-7)

        Returns:
            Updated TraitState
        """
        # Add new response
        trait_state.responses.append((item_number, response))
        trait_state.items_used.append(item_number)

        # Compute new posterior
        posterior, post_mean, post_sd = self.compute_posterior(
            trait_state.responses,
            trait_state.trait
        )

        # Update state
        trait_state.theta_estimate = post_mean
        trait_state.standard_error = post_sd
        trait_state.posterior_mean = post_mean
        trait_state.posterior_sd = post_sd

        # Update total information
        trait_state.total_information = sum(
            self.irt.item_fisher_information(item_num, post_mean)
            for item_num in trait_state.items_used
        )

        return trait_state

    def expected_posterior_variance(
        self,
        trait_state: TraitState,
        candidate_item: int
    ) -> float:
        """
        Calculate expected posterior variance if we administer candidate_item.

        Used for item selection - lower expected variance = more informative.

        EPV = sum over possible responses of P(response) * Var(theta | response)

        Args:
            trait_state: Current trait state
            candidate_item: Item number to evaluate

        Returns:
            Expected posterior variance
        """
        item = MINI_IPIP6_ITEMS[candidate_item]
        current_theta = trait_state.theta_estimate

        epv = 0.0

        # Consider all possible responses (1-7)
        for response in range(1, 8):
            # Probability of this response given current theta
            effective_response = response
            if item["reverse_scored"]:
                effective_response = 8 - response

            p_response = self.irt.likelihood(
                effective_response,
                current_theta,
                item["alpha"],
                item["beta"]
            )

            # Hypothetical posterior if we observe this response
            hypothetical_responses = trait_state.responses + [(candidate_item, response)]
            _, _, hyp_sd = self.compute_posterior(
                hypothetical_responses,
                trait_state.trait
            )

            epv += p_response * (hyp_sd ** 2)

        return epv

    def compute_standard_error(self, trait_state: TraitState) -> float:
        """
        Compute standard error from trait state.

        SE = posterior SD after Bayesian update

        Args:
            trait_state: Current trait state

        Returns:
            Standard error
        """
        return trait_state.posterior_sd

    def estimate_from_responses(
        self,
        responses: List[Tuple[int, int]],
        trait: str
    ) -> Tuple[float, float]:
        """
        Estimate theta and SE from a list of responses.

        Convenience method for batch estimation.

        Args:
            responses: List of (item_number, response) tuples
            trait: Trait name

        Returns:
            Tuple of (theta_estimate, standard_error)
        """
        _, post_mean, post_sd = self.compute_posterior(responses, trait)
        return post_mean, post_sd


# Module-level instance
bayesian_updater = BayesianUpdater()
