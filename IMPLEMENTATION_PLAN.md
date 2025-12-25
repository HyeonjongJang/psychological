# Implementation Plan - Psychological Assessment Chatbot

This document outlines the required modifications in implementation order.

---

## Step 1: Simplify Assessment Types (Survey & DOSE Only)

**Goal:** Remove Static and Natural chatbot options, keep only Original Survey (G1) and DOSE (G3).

### Files to Modify:

| File | Changes |
|------|---------|
| `backend/app/models/session.py` | Remove `STATIC` and `NATURAL` from `SessionType` enum |
| `backend/app/services/counterbalancing.py` | Update `CONDITION_ORDER` to only include `["survey", "dose"]` |
| `backend/app/main.py` | Remove router imports for `static_chatbot` and `natural_chatbot` |
| `frontend/src/app/assessment/[participantId]/page.tsx` | Update `CONDITION_INFO` to only show survey and dose |
| `frontend/src/app/page.tsx` | Update description to mention only 2 assessment types |

### Functions to Modify:
- `get_latin_square_order()` in `counterbalancing.py` - Reduce to 2x2 Latin Square
- `AssessmentHub` component - Remove static/natural cards

---

## Step 2: Randomize Survey vs DOSE Order

**Goal:** Each participant randomly gets either Survey-first or DOSE-first order.

### Files to Modify:

| File | Changes |
|------|---------|
| `backend/app/services/counterbalancing.py` | Implement random 2-condition assignment |

### Functions to Add/Modify:
```python
# counterbalancing.py
def get_randomized_order() -> List[str]:
    """Randomly assign order: either ['survey', 'dose'] or ['dose', 'survey']"""
    import random
    order = ["survey", "dose"]
    random.shuffle(order)
    return order
```

---

## Step 3: Add Language Selection (Korean/English)

**Goal:** User selects language at start; all UI and questions display in chosen language.

### Files to Create:

| File | Purpose |
|------|---------|
| `frontend/src/lib/i18n.ts` | Translation strings for KR/EN |
| `frontend/src/context/LanguageContext.tsx` | Language state management |

### Files to Modify:

| File | Changes |
|------|---------|
| `backend/app/core/mini_ipip6_data.py` | Add Korean translations for all 24 items |
| `frontend/src/app/page.tsx` | Add language selection buttons before registration |
| `frontend/src/components/ui/LikertScale.tsx` | Use translated labels |
| All page components | Wrap text in translation function |

### Data to Add:
```python
# mini_ipip6_data.py - Add Korean translations
MINI_IPIP6_ITEMS_KR = {
    1: {"text": "나는 파티의 분위기 메이커이다.", ...},
    2: {"text": "나는 다른 사람들의 감정에 공감한다.", ...},
    # ... all 24 items
}
```

---

## Step 4: Improve Chatbot Tone (Polite/Friendly)

**Goal:** Make chatbot responses polite and friendly like standard GPT.

### Files to Modify:

| File | Changes |
|------|---------|
| `backend/app/routers/dose_chatbot.py` | Update welcome message and item presentation |
| `backend/app/routers/survey.py` | Add friendly instructions |
| `frontend/src/app/assessment/[participantId]/dose/page.tsx` | Update message formatting |

### Messages to Update:
```typescript
// Current: "I am the life of the party."
// New (EN): "Here's the next statement about yourself:\n\n\"I am the life of the party.\"\n\nPlease rate how accurately this describes you."
// New (KR): "다음 문장이 본인을 얼마나 잘 설명하는지 평가해 주세요:\n\n\"나는 파티의 분위기 메이커이다.\"\n\n1(매우 부정확)부터 7(매우 정확)까지 선택해 주세요."
```

---

## Step 5: Display Personality Results on Final Page

**Goal:** After completing both assessments, show user their personality profile.

### Files to Modify:

| File | Changes |
|------|---------|
| `frontend/src/app/results/[participantId]/page.tsx` | Add personality interpretation text |
| `frontend/src/lib/personality-descriptions.ts` | Create (new file with trait descriptions) |

### Functions to Add:
```typescript
// personality-descriptions.ts
export function getTraitDescription(trait: string, score: number, lang: 'en' | 'kr'): string {
    // Returns human-readable description based on score level
    // e.g., score > 5 = "You are highly extraverted..."
}
```

---

## Step 6: Add Satisfaction Survey

