# Project Structure

This document describes the complete project structure of the Psychological Assessment Chatbot.

## Overview

```
psychological/
├── backend/                    # Python FastAPI backend
│   ├── app/                   # Main application package
│   │   ├── core/             # Core modules (database, item data)
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── routers/          # API route handlers
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic (IRT, DOSE algorithm)
│   │   └── utils/            # Utility functions
│   ├── scripts/              # Analysis scripts (Monte Carlo simulation)
│   ├── tests/                # Test suite
│   └── requirements.txt      # Python dependencies
├── frontend/                  # Next.js React frontend
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # Reusable UI components
│   │   ├── context/          # React Context providers
│   │   └── lib/              # Utility libraries
│   └── package.json          # Node.js dependencies
├── docs/                      # Technical documentation
└── README.md                  # Project overview
```

---

## Backend Structure (`backend/`)

### Core (`backend/app/core/`)

| File | Purpose |
|------|---------|
| `database.py` | SQLAlchemy async engine and session management |
| `mini_ipip6_data.py` | Mini-IPIP6 item data with IRT parameters from Sibley (2012) |

### Models (`backend/app/models/`)

| File | Purpose |
|------|---------|
| `participant.py` | Participant model (demographics, condition order) |
| `session.py` | Assessment session model (survey/DOSE) |
| `response.py` | Individual item response model |
| `result.py` | Assessment result model (trait scores) |
| `satisfaction.py` | Satisfaction survey response model |

### Routers (`backend/app/routers/`)

| File | Endpoints | Purpose |
|------|-----------|---------|
| `participants.py` | `/api/participants/*` | Participant registration |
| `survey.py` | `/api/survey/*` | Traditional survey (G1) |
| `dose_chatbot.py` | `/api/dose/*` | DOSE adaptive chatbot (G3) |
| `results.py` | `/api/results/*` | Assessment results |
| `satisfaction.py` | `/api/satisfaction/*` | Satisfaction survey |
| `export.py` | `/api/export/*` | Data export (JSON/CSV) |

### Services (`backend/app/services/`)

| File | Purpose |
|------|---------|
| `irt_engine.py` | Graded Response Model (GRM) probability calculations |
| `bayesian_updater.py` | Bayesian posterior estimation for trait scores |
| `dose_algorithm.py` | DOSE adaptive item selection algorithm |
| `scoring_service.py` | Classical test theory scoring |
| `counterbalancing.py` | Condition order randomization |
| `llm_service.py` | OpenAI GPT-4 integration (for future use) |

### Scripts (`backend/scripts/`)

| File | Purpose |
|------|---------|
| `monte_carlo_simulation.py` | Validate DOSE vs Survey with 1,000 virtual participants |
| `analyze_results.py` | Multi-threshold analysis and report generation |

---

## Frontend Structure (`frontend/`)

### Pages (`frontend/src/app/`)

| Route | File | Purpose |
|-------|------|---------|
| `/` | `page.tsx` | Registration with language selection |
| `/assessment/[id]` | `page.tsx` | Assessment hub (shows condition order) |
| `/assessment/[id]/survey` | `survey/page.tsx` | Traditional survey interface |
| `/assessment/[id]/dose` | `dose/page.tsx` | DOSE chatbot interface |
| `/results/[id]` | `page.tsx` | Personality results with radar chart |
| `/satisfaction/[id]` | `page.tsx` | Satisfaction survey |
| `/admin` | `page.tsx` | Admin dashboard for data export |

### Components (`frontend/src/components/`)

| Directory | Files | Purpose |
|-----------|-------|---------|
| `chat/` | `ChatContainer.tsx`, `MessageBubble.tsx`, `TypingIndicator.tsx` | Chat interface components |
| `ui/` | `LikertScale.tsx` | 7-point Likert scale buttons |

### Libraries (`frontend/src/lib/`)

| File | Purpose |
|------|---------|
| `api.ts` | API client for backend communication |
| `i18n.ts` | Korean/English translations |
| `personality-descriptions.ts` | Trait descriptions for results page |

### Context (`frontend/src/context/`)

| File | Purpose |
|------|---------|
| `LanguageContext.tsx` | Language state management (Korean/English) |

---

## Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `DOSE_ALGORITHM.md` | Technical documentation of DOSE algorithm |
| `MONTE_CARLO_ANALYSIS.md` | Simulation validation results |
| `PROJECT_STRUCTURE.md` | This file |

---

## Configuration Files

| File | Purpose |
|------|---------|
| `backend/app/config.py` | Backend settings (database, DOSE parameters) |
| `frontend/tsconfig.json` | TypeScript configuration |
| `frontend/package.json` | Node.js dependencies |
| `.gitignore` | Git ignore patterns |

---

## Key Parameters

### DOSE Algorithm Settings (`backend/app/config.py`)

```python
DOSE_SE_THRESHOLD = 0.65    # Stop when SE < this value
DOSE_MAX_ITEMS_PER_TRAIT = 4  # Maximum items per trait
```

### IRT Parameters

- 24 items total (4 per trait)
- 6 HEXACO traits: Extraversion, Agreeableness, Conscientiousness, Neuroticism, Openness, Honesty-Humility
- Parameters from Sibley (2012) validation study
- Graded Response Model with 7-point Likert scale

---

## Database Schema

### SQLite Tables

```sql
participants (id, participant_code, age, gender, education_level,
              latin_square_row, condition_order, language, created_at)

assessment_sessions (id, participant_id, session_type, status,
                     current_theta, current_se, started_at, completed_at)

item_responses (id, session_id, item_number, response_value,
                theta_before, theta_after, se_before, se_after, response_time)

assessment_results (id, session_id, extraversion_score, ...,
                    total_items, duration_seconds)

satisfaction_responses (id, participant_id, overall_rating,
                        preferred_method, ease_of_use, would_recommend,
                        open_feedback, created_at)
```

---

## API Endpoints Summary

### Participants
- `POST /api/participants/register` - Register new participant
- `GET /api/participants/{id}` - Get participant details

### Survey (G1)
- `POST /api/survey/{id}/start` - Start survey session
- `GET /api/survey/{id}/items` - Get all 24 items
- `POST /api/survey/{id}/submit` - Submit all responses

### DOSE (G3)
- `POST /api/dose/{id}/start` - Start DOSE session
- `POST /api/dose/{id}/respond` - Submit response, get next item

### Results
- `GET /api/results/{id}` - Get assessment results
- `GET /api/results/{id}/compare` - Compare Survey vs DOSE

### Export
- `GET /api/export/participants` - Export all participants (JSON)
- `GET /api/export/participants/csv` - Export as CSV
- `GET /api/export/participant/{id}` - Export single participant

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: SQLAlchemy 2.0+ with async support
- **Scientific**: NumPy, SciPy (IRT calculations)
- **LLM**: OpenAI API (optional, for G4 Natural)

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Context + Zustand
- **Charts**: SVG-based radar chart

---

*Last Updated: December 2024*
