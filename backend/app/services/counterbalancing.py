"""
Random Counterbalancing for Within-Subject Design.

Implements random order assignment between Survey and DOSE conditions
to prevent systematic order effects.
"""

import random
from typing import Dict, List, Optional

# Two assessment conditions
CONDITIONS = ["survey", "dose"]


def get_condition_name(index: int) -> str:
    """Get condition name from index."""
    return CONDITIONS[index]


def get_condition_index(name: str) -> int:
    """Get condition index from name."""
    return CONDITIONS.index(name)


def assign_condition_order(participant_number: int) -> Dict:
    """
    Assign randomized condition order to a participant.

    Args:
        participant_number: Sequential participant number (1-indexed)
            Note: participant_number is kept for API compatibility but
            order is now randomly assigned.

    Returns:
        Dict containing:
        - latin_square_row: 0 for survey-first, 1 for dose-first
        - condition_sequence: List of condition indices
        - condition_order: List of condition names in order
    """
    # Randomly decide order
    order = CONDITIONS.copy()
    random.shuffle(order)

    # Determine row index based on which comes first
    row_index = 0 if order[0] == "survey" else 1
    sequence = [CONDITIONS.index(c) for c in order]

    return {
        "latin_square_row": row_index,
        "condition_sequence": sequence,
        "condition_order": order,
    }


def get_next_condition(
    condition_order: List[str],
    completed_conditions: List[str]
) -> Optional[str]:
    """
    Get the next condition for a participant based on their assigned order.

    Args:
        condition_order: Participant's assigned condition order
        completed_conditions: List of completed condition names

    Returns:
        Next condition name, or None if all completed
    """
    for condition in condition_order:
        if condition not in completed_conditions:
            return condition
    return None


def get_sequence_number(
    condition_order: List[str],
    condition: str
) -> int:
    """
    Get the sequence number (1-2) for a condition in a participant's order.

    Args:
        condition_order: Participant's assigned condition order
        condition: Condition name to find

    Returns:
        Sequence number (1-indexed)
    """
    return condition_order.index(condition) + 1


def validate_order_balance(participant_count: int) -> Dict:
    """
    Validate expected balance for random assignment.

    Note: With random assignment, balance is probabilistic.
    Expected 50/50 split with variance.

    Args:
        participant_count: Total number of participants

    Returns:
        Dict with balance statistics
    """
    return {
        "total_participants": participant_count,
        "expected_per_order": participant_count / 2,
        "note": "Random assignment - actual balance may vary"
    }
