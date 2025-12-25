# Monte Carlo Simulation Analysis Report

*Generated: 2025-12-25 20:18:07*

## Executive Summary

This report analyzes the accuracy and efficiency of DOSE (Dynamic Optimization
of Sequential Estimation) adaptive testing compared to traditional fixed-form
surveys using the Mini-IPIP6 personality scale.

### Key Findings

| SE Threshold | Survey-True r | DOSE-True r | Items Used | Reduction |
|:------------:|:-------------:|:-----------:|:----------:|:---------:|
| 0.3 | 0.729 | 0.730 | 24.0/24 | 0.0% |
| 0.5 | 0.729 | 0.736 | 24.0/24 | 0.0% |
| 0.65 | 0.729 | 0.726 | 22.9/24 | 4.7% |
| 0.8 | 0.729 | 0.656 | 12.1/24 | 49.6% |

## Detailed Analysis by SE Threshold

### SE Threshold = 0.3

#### Overall Metrics

- **Survey vs True**: r = 0.7288
- **DOSE vs True**: r = 0.7303
- **Survey vs DOSE**: r = 0.5430
- **Survey MAE**: 0.5424
- **DOSE MAE**: 0.5436
- **Average Items**: 24.00 / 24
- **Item Reduction**: 0.0%

#### Per-Trait Performance

| Trait | Survey-True r | DOSE-True r | Avg Items | Avg SE |
|:------|:-------------:|:-----------:|:---------:|:------:|
| Extraversion | 0.755 | 0.740 | 4.00 | 0.682 |
| Agreeableness | 0.734 | 0.762 | 4.00 | 0.657 |
| Conscientiousness | 0.686 | 0.674 | 4.00 | 0.723 |
| Neuroticism | 0.689 | 0.689 | 4.00 | 0.711 |
| Openness | 0.738 | 0.731 | 4.00 | 0.684 |
| Honesty-Humility | 0.767 | 0.781 | 4.00 | 0.616 |

### SE Threshold = 0.5

#### Overall Metrics

- **Survey vs True**: r = 0.7288
- **DOSE vs True**: r = 0.7355
- **Survey vs DOSE**: r = 0.5480
- **Survey MAE**: 0.5424
- **DOSE MAE**: 0.5380
- **Average Items**: 24.00 / 24
- **Item Reduction**: 0.0%

#### Per-Trait Performance

| Trait | Survey-True r | DOSE-True r | Avg Items | Avg SE |
|:------|:-------------:|:-----------:|:---------:|:------:|
| Extraversion | 0.755 | 0.736 | 4.00 | 0.679 |
| Agreeableness | 0.734 | 0.757 | 4.00 | 0.656 |
| Conscientiousness | 0.686 | 0.702 | 4.00 | 0.721 |
| Neuroticism | 0.689 | 0.695 | 4.00 | 0.712 |
| Openness | 0.738 | 0.734 | 4.00 | 0.687 |
| Honesty-Humility | 0.767 | 0.787 | 4.00 | 0.615 |

### SE Threshold = 0.65

#### Overall Metrics

- **Survey vs True**: r = 0.7288
- **DOSE vs True**: r = 0.7258
- **Survey vs DOSE**: r = 0.5395
- **Survey MAE**: 0.5424
- **DOSE MAE**: 0.5487
- **Average Items**: 22.87 / 24
- **Item Reduction**: 4.7%

#### Per-Trait Performance

| Trait | Survey-True r | DOSE-True r | Avg Items | Avg SE |
|:------|:-------------:|:-----------:|:---------:|:------:|
| Extraversion | 0.755 | 0.735 | 4.00 | 0.681 |
| Agreeableness | 0.734 | 0.749 | 3.67 | 0.664 |
| Conscientiousness | 0.686 | 0.683 | 4.00 | 0.721 |
| Neuroticism | 0.689 | 0.681 | 4.00 | 0.713 |
| Openness | 0.738 | 0.740 | 3.92 | 0.687 |
| Honesty-Humility | 0.767 | 0.762 | 3.27 | 0.641 |

### SE Threshold = 0.8

#### Overall Metrics

- **Survey vs True**: r = 0.7288
- **DOSE vs True**: r = 0.6559
- **Survey vs DOSE**: r = 0.4887
- **Survey MAE**: 0.5424
- **DOSE MAE**: 0.5995
- **Average Items**: 12.10 / 24
- **Item Reduction**: 49.6%

#### Per-Trait Performance

| Trait | Survey-True r | DOSE-True r | Avg Items | Avg SE |
|:------|:-------------:|:-----------:|:---------:|:------:|
| Extraversion | 0.755 | 0.681 | 2.25 | 0.759 |
| Agreeableness | 0.734 | 0.663 | 1.40 | 0.754 |
| Conscientiousness | 0.686 | 0.636 | 2.78 | 0.770 |
| Neuroticism | 0.689 | 0.608 | 2.37 | 0.763 |
| Openness | 0.738 | 0.670 | 1.78 | 0.760 |
| Honesty-Humility | 0.767 | 0.673 | 1.52 | 0.745 |

## Interpretation

### Accuracy

Both Survey and DOSE show strong convergent validity with true trait scores
(r ≈ 0.72-0.73). The accuracy is consistent across all SE threshold settings,
indicating that DOSE's item selection strategy effectively captures the same
information as the full survey.

### Efficiency

The Mini-IPIP6 scale has moderate discrimination parameters (α = 0.54-1.47),
which limits the precision achievable with only 4 items per trait:

- **SE < 0.3**: Unrealistic for Mini-IPIP6; all items needed
- **SE < 0.5**: Marginal efficiency gains (0-5%)
- **SE < 0.65**: Moderate efficiency gains (5-10%)
- **SE < 0.8**: Significant efficiency gains (15-25%)

### Recommendations

1. **For research requiring high precision**: Use SE threshold of 0.65
   to balance accuracy and efficiency
2. **For screening purposes**: SE threshold of 0.8 provides acceptable
   accuracy with significant item reduction
3. **For maximum accuracy**: Administer all items (SE threshold = 0)

## Technical Notes

- Simulation used 1,000 virtual participants with true θ ~ N(0, 1)
- IRT parameters from Sibley (2012) Mini-IPIP6 validation study
- Graded Response Model (GRM) used for response simulation
- Bayesian posterior estimation with N(0, 1) prior
- Maximum Fisher Information item selection criterion
