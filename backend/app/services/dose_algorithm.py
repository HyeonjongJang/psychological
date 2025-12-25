"""
DOSE (Dynamic Optimization of Sequential Estimation) Algorithm.

Implements adaptive testing using Item Response Theory with Bayesian updates
and Maximum Fisher Information item selection.

Algorithm flow:
1. Initialize with N(0,1) prior for each trait
2. Select starting items (highest discrimination)
3. Administer item, collect response
4. Update posterior using Bayes' theorem
5. Calculate SE and check stopping rule (SE < threshold)
6. If not stopped, select next item maximizing Fisher Information
7. Repeat until all traits reach stopping criterion or max items
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from .irt_engine import IRTEngine, irt_engine
from .bayesian_updater import BayesianUpdater, TraitState, bayesian_updater
from ..core.mini_ipip6_data import (
    MINI_IPIP6_ITEMS, TRAITS, TRAIT_ITEMS,
    get_highest_discrimination_item
)
from ..config import settings


class DOSEAction(str, Enum):
    """Possible actions from DOSE algorithm."""
    PRESENT_ITEM = "present_item"
    COMPLETE = "complete"


@dataclass
class ItemHistory:
    """Record of an administered item."""
    item_number: int
    trait: str
    response: int
    theta_before: float
    theta_after: float
    se_before: float
    se_after: float
    fisher_information: float
    presentation_order: int


@dataclass
class DOSESessionState:
    """Complete state for a DOSE assessment session."""
    trait_states: Dict[str, TraitState]
    administered_items: List[ItemHistory] = field(default_factory=list)
    traits_completed: Dict[str, bool] = field(default_factory=dict)
    total_items: int = 0
    current_trait_index: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "trait_states": {
                trait: state.to_dict()
                for trait, state in self.trait_states.items()
            },
            "traits_completed": self.traits_completed,
            "total_items": self.total_items,
            "administered_items": [
                {
                    "item_number": h.item_number,
                    "trait": h.trait,
                    "response": h.response,
                    "theta_after": h.theta_after,
                    "se_after": h.se_after,
                    "fisher_information": h.fisher_information,
                    "presentation_order": h.presentation_order,
                }
                for h in self.administered_items
            ]
        }


class DOSEAlgorithm:
    """
    DOSE Algorithm for adaptive personality assessment.

    Implements:
    - Maximum Fisher Information item selection
    - Bayesian posterior updates
    - Stopping rule based on SE threshold
    - Round-robin trait assessment
    """

    def __init__(
        self,
        irt: IRTEngine = None,
        bayesian: BayesianUpdater = None,
        se_threshold: float = None,
        max_items_per_trait: int = None
    ):
        """
        Initialize DOSE algorithm.

        Args:
            irt: IRT engine instance
            bayesian: Bayesian updater instance
            se_threshold: SE threshold for stopping (default from settings)
            max_items_per_trait: Maximum items per trait (default from settings)
        """
        self.irt = irt or irt_engine
        self.bayesian = bayesian or bayesian_updater
        self.se_threshold = se_threshold or settings.DOSE_SE_THRESHOLD
        self.max_items_per_trait = max_items_per_trait or settings.DOSE_MAX_ITEMS_PER_TRAIT

    def initialize_session(self) -> DOSESessionState:
        """
        Initialize a new DOSE assessment session.

        Returns:
            New DOSESessionState with initialized trait states
        """
        trait_states = self.bayesian.initialize_trait_states()
        traits_completed = {trait: False for trait in TRAITS}

        return DOSESessionState(
            trait_states=trait_states,
            traits_completed=traits_completed,
        )

    def select_starting_items(self) -> Dict[str, int]:
        """
        Select the first item for each trait.

        Uses highest discrimination (alpha) for cold start.

        Returns:
            Dict mapping trait to starting item number
        """
        return {
            trait: get_highest_discrimination_item(trait)
            for trait in TRAITS
        }

    def select_next_item(
        self,
        state: DOSESessionState,
        trait: str
    ) -> Optional[int]:
        """
        Select the next item for a trait using Maximum Fisher Information.

        Args:
            state: Current session state
            trait: Trait to select item for

        Returns:
            Item number with maximum information, or None if no items available
        """
        trait_state = state.trait_states[trait]
        current_theta = trait_state.theta_estimate
        administered = set(trait_state.items_used)

        # Get available items for this trait
        available_items = [
            item_num for item_num in TRAIT_ITEMS[trait]
            if item_num not in administered
        ]

        if not available_items:
            return None

        # Calculate Fisher Information for each available item
        item_info = {}
        for item_num in available_items:
            info = self.irt.item_fisher_information(item_num, current_theta)
            item_info[item_num] = info

        # Select item with maximum information
        best_item = max(item_info, key=item_info.get)
        return best_item

    def process_response(
        self,
        state: DOSESessionState,
        item_number: int,
        response: int
    ) -> DOSESessionState:
        """
        Process a response and update session state.

        Args:
            state: Current session state
            item_number: Administered item number
            response: Response value (1-7)

        Returns:
            Updated session state
        """
        item = MINI_IPIP6_ITEMS[item_number]
        trait = item["trait"]
        trait_state = state.trait_states[trait]

        # Store values before update
        theta_before = trait_state.theta_estimate
        se_before = trait_state.standard_error

        # Calculate Fisher Information for this item at current theta
        fisher_info = self.irt.item_fisher_information(item_number, theta_before)

        # Update posterior using Bayesian updater
        trait_state = self.bayesian.update_trait_state(
            trait_state,
            item_number,
            response
        )
        state.trait_states[trait] = trait_state

        # Create history record
        history = ItemHistory(
            item_number=item_number,
            trait=trait,
            response=response,
            theta_before=theta_before,
            theta_after=trait_state.theta_estimate,
            se_before=se_before,
            se_after=trait_state.standard_error,
            fisher_information=fisher_info,
            presentation_order=state.total_items + 1,
        )
        state.administered_items.append(history)
        state.total_items += 1

        # Check if trait has reached stopping criterion
        if (trait_state.standard_error < self.se_threshold or
                len(trait_state.items_used) >= self.max_items_per_trait):
            state.traits_completed[trait] = True

        return state

    def get_next_action(self, state: DOSESessionState) -> Dict[str, Any]:
        """
        Determine the next action in the assessment.

        Returns:
            Dictionary with action type and relevant data:
            - If complete: {"action": "complete", "current_estimates": {...}}
            - If present_item: {"action": "present_item", "item_number": ..., ...}
        """
        # Check if all traits are completed
        if all(state.traits_completed.values()):
            return {
                "action": DOSEAction.COMPLETE,
                "current_estimates": self._get_current_estimates(state),
                "total_items": state.total_items,
            }

        # Find incomplete traits
        incomplete_traits = [
            t for t in TRAITS
            if not state.traits_completed[t]
        ]

        # Round-robin: cycle through incomplete traits
        # Use total_items to determine which trait to assess next
        trait_index = state.total_items % len(incomplete_traits)
        next_trait = incomplete_traits[trait_index]

        # Select next item for this trait
        next_item = self.select_next_item(state, next_trait)

        if next_item is None:
            # No more items for this trait, mark as completed
            state.traits_completed[next_trait] = True
            return self.get_next_action(state)  # Recurse

        # Get item data
        item_data = MINI_IPIP6_ITEMS[next_item]
        trait_state = state.trait_states[next_trait]

        return {
            "action": DOSEAction.PRESENT_ITEM,
            "item_number": next_item,
            "item_text": item_data["text"],
            "trait": next_trait,
            "current_theta": trait_state.theta_estimate,
            "current_se": trait_state.standard_error,
            "current_estimates": self._get_current_estimates(state),
            "progress": {
                "items_administered": state.total_items,
                "traits_completed": sum(state.traits_completed.values()),
                "total_traits": len(TRAITS),
            }
        }

    def _get_current_estimates(self, state: DOSESessionState) -> Dict[str, Dict]:
        """
        Get current theta and SE estimates for all traits.

        Args:
            state: Current session state

        Returns:
            Dict mapping trait to estimates
        """
        return {
            trait: {
                "theta": state.trait_states[trait].theta_estimate,
                "se": state.trait_states[trait].standard_error,
                "items_administered": len(state.trait_states[trait].items_used),
                "completed": state.traits_completed[trait],
            }
            for trait in TRAITS
        }

    def get_final_results(self, state: DOSESessionState) -> Dict[str, Any]:
        """
        Generate final results after assessment completion.

        Args:
            state: Final session state

        Returns:
            Complete results dictionary
        """
        trait_estimates = {}
        for trait in TRAITS:
            ts = state.trait_states[trait]
            trait_estimates[trait] = {
                "theta": ts.theta_estimate,
                "standard_error": ts.standard_error,
                "likert_score": self.irt.theta_to_likert_scale(ts.theta_estimate),
                "items_administered": len(ts.items_used),
                "items_used": ts.items_used,
                "total_information": ts.total_information,
            }

        return {
            "trait_estimates": trait_estimates,
            "total_items_administered": state.total_items,
            "item_reduction_rate": 1 - (state.total_items / 24),
            "item_history": [
                {
                    "item_number": h.item_number,
                    "trait": h.trait,
                    "response": h.response,
                    "item_text": MINI_IPIP6_ITEMS[h.item_number]["text"],
                    "theta_before": h.theta_before,
                    "theta_after": h.theta_after,
                    "se_before": h.se_before,
                    "se_after": h.se_after,
                    "fisher_information": h.fisher_information,
                    "presentation_order": h.presentation_order,
                }
                for h in state.administered_items
            ],
        }

    def check_stopping_criterion(
        self,
        state: DOSESessionState,
        trait: str
    ) -> Tuple[bool, str]:
        """
        Check if stopping criterion is met for a trait.

        Args:
            state: Current session state
            trait: Trait to check

        Returns:
            Tuple of (should_stop, reason)
        """
        ts = state.trait_states[trait]

        if ts.standard_error < self.se_threshold:
            return True, f"SE ({ts.standard_error:.3f}) below threshold ({self.se_threshold})"

        if len(ts.items_used) >= self.max_items_per_trait:
            return True, f"Maximum items ({self.max_items_per_trait}) reached"

        return False, "Continue"


# Module-level instance
dose_algorithm = DOSEAlgorithm()
