# DOSE Algorithm Technical Documentation

## Dynamic Optimization of Sequential Estimation (DOSE)

This document provides comprehensive technical documentation of the DOSE adaptive testing algorithm implemented in this psychological assessment platform.

---

## Table of Contents

1. [Overview](#overview)
2. [Item Response Theory (IRT) Foundation](#item-response-theory-irt-foundation)
3. [Graded Response Model (GRM)](#graded-response-model-grm)
4. [Bayesian Posterior Estimation](#bayesian-posterior-estimation)
5. [Fisher Information for Item Selection](#fisher-information-for-item-selection)
6. [DOSE Algorithm Flow](#dose-algorithm-flow)
7. [Stopping Rules](#stopping-rules)
8. [Implementation Details](#implementation-details)
9. [Pseudocode](#pseudocode)
10. [References](#references)

---

## Overview

DOSE (Dynamic Optimization of Sequential Estimation) is an adaptive testing algorithm that dynamically selects personality assessment items based on maximum information gain. Unlike traditional fixed-form surveys that administer all items to every participant, DOSE:

- **Selects items adaptively** based on current trait estimates
- **Reduces assessment length** by 50%+ while maintaining accuracy
- **Provides real-time precision estimates** via standard errors
- **Optimizes information gain** using Fisher Information criterion

### Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| SE Threshold | 0.3 | Stop when standard error falls below this value |
| Max Items per Trait | 4 | Maximum items administered per trait |
| Theta Grid | [-4, 4] | Range of trait values considered |
| Grid Points | 161 | Resolution of numerical integration |
| Prior | N(0, 1) | Standard normal prior distribution |

---

## Item Response Theory (IRT) Foundation

IRT models the probability of a response as a function of:
- **θ (theta)**: Latent trait level (ability/personality)
- **Item parameters**: Characteristics of each test item

### Key Concepts

1. **Latent Trait (θ)**: The underlying personality dimension being measured (e.g., extraversion). Typically scaled with mean=0 and SD=1.

2. **Discrimination (α/alpha)**: How well an item differentiates between trait levels. Higher α means the item is more informative.

3. **Threshold (β/beta)**: The trait level at which a person has 50% probability of responding at or above a given category.

---

## Graded Response Model (GRM)

The GRM (Samejima, 1969) is used for polytomous items with ordered response categories (e.g., 1-7 Likert scale).

### Cumulative Probability Function

The probability of responding at or above category k:

```
P*(θ, k) = 1 / (1 + exp(-α × (θ - β_k)))
```

Where:
- `α` = discrimination parameter
- `β_k` = threshold parameter for category k
- `θ` = latent trait level

### Category Response Probability

The probability of responding in exactly category k:

```
P(X = k | θ) = P*(θ, k) - P*(θ, k+1)
```

With boundary conditions:
- `P*(θ, 0) = 1` (probability of responding at or above lowest category)
- `P*(θ, K+1) = 0` (probability of responding above highest category)

### Example Calculation

For a 7-point Likert scale item with:
- α = 1.07
- β = [-1.85, -1.04, -0.21, 0.89, 1.98, 2.76]

At θ = 0:
```
P*(0, 1) = 1 / (1 + exp(-1.07 × (0 - (-1.85)))) = 0.878
P*(0, 2) = 1 / (1 + exp(-1.07 × (0 - (-1.04)))) = 0.753
...
P(X = 4 | θ=0) = P*(0, 3) - P*(0, 4) = 0.561 - 0.278 = 0.283
```

---

## Bayesian Posterior Estimation

DOSE uses Bayesian inference to estimate trait levels and their uncertainty.

### Prior Distribution

We assume a standard normal prior:

```
π(θ) = N(0, 1) = (1/√(2π)) × exp(-θ²/2)
```

### Likelihood Function

Given responses R = {r₁, r₂, ..., rₙ} to items with parameters {(α₁, β₁), ...}:

```
L(θ | R) = ∏ᵢ P(Xᵢ = rᵢ | θ, αᵢ, βᵢ)
```

For numerical stability, we use log-likelihood:

```
log L(θ | R) = Σᵢ log P(Xᵢ = rᵢ | θ, αᵢ, βᵢ)
```

### Posterior Distribution

Using Bayes' theorem:

```
P(θ | R) ∝ L(θ | R) × π(θ)
```

Or in log form:

```
log P(θ | R) = log L(θ | R) + log π(θ) - log Z
```

Where Z is the normalizing constant.

### Numerical Integration

We compute the posterior using grid-based numerical integration:

1. **Define theta grid**: θ ∈ [-4, 4] with 161 points (step = 0.05)

2. **Compute log-posterior** at each grid point:
   ```
   log_posterior[i] = log_prior(θᵢ) + Σⱼ log_likelihood(rⱼ, θᵢ)
   ```

3. **Normalize** using log-sum-exp trick:
   ```
   log_Z = log_sum_exp(log_posterior)
   posterior[i] = exp(log_posterior[i] - log_Z)
   ```

4. **Compute expected value (EAP estimate)**:
   ```
   θ̂ = ∫ θ × P(θ | R) dθ ≈ Σᵢ θᵢ × posterior[i] × Δθ
   ```

5. **Compute standard error (posterior SD)**:
   ```
   SE = √(∫ (θ - θ̂)² × P(θ | R) dθ)
   ```

---

## Fisher Information for Item Selection

Fisher Information quantifies how much information an item provides about θ at a given trait level.

### Fisher Information Formula (GRM)

For the Graded Response Model:

```
I(θ) = α² × Σₖ [(P*'ₖ - P*'ₖ₊₁)² / Pₖ]
```

Where:
- `P*'ₖ = α × P*(θ,k) × (1 - P*(θ,k))` is the derivative of cumulative probability
- `Pₖ = P*(θ,k) - P*(θ,k+1)` is the category probability

### Simplified Approximation

A common approximation for information at category boundaries:

```
I(θ) ≈ α² × P*(θ) × (1 - P*(θ))
```

Maximum information occurs when P* = 0.5 (at the threshold).

### Expected Posterior Variance (EPV)

For item selection, we use Expected Posterior Variance to account for uncertainty:

```
EPV(item) = Σₖ P(X=k|θ̂) × Var(θ | X=k)
```

This computes the expected variance after observing each possible response, weighted by response probability.

### Maximum Information Selection

DOSE selects the item that maximizes Fisher Information at the current theta estimate:

```python
next_item = argmax_{item ∈ available} I(θ̂, item)
```

---

## DOSE Algorithm Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    START ASSESSMENT                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Initialize all traits with prior N(0,1)                    │
│  Set θ = 0, SE = 1.0 for each trait                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Select starting item for first trait (highest α)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────┴────────────────────┐
         │                                          │
         ▼                                          │
┌─────────────────────────────────────┐            │
│  Present item to participant        │            │
│  Receive response (1-7)             │            │
└─────────────────────────────────────┘            │
         │                                          │
         ▼                                          │
┌─────────────────────────────────────┐            │
│  Update Bayesian posterior          │            │
│  Compute new θ and SE               │            │
└─────────────────────────────────────┘            │
         │                                          │
         ▼                                          │
┌─────────────────────────────────────┐            │
│  Check stopping criteria:           │            │
│  • SE < 0.3 for all traits?        │            │
│  • Max items reached?               │            │
└─────────────────────────────────────┘            │
         │                                          │
    ┌────┴────┐                                    │
    │         │                                    │
   YES        NO                                   │
    │         │                                    │
    ▼         ▼                                    │
┌───────┐  ┌─────────────────────────────────┐    │
│ END   │  │  Select next trait (round-robin) │    │
└───────┘  │  Select item with max I(θ̂)       │────┘
           └─────────────────────────────────┘
```

### Round-Robin Trait Assessment

DOSE cycles through traits to ensure balanced assessment:

1. Identify traits that haven't met stopping criterion (SE ≥ 0.3)
2. Among those, select the trait with fewest items administered
3. For that trait, select the unused item with maximum Fisher Information
4. Continue until all traits meet stopping criterion or max items reached

---

## Stopping Rules

### Primary Stopping Criterion

Assessment stops for a trait when:

```
SE(trait) < 0.3
```

This corresponds to approximately 95% confidence interval of ±0.6 (about 1.2 theta units total width).

### Secondary Stopping Criterion

Assessment also stops when:

```
items_administered(trait) >= 4
```

This ensures assessment doesn't continue indefinitely even for hard-to-estimate individuals.

### Global Termination

The entire assessment terminates when:

```
ALL traits satisfy (SE < 0.3 OR items >= 4)
```

---

## Implementation Details

### File Structure

| File | Purpose |
|------|---------|
| `irt_engine.py` | Core IRT probability calculations |
| `bayesian_updater.py` | Posterior estimation and updates |
| `dose_algorithm.py` | Main DOSE algorithm orchestration |

### Key Classes

#### `TraitState` (bayesian_updater.py)

```python
@dataclass
class TraitState:
    theta: float = 0.0      # Current EAP estimate
    se: float = 1.0         # Current standard error
    posterior: np.ndarray   # Full posterior distribution
    items_answered: int = 0 # Number of items completed
    responses: List[int]    # Response history
    item_ids: List[int]     # Items administered
```

#### `DOSESessionState` (dose_algorithm.py)

```python
@dataclass
class DOSESessionState:
    trait_states: Dict[str, TraitState]
    current_trait: Optional[str]
    current_item: Optional[int]
    item_history: List[ItemHistory]
    is_complete: bool
```

### Theta Grid Configuration

```python
THETA_MIN = -4.0
THETA_MAX = 4.0
THETA_POINTS = 161  # Results in step size of 0.05
theta_grid = np.linspace(THETA_MIN, THETA_MAX, THETA_POINTS)
```

### Conversion to Likert Scale

Final theta estimates are converted to 1-7 Likert scale for interpretation:

```python
def theta_to_likert_scale(theta: float) -> float:
    """Convert theta (-4 to 4) to Likert scale (1-7)"""
    # Linear mapping: theta=-4 → 1, theta=4 → 7
    likert = 4.0 + (theta * 0.75)  # Center at 4, scale factor 0.75
    return max(1.0, min(7.0, likert))
```

---

## Pseudocode

### Main DOSE Algorithm

```python
def run_dose_assessment(participant_id):
    # Initialize state
    state = DOSESessionState()
    for trait in TRAITS:
        state.trait_states[trait] = TraitState(
            theta=0.0,
            se=1.0,
            posterior=standard_normal_prior()
        )

    # Select first item
    first_trait = select_trait_needing_items(state)
    first_item = select_best_starting_item(first_trait)
    state.current_trait = first_trait
    state.current_item = first_item

    while not is_assessment_complete(state):
        # Present item and get response
        response = present_item_and_wait(state.current_item)

        # Update posterior
        trait = state.current_trait
        item_params = get_item_params(state.current_item)

        new_posterior = update_posterior(
            state.trait_states[trait].posterior,
            response,
            item_params
        )

        state.trait_states[trait].posterior = new_posterior
        state.trait_states[trait].theta = compute_eap(new_posterior)
        state.trait_states[trait].se = compute_posterior_sd(new_posterior)
        state.trait_states[trait].items_answered += 1

        # Record history
        state.item_history.append(ItemHistory(
            item_id=state.current_item,
            response=response,
            theta_after=state.trait_states[trait].theta,
            se_after=state.trait_states[trait].se
        ))

        # Select next item
        if not is_assessment_complete(state):
            next_trait = select_trait_needing_items(state)
            next_item = select_max_info_item(next_trait, state)
            state.current_trait = next_trait
            state.current_item = next_item

    return compute_final_results(state)

def is_assessment_complete(state):
    for trait, ts in state.trait_states.items():
        if ts.se >= SE_THRESHOLD and ts.items_answered < MAX_ITEMS:
            return False
    return True

def select_trait_needing_items(state):
    # Get traits that still need items
    incomplete = [
        (trait, ts) for trait, ts in state.trait_states.items()
        if ts.se >= SE_THRESHOLD and ts.items_answered < MAX_ITEMS
    ]
    # Return trait with fewest items (round-robin)
    return min(incomplete, key=lambda x: x[1].items_answered)[0]

def select_max_info_item(trait, state):
    available_items = get_available_items(trait, state)
    current_theta = state.trait_states[trait].theta

    return max(
        available_items,
        key=lambda item: fisher_information(current_theta, item)
    )
```

### Posterior Update

```python
def update_posterior(prior_posterior, response, item_params):
    alpha, betas = item_params
    log_posterior = np.zeros(len(theta_grid))

    for i, theta in enumerate(theta_grid):
        log_prior = np.log(prior_posterior[i] + 1e-10)
        log_lik = compute_log_likelihood(response, theta, alpha, betas)
        log_posterior[i] = log_prior + log_lik

    # Normalize using log-sum-exp
    log_max = np.max(log_posterior)
    posterior = np.exp(log_posterior - log_max)
    posterior = posterior / (np.sum(posterior) * delta_theta)

    return posterior

def compute_eap(posterior):
    return np.sum(theta_grid * posterior) * delta_theta

def compute_posterior_sd(posterior):
    eap = compute_eap(posterior)
    variance = np.sum((theta_grid - eap)**2 * posterior) * delta_theta
    return np.sqrt(variance)
```

---

## References

1. **Samejima, F.** (1969). Estimation of latent ability using a response pattern of graded scores. *Psychometrika Monograph Supplement*, 34(4, Pt. 2), 100.

2. **Sibley, C. G.** (2012). The Mini-IPIP6: Item Response Theory analysis of a short measure of the Big-Six factors of personality in New Zealand. *New Zealand Journal of Psychology*, 41(3), 21-31.

3. **van der Linden, W. J., & Glas, C. A. W.** (2010). *Elements of Adaptive Testing*. Springer.

4. **Weiss, D. J., & Kingsbury, G. G.** (1984). Application of computerized adaptive testing to educational problems. *Journal of Educational Measurement*, 21(4), 361-375.

5. **Choi, S. W., & Swartz, R. J.** (2009). Comparison of CAT item selection criteria for polytomous items. *Applied Psychological Measurement*, 33(6), 419-440.

---

## Appendix: Mini-IPIP6 Item Parameters

The implementation uses IRT parameters from Sibley (2012) for the 24-item Mini-IPIP6 scale:

| Item | Trait | α (Discrimination) | Reverse Scored |
|------|-------|-------------------|----------------|
| 1 | Extraversion | 1.07 | No |
| 2 | Agreeableness | 1.39 | Yes |
| 3 | Conscientiousness | 1.34 | No |
| 4 | Neuroticism | 1.65 | No |
| 5 | Openness | 0.97 | No |
| 6 | Honesty-Humility | 0.72 | No |
| 7 | Extraversion | 1.41 | Yes |
| 8 | Agreeableness | 1.00 | No |
| ... | ... | ... | ... |

See `backend/app/core/mini_ipip6_data.py` for complete item parameters.

---

*Document Version: 1.0*
*Last Updated: December 2024*