**Goal:** After viewing results, participant completes a brief satisfaction survey.

### Files to Create:

| File | Purpose |
|------|---------|
| `frontend/src/app/satisfaction/[participantId]/page.tsx` | Satisfaction survey page |
| `backend/app/routers/satisfaction.py` | API endpoint to save satisfaction responses |
| `backend/app/models/satisfaction.py` | Database model for satisfaction data |

### Survey Questions:
1. Overall experience rating (1-5 stars)
2. Which method did you prefer? (Survey / DOSE)
3. Was the DOSE chatbot easy to use? (1-7 Likert)
4. Would you recommend this to others? (1-7 Likert)
5. Open feedback (text)

---

## Step 7: Save All Data Locally

**Goal:** Export all session data to local JSON/CSV files.

### Files to Create:

| File | Purpose |
|------|---------|
| `backend/app/routers/export.py` | Data export endpoints |
| `frontend/src/app/admin/page.tsx` | Admin page for data download |

### Data to Export:
```json
{
  "participant": {
    "id": "...",
    "age": 25,
    "gender": "female",
    "language": "kr",
    "condition_order": ["dose", "survey"]
  },
  "sessions": [
    {
      "type": "dose",
      "start_time": "...",
      "end_time": "...",
      "duration_seconds": 180,
      "items_administered": 12,
      "responses": [...],
      "final_scores": {...}
    }
  ],
  "satisfaction": {...}
}
```

### Functions to Add:
```python
# export.py
@router.get("/export/participant/{participant_id}")
async def export_participant_data(participant_id: str) -> FileResponse:
    """Export all data for a participant as JSON"""

@router.get("/export/all")
async def export_all_data() -> FileResponse:
    """Export all participants data as CSV"""
```

---

## Step 8: Create DOSE Algorithm Documentation

**Goal:** Document how DOSE works for research transparency.

### Files to Create:

| File | Purpose |
|------|---------|
| `docs/DOSE_ALGORITHM.md` | Technical documentation of DOSE |

### Content Outline:
1. Overview of Item Response Theory (IRT)
2. Graded Response Model (GRM) equations
3. Bayesian posterior estimation
4. Fisher Information for item selection
5. Stopping rule (SE < 0.3)
6. Pseudocode and flowchart

---

## Step 9: Monte Carlo Simulation for Performance Evaluation

**Goal:** Validate DOSE efficiency with simulated virtual respondents.

### Files to Create:

| File | Purpose |
|------|---------|
| `backend/scripts/monte_carlo_simulation.py` | Simulation script |
| `backend/scripts/analyze_results.py` | Result analysis and visualization |

### Simulation Design:
```python
def run_simulation(n_virtual_respondents: int = 1000):
    """
    1. Generate 1000 virtual respondents with known true theta values
    2. Simulate responses based on IRT probabilities
    3. Run DOSE algorithm on each virtual respondent
    4. Compare estimated theta vs true theta
    5. Calculate: accuracy (correlation), efficiency (avg items), precision (SE)
    """
```

### Metrics to Calculate:
- Pearson r between estimated and true scores
- Mean Absolute Error (MAE)
- Average items administered
- Item reduction rate vs full 24-item survey

---

## Step 10: Final Integration & Testing

**Goal:** Ensure all components work together.

### Testing Checklist:
- [ ] Language toggle works throughout app
- [ ] Random order assignment works
- [ ] DOSE stops correctly at SE < 0.3
- [ ] Results display correctly in both languages
- [ ] Satisfaction survey saves data
- [ ] Data export produces valid JSON/CSV
- [ ] Monte Carlo simulation runs successfully

---

## Implementation Priority Order

| Priority | Step | Complexity | Dependencies |
|----------|------|------------|--------------|
| 1 | Step 1 (Simplify to Survey+DOSE) | Low | None |
| 2 | Step 2 (Random order) | Low | Step 1 |
| 3 | Step 4 (Polite tone) | Low | None |
| 4 | Step 3 (KR/EN language) | Medium | None |
| 5 | Step 5 (Show results) | Low | Step 3 |
| 6 | Step 6 (Satisfaction survey) | Medium | Step 5 |
| 7 | Step 7 (Local data export) | Medium | Step 6 |
| 8 | Step 8 (DOSE documentation) | Low | None |
| 9 | Step 9 (Monte Carlo) | High | Step 8 |
| 10 | Step 10 (Final testing) | Medium | All |
