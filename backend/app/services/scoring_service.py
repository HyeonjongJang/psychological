"""
Classical Scoring Service for Personality Assessment.

Implements classical test theory scoring for the Mini-IPIP6 scale.
Used for G1 (Survey) and G2 (Static Chatbot) conditions.
"""

from typing import Dict, List, Tuple
from ..core.mini_ipip6_data import (
    MINI_IPIP6_ITEMS, TRAITS, TRAIT_ITEMS,
    REVERSE_SCORED_ITEMS, score_response
)


def calculate_trait_score(
    responses: Dict[int, int],
    trait: str
) -> Tuple[float, int]:
    """
    Calculate average score for a single trait.

    Args:
        responses: Dict mapping item_number to response (1-7)
        trait: Trait name

    Returns:
        Tuple of (average_score, num_items)
    """
    trait_items = TRAIT_ITEMS[trait]
    scores = []

    for item_num in trait_items:
        if item_num in responses:
            # Apply reverse scoring if needed
            scored = score_response(item_num, responses[item_num])
            scores.append(scored)

    if not scores:
        return 0.0, 0

    return sum(scores) / len(scores), len(scores)


def calculate_all_trait_scores(
    responses: Dict[int, int]
) -> Dict[str, Dict]:
    """
    Calculate scores for all six traits.

    Args:
        responses: Dict mapping item_number to response (1-7)

    Returns:
        Dict mapping trait to score data
    """
    results = {}

    for trait in TRAITS:
        score, num_items = calculate_trait_score(responses, trait)
        results[trait] = {
            "score": score,
            "num_items": num_items,
            "complete": num_items == 4,  # 4 items per trait
        }

    return results


def calculate_all_scores_from_list(
    response_list: List[Tuple[int, int]]
) -> Dict[str, Dict]:
    """
    Calculate scores from a list of (item_number, response) tuples.

    Args:
        response_list: List of (item_number, response) tuples

    Returns:
        Dict mapping trait to score data
    """
    responses = {item_num: response for item_num, response in response_list}
    return calculate_all_trait_scores(responses)


def validate_complete_responses(responses: Dict[int, int]) -> Dict:
    """
    Validate that all 24 items have been responded to.

    Args:
        responses: Dict mapping item_number to response

    Returns:
        Validation result dict
    """
    expected_items = set(range(1, 25))
    provided_items = set(responses.keys())

    missing = expected_items - provided_items
    extra = provided_items - expected_items

    invalid_values = {
        item: val for item, val in responses.items()
        if not (1 <= val <= 7)
    }

    return {
        "valid": len(missing) == 0 and len(extra) == 0 and len(invalid_values) == 0,
        "missing_items": list(missing),
        "extra_items": list(extra),
        "invalid_values": invalid_values,
        "total_responses": len(responses),
    }


def get_score_interpretation(trait: str, score: float) -> str:
    """
    Get interpretation text for a trait score.

    Args:
        trait: Trait name
        score: Score on 1-7 scale

    Returns:
        Interpretation string
    """
    if score < 2.5:
        level = "Very Low"
    elif score < 3.5:
        level = "Low"
    elif score < 4.5:
        level = "Average"
    elif score < 5.5:
        level = "High"
    else:
        level = "Very High"

    return f"{level} {trait.replace('_', ' ').title()}"


def compare_scores(
    scores1: Dict[str, float],
    scores2: Dict[str, float]
) -> Dict:
    """
    Compare two sets of trait scores.

    Useful for comparing DOSE vs Survey results.

    Args:
        scores1: First set of scores
        scores2: Second set of scores

    Returns:
        Comparison statistics
    """
    import numpy as np
    import math

    traits = list(set(scores1.keys()) & set(scores2.keys()))

    if not traits:
        return {"error": "No common traits to compare"}

    s1 = np.array([scores1[t] for t in traits])
    s2 = np.array([scores2[t] for t in traits])

    # Calculate correlation (handle NaN when variance is zero)
    correlation = np.corrcoef(s1, s2)[0, 1]
    if math.isnan(correlation) or math.isinf(correlation):
        correlation = 0.0  # Default to 0 when correlation can't be computed

    # Calculate differences
    diffs = s1 - s2
    mae = np.mean(np.abs(diffs))
    rmse = np.sqrt(np.mean(diffs ** 2))

    # Ensure no NaN/Inf values in output
    def safe_float(val):
        if math.isnan(val) or math.isinf(val):
            return 0.0
        return float(val)

    return {
        "traits_compared": traits,
        "pearson_r": safe_float(correlation),  # Frontend expects "pearson_r"
        "mean_absolute_error": safe_float(mae),  # Frontend expects "mean_absolute_error"
        "rmse": safe_float(rmse),
        "trait_differences": {t: safe_float(s1[i] - s2[i]) for i, t in enumerate(traits)},
    }
