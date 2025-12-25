"""
Mini-IPIP6 Item Data with IRT Parameters from Sibley (2012).

Reference:
Sibley, C. G. (2012). The Mini-IPIP6: Item Response Theory analysis of a short
measure of the big-six factors of personality in New Zealand.
New Zealand Journal of Psychology, 41(3), 20-30.

Parameters extracted from Table 2 (page 26).
"""

from typing import Dict, List

# Six personality traits measured by Mini-IPIP6
TRAITS = [
    "extraversion",
    "agreeableness",
    "conscientiousness",
    "neuroticism",
    "openness",
    "honesty_humility"
]

# Trait display names (English)
TRAIT_NAMES = {
    "extraversion": "Extraversion",
    "agreeableness": "Agreeableness",
    "conscientiousness": "Conscientiousness",
    "neuroticism": "Neuroticism",
    "openness": "Openness to Experience",
    "honesty_humility": "Honesty-Humility"
}

# Trait display names (Korean)
TRAIT_NAMES_KR = {
    "extraversion": "외향성",
    "agreeableness": "우호성",
    "conscientiousness": "성실성",
    "neuroticism": "신경증",
    "openness": "개방성",
    "honesty_humility": "정직-겸손"
}

# Items for each trait (1-indexed item numbers)
TRAIT_ITEMS = {
    "extraversion": [1, 7, 19, 23],
    "agreeableness": [2, 8, 14, 20],
    "conscientiousness": [3, 10, 11, 22],
    "neuroticism": [4, 15, 16, 17],
    "openness": [5, 9, 13, 21],
    "honesty_humility": [6, 12, 18, 24]
}

# Items that need reverse scoring
REVERSE_SCORED_ITEMS = [6, 7, 8, 9, 11, 12, 13, 15, 17, 18, 19, 20, 21, 22, 24]

