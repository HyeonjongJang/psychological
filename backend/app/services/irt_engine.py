"""
Item Response Theory (IRT) Engine implementing Graded Response Model (GRM).

Based on Samejima's (1969) Graded Response Model and the 2PLM formulation
from Sibley (2012).

Key formulas:
- Cumulative probability: P*(theta) = 1 / (1 + exp(-alpha * (theta - beta_k)))
- Category probability: P_k(theta) = P*_{k-1}(theta) - P*_k(theta)
- Fisher Information: I(theta) = sum over thresholds of alpha^2 * P*(1-P*)
"""

import numpy as np
from typing import List, Tuple, Optional
from ..core.mini_ipip6_data import MINI_IPIP6_ITEMS


class IRTEngine:
    """
    IRT Engine for Graded Response Model calculations.

    Implements the Two-Parameter Logistic Model (2PLM) extended for
    polytomous (graded) responses on a 7-point Likert scale.
    """

    def __init__(
        self,
        theta_range: Tuple[float, float] = (-4.0, 4.0),
        grid_points: int = 200
    ):
        """
        Initialize IRT Engine.

        Args:
            theta_range: Range of theta values for integration
            grid_points: Number of points for numerical integration
        """
        self.theta_range = theta_range
        self.grid_points = grid_points
        self.theta_grid = np.linspace(theta_range[0], theta_range[1], grid_points)
        self.theta_step = self.theta_grid[1] - self.theta_grid[0]

    def cumulative_probability(
        self,
        theta: float,
        alpha: float,
        beta: float
    ) -> float:
        """
        Calculate cumulative probability P*(theta).

        P*(theta) = 1 / (1 + exp(-alpha * (theta - beta)))

        This is the probability of responding at or above a given threshold.

        Args:
            theta: Trait level (ability/personality)
            alpha: Item discrimination parameter
            beta: Item difficulty/threshold parameter

        Returns:
            Probability of responding at or above the threshold
        """
        exponent = -alpha * (theta - beta)
        # Clip to prevent numerical overflow
        exponent = np.clip(exponent, -700, 700)
        return 1.0 / (1.0 + np.exp(exponent))

    def category_probabilities(
        self,
        theta: float,
        alpha: float,
        betas: List[float]
    ) -> np.ndarray:
        """
        Calculate probability of each response category (1-7).

        For 7-point scale with 6 beta thresholds:
        - P(X=1) = 1 - P*(beta_1)
        - P(X=k) = P*(beta_{k-1}) - P*(beta_k) for k=2,...,6
        - P(X=7) = P*(beta_6)

        Args:
            theta: Trait level
            alpha: Item discrimination
            betas: List of 6 difficulty thresholds

        Returns:
            Array of 7 probabilities for response categories 1-7
        """
        probs = np.zeros(7)

        # P(X=1): probability of scoring 1 (below first threshold)
        probs[0] = 1.0 - self.cumulative_probability(theta, alpha, betas[0])

        # P(X=k) for k=2 to 6
        for k in range(1, 6):
            probs[k] = (
                self.cumulative_probability(theta, alpha, betas[k - 1]) -
                self.cumulative_probability(theta, alpha, betas[k])
            )

        # P(X=7): probability of scoring 7 (above last threshold)
        probs[6] = self.cumulative_probability(theta, alpha, betas[5])

        # Handle numerical issues: ensure valid probabilities
        probs = np.clip(probs, 1e-10, 1.0)
        probs = probs / probs.sum()  # Normalize to sum to 1

        return probs

    def expected_score(
        self,
        theta: float,
        alpha: float,
        betas: List[float]
    ) -> float:
        """
        Calculate expected response (1-7) for a given theta.

        E[X|theta] = sum over k of k * P(X=k|theta)

        Args:
            theta: Trait level
            alpha: Item discrimination
            betas: Difficulty thresholds

        Returns:
            Expected response value (1-7 scale)
        """
        probs = self.category_probabilities(theta, alpha, betas)
        return np.sum(probs * np.arange(1, 8))

    def fisher_information(
        self,
        theta: float,
        alpha: float,
        betas: List[float]
    ) -> float:
        """
        Calculate Fisher Information for an item at given theta.

        For GRM, information is calculated as:
        I(theta) = alpha^2 * sum over thresholds of P*_k(1 - P*_k)

        This represents how much information the item provides
        about theta at the current estimate.

        Args:
            theta: Current trait estimate
            alpha: Item discrimination
            betas: Difficulty thresholds

        Returns:
            Fisher Information value (higher = more informative)
        """
        info = 0.0
        for beta in betas:
            p_star = self.cumulative_probability(theta, alpha, beta)
            # Information contribution from each threshold
            info += p_star * (1.0 - p_star)

        return (alpha ** 2) * info

    def likelihood(
        self,
        response: int,
        theta: float,
        alpha: float,
        betas: List[float]
    ) -> float:
        """
        Calculate likelihood P(X=response | theta).

        Args:
            response: Observed response (1-7 Likert scale)
            theta: Trait level
            alpha: Item discrimination
            betas: Difficulty thresholds

        Returns:
            Likelihood of the observed response
        """
        probs = self.category_probabilities(theta, alpha, betas)
        return probs[response - 1]  # Convert 1-7 to 0-6 index

    def log_likelihood(
        self,
        response: int,
        theta: float,
        alpha: float,
        betas: List[float]
    ) -> float:
        """
        Calculate log-likelihood for numerical stability.

        Args:
            response: Observed response (1-7)
            theta: Trait level
            alpha: Item discrimination
            betas: Difficulty thresholds

        Returns:
            Log-likelihood value
        """
        lik = self.likelihood(response, theta, alpha, betas)
        return np.log(max(lik, 1e-300))

    def item_log_likelihood(
        self,
        item_number: int,
        response: int,
        theta: float
    ) -> float:
        """
        Calculate log-likelihood for a specific Mini-IPIP6 item.

        Handles reverse scoring automatically.

        Args:
            item_number: Item number (1-24)
            response: Observed response (1-7)
            theta: Trait level

        Returns:
            Log-likelihood value
        """
        item = MINI_IPIP6_ITEMS[item_number]

        # For reverse-scored items, a HIGH response indicates LOW trait
        # Transform response for likelihood calculation
        effective_response = response
        if item["reverse_scored"]:
            effective_response = 8 - response

        return self.log_likelihood(
            effective_response,
            theta,
            item["alpha"],
            item["beta"]
        )

    def item_fisher_information(
        self,
        item_number: int,
        theta: float
    ) -> float:
        """
        Calculate Fisher Information for a specific Mini-IPIP6 item.

        Args:
            item_number: Item number (1-24)
            theta: Current trait estimate

        Returns:
            Fisher Information value
        """
        item = MINI_IPIP6_ITEMS[item_number]
        return self.fisher_information(theta, item["alpha"], item["beta"])

    def total_information(
        self,
        item_numbers: List[int],
        theta: float
    ) -> float:
        """
        Calculate total Fisher Information from multiple items.

        Args:
            item_numbers: List of item numbers
            theta: Current trait estimate

        Returns:
            Sum of Fisher Information across items
        """
        return sum(
            self.item_fisher_information(num, theta)
            for num in item_numbers
        )

    def standard_error_from_information(
        self,
        total_info: float
    ) -> float:
        """
        Calculate standard error from total Fisher Information.

        SE = 1 / sqrt(I(theta))

        Args:
            total_info: Total Fisher Information

        Returns:
            Standard error of the estimate
        """
        if total_info <= 0:
            return float('inf')
        return 1.0 / np.sqrt(total_info)

    def theta_to_likert_scale(
        self,
        theta: float,
        scale_min: float = 1.0,
        scale_max: float = 7.0
    ) -> float:
        """
        Convert theta (z-score) to Likert scale (1-7).

        Maps theta from approximately N(0,1) to the 1-7 scale
        using a linear transformation.

        Args:
            theta: Trait level in z-score units
            scale_min: Minimum of target scale
            scale_max: Maximum of target scale

        Returns:
            Score on Likert scale
        """
        # Assume theta range of -3 to +3 covers most of population
        # Map this to 1-7 scale
        theta_min, theta_max = -3.0, 3.0

        # Linear transformation
        normalized = (theta - theta_min) / (theta_max - theta_min)
        likert = scale_min + normalized * (scale_max - scale_min)

        # Clip to valid range
        return np.clip(likert, scale_min, scale_max)

    def likert_to_theta_scale(
        self,
        likert: float,
        scale_min: float = 1.0,
        scale_max: float = 7.0
    ) -> float:
        """
        Convert Likert scale (1-7) to theta (z-score).

        Args:
            likert: Score on Likert scale
            scale_min: Minimum of source scale
            scale_max: Maximum of source scale

        Returns:
            Theta in z-score units
        """
        theta_min, theta_max = -3.0, 3.0

        # Inverse linear transformation
        normalized = (likert - scale_min) / (scale_max - scale_min)
        theta = theta_min + normalized * (theta_max - theta_min)

        return theta


# Module-level instance for convenience
irt_engine = IRTEngine()
