# Deployment Guide

This guide covers deploying the Psychological Assessment Chatbot to various platforms.

## Project Structure

```
psychological/
├── backend/          # FastAPI application
│   ├── app/
│   └── requirements.txt
├── frontend/         # Next.js application
│   ├── src/
│   └── package.json
└── data/             # SQLite database (created at runtime)
```

---

## Option 1: Deploy to Railway (Recommended)

Railway provides easy deployment for both FastAPI and Next.js with automatic HTTPS.

### Backend Deployment

1. Create a new project on [Railway](https://railway.app)

2. Connect your GitHub repository

3. Add a new service from your repo, select the `backend` directory

4. Set environment variables:
   ```
   DATABASE_URL=sqlite+aiosqlite:///./data/psychological.db
   CORS_ORIGINS=["https://your-frontend-url.railway.app"]
   ```

5. Railway will auto-detect FastAPI and deploy

### Frontend Deployment

1. Add another service from the same repo, select `frontend` directory

2. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```

3. Add to `next.config.mjs`:
   ```javascript
   async rewrites() {
     return [
       {
         source: '/api/:path*',
         destination: 'https://your-backend-url.railway.app/api/:path*',
       },
     ];
   }
   ```

---

## Option 2: Deploy to Vercel (Frontend) + Render (Backend)

### Backend on Render

1. Create account on [Render](https://render.com)

2. Create a new Web Service from your GitHub repo

3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Add environment variables in Render dashboard

### Frontend on Vercel

1. Import project to [Vercel](https://vercel.com)

2. Set root directory to `frontend`

3. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-render-url.onrender.com
   ```

4. Update `next.config.mjs` with API rewrite rules

---

## Option 3: Local Development with Docker

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/psychological.db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
```

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

---

## Option 4: Streamlit Data Analysis Dashboard

If you want to create a Streamlit app for analyzing exported data:

### Create `streamlit_dashboard.py`

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

st.set_page_config(
    page_title="Psychological Assessment Analysis",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Psychological Assessment Data Analysis")

# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.header("Data Overview")
    st.write(f"Total participants: {len(df)}")

    # Filter completed participants
    completed = df[(df['survey_completed'] == True) & (df['dose_completed'] == True)]
    st.write(f"Completed both assessments: {len(completed)}")

    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["Trait Comparison", "Correlation", "Efficiency", "Demographics"])

    with tab1:
        st.subheader("Survey vs DOSE Trait Scores")
        traits = ['extraversion', 'agreeableness', 'conscientiousness',
                  'neuroticism', 'openness', 'honesty_humility']

        for trait in traits:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.scatter(
                    completed,
                    x=f'survey_{trait}',
                    y=f'dose_{trait}',
                    title=f'{trait.title()}',
                    labels={f'survey_{trait}': 'Survey', f'dose_{trait}': 'DOSE'}
                )
                fig.add_trace(go.Scatter(x=[1,7], y=[1,7], mode='lines', name='Perfect Agreement'))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Calculate correlation
                if len(completed) > 2:
                    r, p = stats.pearsonr(
                        completed[f'survey_{trait}'].dropna(),
                        completed[f'dose_{trait}'].dropna()
                    )
                    st.metric(f"{trait.title()} Correlation", f"r = {r:.3f}", f"p = {p:.4f}")

    with tab2:
        st.subheader("Overall Correlation Analysis")
        if len(completed) > 2:
            survey_cols = [f'survey_{t}' for t in traits]
            dose_cols = [f'dose_{t}' for t in traits]

            survey_scores = completed[survey_cols].values.flatten()
            dose_scores = completed[dose_cols].values.flatten()

            valid_mask = ~(pd.isna(survey_scores) | pd.isna(dose_scores))
            r, p = stats.pearsonr(survey_scores[valid_mask], dose_scores[valid_mask])

            st.metric("Overall Pearson r", f"{r:.3f}", f"p < 0.001" if p < 0.001 else f"p = {p:.4f}")

            # MAE
            mae = abs(survey_scores[valid_mask] - dose_scores[valid_mask]).mean()
            st.metric("Mean Absolute Error", f"{mae:.3f}")

    with tab3:
        st.subheader("Efficiency Metrics")
        col1, col2 = st.columns(2)

        with col1:
            avg_survey_items = completed['survey_items'].mean()
            avg_dose_items = completed['dose_items'].mean()
            st.metric("Avg Survey Items", f"{avg_survey_items:.1f}")
            st.metric("Avg DOSE Items", f"{avg_dose_items:.1f}")
            if avg_survey_items > 0:
                reduction = (1 - avg_dose_items/avg_survey_items) * 100
                st.metric("Item Reduction", f"{reduction:.1f}%")

        with col2:
            avg_survey_time = completed['survey_duration_seconds'].mean() / 60
            avg_dose_time = completed['dose_duration_seconds'].mean() / 60
            st.metric("Avg Survey Time", f"{avg_survey_time:.1f} min")
            st.metric("Avg DOSE Time", f"{avg_dose_time:.1f} min")

    with tab4:
        st.subheader("Demographics")
        col1, col2 = st.columns(2)

        with col1:
            fig = px.histogram(df, x='age', title='Age Distribution')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(df, names='gender', title='Gender Distribution')
            st.plotly_chart(fig, use_container_width=True)

    # Satisfaction Survey Analysis
    if 'satisfaction_completed' in df.columns:
        st.header("Satisfaction Survey Results")
        sat_completed = df[df['satisfaction_completed'] == True]

        if len(sat_completed) > 0:
            col1, col2, col3 = st.columns(3)

            with col1:
                avg_rating = sat_completed['satisfaction_overall_rating'].mean()
                st.metric("Avg Overall Rating", f"{avg_rating:.2f}/5")

            with col2:
                preferred = sat_completed['satisfaction_preferred_method'].value_counts()
                st.write("Preferred Method:")
                st.write(preferred)

            with col3:
                avg_ease = sat_completed['satisfaction_dose_ease_of_use'].mean()
                st.metric("DOSE Ease of Use", f"{avg_ease:.2f}/7")
```

### Deploy Streamlit

1. Create `requirements.txt` for Streamlit:
   ```
   streamlit
   pandas
   plotly
   scipy
   ```

2. Deploy to [Streamlit Community Cloud](https://streamlit.io/cloud):
   - Connect your GitHub repository
   - Select `streamlit_dashboard.py` as the main file
   - Deploy

---

## GitHub Repository Setup

### 1. Initialize Git

```bash
cd /root/psychological
git init
```

### 2. Create .gitignore

```
# Python
__pycache__/
*.py[cod]
.env
venv/
.venv/

# Node
node_modules/
.next/
out/

# Database
*.db
data/

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

### 3. Push to GitHub

```bash
git add .
git commit -m "Initial commit: Psychological Assessment Chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/psychological-assessment-chatbot.git
git push -u origin main
```

---

## Environment Variables Reference

### Backend (.env)

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./data/psychological.db

# For production with PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# App
APP_NAME=Psychological Assessment Chatbot
APP_VERSION=1.0.0
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Data Export API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/export/summary` | GET | Get data collection summary |
| `/api/export/participants/csv` | GET | Download all data as CSV |
| `/api/export/participants/json` | GET | Download all data as JSON |

### CSV Columns

- `participant_id`, `participant_code`, `age`, `gender`, `condition_order`
- `survey_completed`, `survey_extraversion`, `survey_agreeableness`, etc.
- `dose_completed`, `dose_extraversion`, `dose_extraversion_se`, etc.
- `satisfaction_completed`, `satisfaction_overall_rating`, `satisfaction_preferred_method`, etc.

---

## Quick Start Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Admin Page: http://localhost:3000/admin