# Complete Mini-IPIP6 item data with IRT parameters
# alpha: discrimination parameter
# beta: difficulty parameters (6 thresholds for 7-point Likert scale)
MINI_IPIP6_ITEMS: Dict[int, Dict] = {
    # === EXTRAVERSION ===
    1: {
        "text": "Am the life of the party.",
        "trait": "extraversion",
        "reverse_scored": False,
        "alpha": 1.07,
        "beta": [-1.85, -1.04, -0.21, 0.89, 1.98, 2.76]
    },
    7: {
        "text": "Don't talk a lot.",
        "trait": "extraversion",
        "reverse_scored": True,
        "alpha": 0.84,
        "beta": [-2.82, -1.67, -0.80, 0.10, 0.86, 1.91]
    },
    19: {
        "text": "Keep in the background.",
        "trait": "extraversion",
        "reverse_scored": True,
        "alpha": 1.00,
        "beta": [-2.51, -1.32, -0.49, 0.45, 1.23, 2.44]
    },
    23: {
        "text": "Talk to a lot of different people at parties.",
        "trait": "extraversion",
        "reverse_scored": False,
        "alpha": 0.92,
        "beta": [-2.25, -1.27, -0.54, 0.24, 0.97, 1.96]
    },

    # === AGREEABLENESS ===
    2: {
        "text": "Sympathize with others' feelings.",
        "trait": "agreeableness",
        "reverse_scored": False,
        "alpha": 1.46,
        "beta": [-3.19, -2.51, -1.86, -1.19, -0.28, 0.99]
    },
    8: {
        "text": "Am not interested in other people's problems.",
        "trait": "agreeableness",
        "reverse_scored": True,
        "alpha": 0.66,
        "beta": [-3.74, -2.51, -1.59, -0.76, 0.22, 1.76]
    },
    14: {
        "text": "Feel others' emotions.",
        "trait": "agreeableness",
        "reverse_scored": False,
        "alpha": 1.12,
        "beta": [-3.15, -2.36, -1.70, -0.92, 0.03, 1.37]
    },
    20: {
        "text": "Am not really interested in others.",
        "trait": "agreeableness",
        "reverse_scored": True,
        "alpha": 0.81,
        "beta": [-3.77, -2.69, -1.94, -1.19, -0.28, 1.25]
    },

    # === CONSCIENTIOUSNESS ===
    3: {
        "text": "Get chores done right away.",
        "trait": "conscientiousness",
        "reverse_scored": False,
        "alpha": 0.90,
        "beta": [-3.39, -2.13, -1.18, -0.27, 0.57, 1.64]
    },
    10: {
        "text": "Like order.",
        "trait": "conscientiousness",
        "reverse_scored": False,
        "alpha": 0.85,
        "beta": [-3.49, -2.72, -2.02, -1.06, -0.20, 1.12]
    },
    11: {
        "text": "Make a mess of things.",
        "trait": "conscientiousness",
        "reverse_scored": True,
        "alpha": 0.77,
        "beta": [-4.21, -2.93, -2.05, -1.07, -0.18, 1.38]
    },
    22: {
        "text": "Often forget to put things back in their proper place.",
        "trait": "conscientiousness",
        "reverse_scored": True,
        "alpha": 0.94,
        "beta": [-2.63, -1.73, -1.17, -0.64, -0.09, 1.11]
    },

    # === NEUROTICISM ===
    4: {
        "text": "Have frequent mood swings.",
        "trait": "neuroticism",
        "reverse_scored": False,
        "alpha": 1.13,
        "beta": [-1.32, -0.23, 0.36, 1.04, 1.72, 2.53]
    },
    15: {
        "text": "Am relaxed most of the time.",
        "trait": "neuroticism",
        "reverse_scored": True,
        "alpha": 0.77,
        "beta": [-2.24, -0.70, 0.38, 1.48, 2.57, 3.92]
    },
    16: {
        "text": "Get upset easily.",
        "trait": "neuroticism",
        "reverse_scored": False,
        "alpha": 0.90,
        "beta": [-2.15, -0.76, 0.05, 0.89, 1.72, 2.80]
    },
    17: {
        "text": "Seldom feel blue.",
        "trait": "neuroticism",
        "reverse_scored": True,
        "alpha": 0.65,
        "beta": [-2.82, -1.01, -0.19, 0.76, 1.80, 3.15]
    },

    # === OPENNESS TO EXPERIENCE ===
    5: {
        "text": "Have a vivid imagination.",
        "trait": "openness",
        "reverse_scored": False,
        "alpha": 0.54,
        "beta": [-4.22, -2.68, -1.52, -0.21, 0.94, 2.47]
    },
    9: {
        "text": "Have difficulty understanding abstract ideas.",
        "trait": "openness",
        "reverse_scored": True,
        "alpha": 1.10,
        "beta": [-2.70, -1.72, -1.00, -0.17, 0.47, 1.61]
    },
    13: {
        "text": "Do not have a good imagination.",
        "trait": "openness",
        "reverse_scored": True,
        "alpha": 0.79,
        "beta": [-3.45, -2.35, -1.56, -0.85, -0.11, 1.13]
    },
    21: {
        "text": "Am not interested in abstract ideas.",
        "trait": "openness",
        "reverse_scored": True,
        "alpha": 1.24,
        "beta": [-2.57, -1.71, -1.12, -0.29, 0.41, 1.43]
    },

    # === HONESTY-HUMILITY ===
    6: {
        "text": "Feel entitled to more of everything.",
        "trait": "honesty_humility",
        "reverse_scored": True,
        "alpha": 0.91,
        "beta": [-3.43, -2.67, -1.89, -1.10, -0.42, 0.71]
    },
    12: {
        "text": "Deserve more things in life.",
        "trait": "honesty_humility",
        "reverse_scored": True,
        "alpha": 1.17,
        "beta": [-2.32, -1.69, -1.08, -0.33, 0.17, 0.99]
    },
    18: {
        "text": "Would like to be seen driving around in a very expensive car.",
        "trait": "honesty_humility",
        "reverse_scored": True,
        "alpha": 1.47,
        "beta": [-1.92, -1.42, -0.97, -0.52, -0.16, 0.48]
    },
    24: {
        "text": "Would get a lot of pleasure from owning expensive luxury goods.",
        "trait": "honesty_humility",
        "reverse_scored": True,
        "alpha": 1.16,
        "beta": [-2.08, -1.30, -0.71, -0.12, 0.31, 1.10]
    },
}

