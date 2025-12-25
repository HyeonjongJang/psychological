# Psychological Assessment Chatbot

A research platform comparing traditional survey-based personality assessment with DOSE (Dynamic Optimization of Sequential Estimation) adaptive chatbot assessment using the Mini-IPIP6 scale.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Research Background](#research-background)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [DOSE Algorithm](#dose-algorithm)
- [Validation Results](#validation-results)
- [Data Export & Analysis](#data-export--analysis)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [References](#references)
- [License](#license)

---

## Overview

This platform enables researchers to compare two personality assessment methods:

| Method | Description | Items |
|--------|-------------|-------|
| **Survey (G1)** | Traditional 24-item Mini-IPIP6 questionnaire | Fixed 24 |
| **DOSE (G3)** | Adaptive chatbot using Item Response Theory | Dynamic (avg ~23) |

### Research Question

> Can adaptive chatbot interfaces conduct personality assessments more efficiently while maintaining accuracy compared to traditional surveys?

---

## Features

- **Bilingual Interface**: Full Korean and English support
- **Adaptive Testing**: DOSE algorithm dynamically selects optimal items based on responses
- **IRT-Based Scoring**: Bayesian posterior estimation using Graded Response Model
- **Real-time Precision**: Standard error tracking for each trait
- **Randomized Design**: Counterbalanced condition order (Survey-first or DOSE-first)
- **Comprehensive Results**: Radar chart visualization of personality profiles
- **Satisfaction Survey**: Post-assessment user experience measurement
- **Data Export**: CSV and JSON export for research analysis
- **Admin Dashboard**: Participant management and data download
- **Streamlit Dashboard**: Optional interactive data visualization

---

## Research Background

### Mini-IPIP6 Scale

The Mini-IPIP6 is a 24-item personality inventory measuring six HEXACO traits:

| Trait | Description | Items |
|-------|-------------|-------|
| Extraversion | Sociability, assertiveness, positive emotions | 4 |
| Agreeableness | Cooperation, trust, empathy | 4 |
| Conscientiousness | Organization, diligence, self-discipline | 4 |
| Neuroticism | Anxiety, emotional instability, moodiness | 4 |
| Openness | Imagination, curiosity, intellectual interests | 4 |
| Honesty-Humility | Sincerity, fairness, modesty | 4 |

### Item Response Theory (IRT)

This system uses IRT parameters from Sibley (2012) for:
- **Graded Response Model (GRM)**: Polytomous IRT model for 7-point Likert scales
- **Discrimination (α)**: How well each item differentiates trait levels (range: 0.54-1.47)
- **Thresholds (β)**: Category boundary parameters for each response option

### DOSE Algorithm

DOSE uses Bayesian adaptive testing to:
1. Initialize with N(0,1) prior for each trait
2. Select items maximizing Fisher Information
3. Update posterior after each response
4. Stop when precision threshold (SE < 0.65) is reached

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│                     (Next.js 14 + React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ Register │  │  Survey  │  │   DOSE   │  │   Results    │    │
│  │   Page   │  │   Page   │  │ Chatbot  │  │    Page      │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘    │
└───────┼─────────────┼─────────────┼───────────────┼────────────┘
        │             │             │               │
        ▼             ▼             ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REST API (FastAPI)                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │participants│ │   survey   │ │    dose    │ │  results   │   │
│  │   router   │ │   router   │ │   router   │ │   router   │   │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘   │
└────────┼──────────────┼──────────────┼──────────────┼──────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Services Layer                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ IRT Engine │ │  Bayesian  │ │    DOSE    │ │  Scoring   │   │
│  │   (GRM)    │ │  Updater   │ │ Algorithm  │ │  Service   │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database (SQLite/PostgreSQL)                  │
│  participants │ sessions │ responses │ results │ satisfaction   │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | Next.js (App Router) | 14.x |
| Frontend | React | 18.x |
| Frontend | TypeScript | 5.x |
| Frontend | Tailwind CSS | 3.x |
| Backend | Python | 3.9+ |
| Backend | FastAPI | 0.109+ |
| Backend | SQLAlchemy | 2.0+ |
| Backend | NumPy/SciPy | Latest |
| Database | SQLite (dev) / PostgreSQL (prod) | - |

---

## Installation

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn
- Git

### Clone Repository

```bash
git clone https://github.com/yourusername/psychological-assessment-chatbot.git
cd psychological-assessment-chatbot
```

### Backend Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install Python dependencies
pip install -r backend/requirements.txt

# Start development server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

### Verify Installation

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:3000

---

## Configuration

### Backend Configuration

Edit `backend/app/config.py`:

```python
class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Psychological Assessment Chatbot"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./psychological.db"
    # For PostgreSQL:
    # DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/psychological"

    # CORS - Add your frontend URL
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # DOSE Algorithm Parameters
    DOSE_SE_THRESHOLD: float = 0.65  # Stop when SE falls below this
    DOSE_MAX_ITEMS_PER_TRAIT: int = 4  # Maximum items per trait

    # OpenAI (optional, for future natural chatbot)
    OPENAI_API_KEY: Optional[str] = None
```

### Environment Variables

Create `.env` file in project root:

```env
# Database (production)
DATABASE_URL=postgresql+asyncpg://user:password@localhost/psychological

# OpenAI API (optional)
OPENAI_API_KEY=sk-your-api-key-here

# Debug mode
DEBUG=false
```

### Frontend Configuration

Edit `frontend/src/lib/api.ts` to change API base URL:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

---

## Usage

### User Flow

```
1. Registration (/)
   └── Select language (Korean/English)
   └── Enter demographics (age, gender)
   └── System assigns random condition order

2. Assessment Hub (/assessment/[id])
   └── View assigned order (Survey→DOSE or DOSE→Survey)
   └── Start first assessment

3. Survey Assessment (/assessment/[id]/survey)
   └── Answer all 24 items
   └── 7-point Likert scale (1-7)

4. DOSE Assessment (/assessment/[id]/dose)
   └── Chatbot presents items adaptively
   └── Stops when SE threshold reached
   └── Typically 20-24 items

5. Results Page (/results/[id])
   └── View personality radar chart
   └── Compare Survey vs DOSE scores
   └── Read trait descriptions

6. Satisfaction Survey (/satisfaction/[id])
   └── Rate overall experience
   └── Indicate preferred method
   └── Provide open feedback
```

### Admin Access

Access the admin dashboard at `/admin` to:
- View all participants
- Download data as CSV or JSON
- Monitor completion rates

---

## API Reference

### Participants

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/participants/register` | Register new participant |
| GET | `/api/participants/{id}` | Get participant details |

**Register Participant Request:**
```json
{
  "age": 25,
  "gender": "female",
  "language": "en"
}
```

**Response:**
```json
{
  "id": "uuid",
  "participant_code": "P001",
  "condition_order": ["survey", "dose"],
  "created_at": "2024-01-01T00:00:00"
}
```

### Survey

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/survey/{id}/start` | Start survey session |
| GET | `/api/survey/{id}/items` | Get all 24 items |
| POST | `/api/survey/{id}/submit` | Submit all responses |

### DOSE

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/dose/{id}/start` | Start DOSE session |
| POST | `/api/dose/{id}/respond` | Submit response, get next item |

**DOSE Response Request:**
```json
{
  "session_id": "uuid",
  "item_number": 1,
  "response": 5
}
```

**DOSE Response:**
```json
{
  "is_complete": false,
  "next_item": {
    "number": 7,
    "text": "Don't talk a lot.",
    "trait": "extraversion"
  },
  "current_estimates": {
    "extraversion": {"theta": 0.5, "se": 0.8, "items_administered": 1}
  }
}
```

### Results

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/results/{id}` | Get all assessment results |
| GET | `/api/results/{id}/compare` | Compare Survey vs DOSE |

### Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/participants` | Export all as JSON |
| GET | `/api/export/participants/csv` | Export all as CSV |
| GET | `/api/export/participant/{id}` | Export single participant |

---

## DOSE Algorithm

### Mathematical Foundation

#### Graded Response Model (GRM)

Cumulative probability of responding at or above category k:

```
P*(θ, k) = 1 / (1 + exp(-α × (θ - βₖ)))
```

Category response probability:

```
P(X = k | θ) = P*(θ, k) - P*(θ, k+1)
```

#### Bayesian Posterior Update

```
P(θ | R) ∝ L(θ | R) × π(θ)

where:
- π(θ) = N(0, 1) prior
- L(θ | R) = ∏ P(Xᵢ = rᵢ | θ)
```

#### Fisher Information

```
I(θ) = α² × Σₖ [(P*'ₖ - P*'ₖ₊₁)² / Pₖ]
```

#### Item Selection

Select item maximizing Fisher Information at current θ estimate:

```python
next_item = argmax_{item} I(θ̂, item)
```

#### Stopping Rule

Stop when Standard Error < threshold:

```
SE = √(Var(θ | responses)) < 0.65
```

### Algorithm Flowchart

```
START
  │
  ▼
Initialize θ = 0, SE = 1.0 for all traits
  │
  ▼
Select trait with highest SE (round-robin)
  │
  ▼
Select item with max Fisher Information
  │
  ▼
Present item to participant
  │
  ▼
Receive response (1-7)
  │
  ▼
Update Bayesian posterior
  │
  ▼
Compute new θ (EAP) and SE
  │
  ▼
All traits SE < 0.65? ──No──┐
  │                         │
  Yes                       │
  │                         │
  ▼                         │
 END ◄──────────────────────┘
```

---

## Validation Results

Monte Carlo simulation with 1,000 virtual participants:

### Accuracy vs Efficiency Trade-off

| SE Threshold | Survey-True r | DOSE-True r | Items Used | Reduction |
|:------------:|:-------------:|:-----------:|:----------:|:---------:|
| 0.30 | 0.729 | 0.730 | 24.0 / 24 | 0.0% |
| 0.50 | 0.729 | 0.736 | 24.0 / 24 | 0.0% |
| **0.65** | **0.729** | **0.726** | **22.9 / 24** | **4.7%** |
| 0.80 | 0.729 | 0.656 | 12.1 / 24 | 49.6% |

### Per-Trait Performance (SE < 0.65)

| Trait | Survey-True r | DOSE-True r | Avg Items |
|-------|:-------------:|:-----------:|:---------:|
| Extraversion | 0.755 | 0.735 | 4.00 |
| Agreeableness | 0.734 | 0.749 | 3.67 |
| Conscientiousness | 0.686 | 0.683 | 4.00 |
| Neuroticism | 0.689 | 0.681 | 4.00 |
| Openness | 0.738 | 0.740 | 3.92 |
| Honesty-Humility | 0.767 | 0.762 | 3.27 |

### Key Findings

1. **Strong Convergent Validity**: Both methods correlate highly with true scores (r ≈ 0.73)
2. **Equivalent Accuracy**: DOSE matches Survey accuracy at SE < 0.65
3. **Moderate Efficiency**: 4.7% item reduction at recommended threshold
4. **Trait Variability**: Honesty-Humility shows most efficiency (3.27 items avg)

### Limitations

The Mini-IPIP6 scale has moderate discrimination parameters (α = 0.54-1.47), which limits achievable precision. Higher efficiency gains would require items with stronger discrimination.

---

## Data Export & Analysis

### Export Formats

#### CSV Export

```bash
curl http://localhost:8000/api/export/participants/csv > data.csv
```

CSV includes:
- Participant demographics
- Survey scores (6 traits)
- DOSE scores (6 traits)
- DOSE standard errors
- Items administered
- Duration (seconds)
- Satisfaction ratings

#### JSON Export

```bash
curl http://localhost:8000/api/export/participants > data.json
```

### Streamlit Dashboard

Interactive data visualization:

```bash
# Install dependencies
pip install streamlit pandas plotly scipy

# Run dashboard
streamlit run streamlit_dashboard.py
```

Features:
- Upload exported CSV
- Trait correlation scatter plots
- Efficiency metrics visualization
- Satisfaction survey analysis

### Monte Carlo Simulation

Run validation simulation:

```bash
cd backend/scripts

# Run simulation (1,000 participants)
python monte_carlo_simulation.py

# Multi-threshold analysis
python analyze_results.py
```

Output files:
- `simulation_results.json`: Detailed metrics
- `analysis_report.md`: Formatted report

---

## Project Structure

```
psychological/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Settings
│   │   ├── core/
│   │   │   ├── database.py      # SQLAlchemy setup
│   │   │   └── mini_ipip6_data.py  # IRT parameters
│   │   ├── models/
│   │   │   ├── participant.py   # Participant model
│   │   │   ├── session.py       # Assessment session
│   │   │   ├── response.py      # Item responses
│   │   │   ├── result.py        # Assessment results
│   │   │   └── satisfaction.py  # Satisfaction survey
│   │   ├── routers/
│   │   │   ├── participants.py  # Registration API
│   │   │   ├── survey.py        # Survey API
│   │   │   ├── dose_chatbot.py  # DOSE API
│   │   │   ├── results.py       # Results API
│   │   │   ├── satisfaction.py  # Satisfaction API
│   │   │   └── export.py        # Data export API
│   │   ├── schemas/
│   │   │   ├── participant.py   # Pydantic schemas
│   │   │   ├── assessment.py
│   │   │   └── satisfaction.py
│   │   └── services/
│   │       ├── irt_engine.py    # GRM calculations
│   │       ├── bayesian_updater.py  # Posterior estimation
│   │       ├── dose_algorithm.py    # Adaptive testing
│   │       ├── scoring_service.py   # Classical scoring
│   │       └── counterbalancing.py  # Randomization
│   ├── scripts/
│   │   ├── monte_carlo_simulation.py
│   │   └── analyze_results.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Registration
│   │   │   ├── layout.tsx       # Root layout
│   │   │   ├── admin/page.tsx   # Admin dashboard
│   │   │   ├── assessment/[participantId]/
│   │   │   │   ├── page.tsx     # Assessment hub
│   │   │   │   ├── survey/page.tsx
│   │   │   │   └── dose/page.tsx
│   │   │   ├── results/[participantId]/page.tsx
│   │   │   └── satisfaction/[participantId]/page.tsx
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   └── TypingIndicator.tsx
│   │   │   └── ui/
│   │   │       └── LikertScale.tsx
│   │   ├── context/
│   │   │   └── LanguageContext.tsx
│   │   └── lib/
│   │       ├── api.ts           # API client
│   │       ├── i18n.ts          # Translations
│   │       └── personality-descriptions.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
├── docs/
│   ├── DOSE_ALGORITHM.md        # Technical documentation
│   ├── MONTE_CARLO_ANALYSIS.md  # Validation results
│   └── PROJECT_STRUCTURE.md     # Code organization
├── streamlit_dashboard.py       # Data visualization
├── streamlit_requirements.txt
├── .gitignore
└── README.md
```

---

## Production Deployment

### Backend (Docker)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Backend (Gunicorn)

```bash
pip install gunicorn
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Vercel)

```bash
cd frontend
npm run build
# Deploy to Vercel
vercel --prod
```

### Environment Variables (Production)

```env
DATABASE_URL=postgresql+asyncpg://user:pass@db-host/psychological
CORS_ORIGINS=["https://your-frontend-domain.com"]
DEBUG=false
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript strict mode for frontend
- Write tests for new features
- Update documentation as needed

---

## References

1. **Sibley, C. G. (2012)**. The Mini-IPIP6: Item Response Theory analysis of a short measure of the big-six factors of personality in New Zealand. *New Zealand Journal of Psychology*, 41(3), 21-31.

2. **Samejima, F. (1969)**. Estimation of latent ability using a response pattern of graded scores. *Psychometrika Monograph Supplement*, 34(4, Pt. 2), 100.

3. **van der Linden, W. J., & Glas, C. A. W. (2010)**. *Elements of Adaptive Testing*. Springer.

4. **Ashton, M. C., & Lee, K. (2007)**. Empirical, theoretical, and practical advantages of the HEXACO model of personality structure. *Personality and Social Psychology Review*, 11(2), 150-166.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Mini-IPIP6 scale and IRT parameters from Sibley (2012)
- FastAPI framework by Sebastián Ramírez
- Next.js framework by Vercel

---

*Developed for psychological research comparing survey and adaptive chatbot assessment methods.*

**Contact**: [lezelamu@naver.com]
**Repository**: [[GitHub URL](https://github.com/HyeonjongJang)]