# Korean translations for all items
MINI_IPIP6_ITEMS_KR: Dict[int, str] = {
    1: "나는 파티의 분위기 메이커이다.",
    2: "나는 다른 사람들의 감정에 공감한다.",
    3: "나는 집안일을 바로바로 처리한다.",
    4: "나는 기분 변화가 자주 있다.",
    5: "나는 생생한 상상력을 가지고 있다.",
    6: "나는 모든 것에서 더 많은 것을 받을 자격이 있다고 느낀다.",
    7: "나는 말을 많이 하지 않는다.",
    8: "나는 다른 사람들의 문제에 관심이 없다.",
    9: "나는 추상적인 아이디어를 이해하는 데 어려움이 있다.",
    10: "나는 질서를 좋아한다.",
    11: "나는 일을 엉망으로 만든다.",
    12: "나는 인생에서 더 많은 것을 받을 자격이 있다.",
    13: "나는 상상력이 좋지 않다.",
    14: "나는 다른 사람들의 감정을 느낀다.",
    15: "나는 대부분의 시간 동안 편안하다.",
    16: "나는 쉽게 화가 난다.",
    17: "나는 거의 우울하지 않다.",
    18: "나는 매우 비싼 차를 운전하는 모습을 보여주고 싶다.",
    19: "나는 뒤에서 조용히 있는 편이다.",
    20: "나는 다른 사람들에게 별로 관심이 없다.",
    21: "나는 추상적인 아이디어에 관심이 없다.",
    22: "나는 물건을 제자리에 돌려놓는 것을 자주 잊어버린다.",
    23: "나는 파티에서 다양한 사람들과 대화한다.",
    24: "나는 비싼 명품을 소유하는 것에서 큰 즐거움을 얻을 것이다.",
}


def get_item_text(item_number: int, lang: str = "en") -> str:
    """Get item text by item number and language."""
    if lang == "kr" and item_number in MINI_IPIP6_ITEMS_KR:
        return MINI_IPIP6_ITEMS_KR[item_number]
    return MINI_IPIP6_ITEMS.get(item_number, {}).get("text", "")


def get_trait_name(trait: str, lang: str = "en") -> str:
    """Get trait display name by language."""
    if lang == "kr":
        return TRAIT_NAMES_KR.get(trait, trait)
    return TRAIT_NAMES.get(trait, trait)


# Survey presentation order (1-24)
SURVEY_ORDER = list(range(1, 25))

# Item numbers sorted by presentation in the original questionnaire
ITEM_PRESENTATION_ORDER = [
    1, 2, 3, 4, 5, 6,      # Items 1-6
    7, 8, 9, 10, 11, 12,   # Items 7-12
    13, 14, 15, 16, 17, 18,  # Items 13-18
    19, 20, 21, 22, 23, 24   # Items 19-24
]


def get_item(item_number: int) -> Dict:
    """Get item data by item number."""
    return MINI_IPIP6_ITEMS.get(item_number)


def get_trait_items(trait: str) -> List[int]:
    """Get all item numbers for a trait."""
    return TRAIT_ITEMS.get(trait, [])


def get_items_for_trait(trait: str) -> List[Dict]:
    """Get all item data for a trait."""
    item_numbers = TRAIT_ITEMS.get(trait, [])
    return [MINI_IPIP6_ITEMS[n] for n in item_numbers]


def get_highest_discrimination_item(trait: str, exclude: List[int] = None) -> int:
    """Get the item with highest discrimination (alpha) for a trait."""
    exclude = exclude or []
    items = [
        (num, MINI_IPIP6_ITEMS[num]["alpha"])
        for num in TRAIT_ITEMS[trait]
        if num not in exclude
    ]
    if not items:
        return None
    return max(items, key=lambda x: x[1])[0]


def reverse_score(response: int) -> int:
    """Reverse score a response on 1-7 scale."""
    return 8 - response


def score_response(item_number: int, response: int) -> int:
    """Score a response, applying reverse scoring if needed."""
    if MINI_IPIP6_ITEMS[item_number]["reverse_scored"]:
        return reverse_score(response)
    return response
