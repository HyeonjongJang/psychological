"""
Streamlit Dashboard for Psychological Assessment Data Analysis

Deploy to Streamlit Community Cloud:
1. Push this file to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your GitHub repo
4. Select this file as the main script
5. Deploy!

Local run:
    pip install streamlit pandas plotly scipy
    streamlit run streamlit_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import json

st.set_page_config(
    page_title="Psychological Assessment Analysis",
    page_icon="brain",
    layout="wide"
)

st.title("Psychological Assessment Data Analysis")
st.markdown("Compare Survey vs DOSE adaptive chatbot personality assessments")

# File uploader
uploaded_file = st.file_uploader("Upload exported CSV file from /api/export/participants/csv", type="csv")

if uploaded_file is None:
    st.info("Please upload a CSV file to begin analysis. You can download the CSV from the admin page at /admin or directly from /api/export/participants/csv")

    # Show example of expected format
    st.subheader("Expected CSV Format")
    example_df = pd.DataFrame({
        'participant_id': ['abc123'],
        'participant_code': ['P001'],
        'age': [25],
        'gender': ['female'],
        'survey_completed': [True],
        'survey_extraversion': [4.5],
        'dose_completed': [True],
        'dose_extraversion': [4.3],
        'satisfaction_completed': [True],
        'satisfaction_overall_rating': [4],
    })
    st.dataframe(example_df)
    st.stop()

# Load data
df = pd.read_csv(uploaded_file)

# Data overview
st.header("Data Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Participants", len(df))

with col2:
    survey_completed = df['survey_completed'].sum() if 'survey_completed' in df.columns else 0
    st.metric("Survey Completed", survey_completed)

with col3:
    dose_completed = df['dose_completed'].sum() if 'dose_completed' in df.columns else 0
    st.metric("DOSE Completed", dose_completed)

with col4:
    both_completed = len(df[(df['survey_completed'] == True) & (df['dose_completed'] == True)]) if 'survey_completed' in df.columns else 0
    st.metric("Both Completed", both_completed)

# Filter to completed participants for analysis
completed = df[(df['survey_completed'] == True) & (df['dose_completed'] == True)]

if len(completed) == 0:
    st.warning("No participants have completed both assessments yet. Analysis requires completed data.")
    st.stop()

st.divider()

# Define traits
TRAITS = ['extraversion', 'agreeableness', 'conscientiousness', 'neuroticism', 'openness', 'honesty_humility']
TRAIT_LABELS = {
    'extraversion': 'Extraversion',
    'agreeableness': 'Agreeableness',
    'conscientiousness': 'Conscientiousness',
    'neuroticism': 'Neuroticism',
    'openness': 'Openness',
    'honesty_humility': 'Honesty-Humility'
}

# Tabs for different analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Trait Comparison", "Correlation Analysis", "Efficiency Metrics", "Satisfaction Survey", "Raw Data"])

with tab1:
    st.header("Survey vs DOSE Trait Scores")

    # Create scatter plots for each trait
    for i in range(0, len(TRAITS), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(TRAITS):
                trait = TRAITS[i + j]
                survey_col = f'survey_{trait}'
                dose_col = f'dose_{trait}'

                if survey_col in completed.columns and dose_col in completed.columns:
                    with col:
                        fig = px.scatter(
                            completed,
                            x=survey_col,
                            y=dose_col,
                            title=TRAIT_LABELS[trait],
                            labels={survey_col: 'Survey Score', dose_col: 'DOSE Score'},
                            hover_data=['participant_code'] if 'participant_code' in completed.columns else None
                        )
                        # Add diagonal line for perfect agreement
                        fig.add_trace(go.Scatter(
                            x=[1, 7], y=[1, 7],
                            mode='lines',
                            name='Perfect Agreement',
                            line=dict(dash='dash', color='gray')
                        ))
                        fig.update_layout(
                            xaxis_range=[1, 7],
                            yaxis_range=[1, 7],
                            xaxis_title='Survey Score',
                            yaxis_title='DOSE Score'
                        )
                        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Correlation Analysis")

    # Calculate per-trait correlations
    correlations = []
    for trait in TRAITS:
        survey_col = f'survey_{trait}'
        dose_col = f'dose_{trait}'

        if survey_col in completed.columns and dose_col in completed.columns:
            valid = completed[[survey_col, dose_col]].dropna()
            if len(valid) > 2:
                r, p = stats.pearsonr(valid[survey_col], valid[dose_col])
                mae = abs(valid[survey_col] - valid[dose_col]).mean()
                correlations.append({
                    'Trait': TRAIT_LABELS[trait],
                    'Pearson r': round(r, 3),
                    'p-value': round(p, 4),
                    'MAE': round(mae, 3),
                    'N': len(valid)
                })

    if correlations:
        corr_df = pd.DataFrame(correlations)
        st.dataframe(corr_df, use_container_width=True, hide_index=True)

        # Overall correlation
        st.subheader("Overall Correlation (All Traits Combined)")

        all_survey = []
        all_dose = []
        for trait in TRAITS:
            survey_col = f'survey_{trait}'
            dose_col = f'dose_{trait}'
            if survey_col in completed.columns and dose_col in completed.columns:
                valid = completed[[survey_col, dose_col]].dropna()
                all_survey.extend(valid[survey_col].tolist())
                all_dose.extend(valid[dose_col].tolist())

        if len(all_survey) > 2:
            overall_r, overall_p = stats.pearsonr(all_survey, all_dose)
            overall_mae = sum(abs(s - d) for s, d in zip(all_survey, all_dose)) / len(all_survey)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Pearson r", f"{overall_r:.3f}")
            with col2:
                st.metric("p-value", f"<0.001" if overall_p < 0.001 else f"{overall_p:.4f}")
            with col3:
                st.metric("Overall MAE", f"{overall_mae:.3f}")

            # Interpretation
            if overall_r >= 0.9:
                st.success("Excellent convergent validity (r >= 0.9). DOSE scores closely match traditional survey scores.")
            elif overall_r >= 0.7:
                st.info("Good convergent validity (r >= 0.7). DOSE shows strong agreement with traditional survey.")
            else:
                st.warning("Moderate convergent validity (r < 0.7). Further investigation recommended.")

with tab3:
    st.header("Efficiency Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Items Administered")

        survey_items = completed['survey_items'].mean() if 'survey_items' in completed.columns else 24
        dose_items = completed['dose_items'].mean() if 'dose_items' in completed.columns else 0

        fig = go.Figure(data=[
            go.Bar(name='Survey', x=['Items'], y=[survey_items], marker_color='#6B7280'),
            go.Bar(name='DOSE', x=['Items'], y=[dose_items], marker_color='#10B981')
        ])
        fig.update_layout(barmode='group', title='Average Items per Assessment')
        st.plotly_chart(fig, use_container_width=True)

        if survey_items > 0 and dose_items > 0:
            reduction = (1 - dose_items / survey_items) * 100
            st.metric("Item Reduction Rate", f"{reduction:.1f}%",
                     delta=f"{survey_items - dose_items:.1f} fewer items")

    with col2:
        st.subheader("Duration")

        survey_time = completed['survey_duration_seconds'].mean() / 60 if 'survey_duration_seconds' in completed.columns else 0
        dose_time = completed['dose_duration_seconds'].mean() / 60 if 'dose_duration_seconds' in completed.columns else 0

        fig = go.Figure(data=[
            go.Bar(name='Survey', x=['Duration (min)'], y=[survey_time], marker_color='#6B7280'),
            go.Bar(name='DOSE', x=['Duration (min)'], y=[dose_time], marker_color='#10B981')
        ])
        fig.update_layout(barmode='group', title='Average Duration per Assessment')
        st.plotly_chart(fig, use_container_width=True)

        if survey_time > 0 and dose_time > 0:
            time_reduction = (1 - dose_time / survey_time) * 100
            st.metric("Time Reduction", f"{time_reduction:.1f}%",
                     delta=f"{survey_time - dose_time:.1f} min faster")

    # Standard Errors (DOSE precision)
    st.subheader("DOSE Precision (Standard Errors)")
    se_cols = [f'dose_{t}_se' for t in TRAITS]
    available_se = [c for c in se_cols if c in completed.columns]

    if available_se:
        se_data = []
        for col in available_se:
            trait = col.replace('dose_', '').replace('_se', '')
            avg_se = completed[col].mean()
            se_data.append({'Trait': TRAIT_LABELS.get(trait, trait), 'Avg SE': avg_se})

        se_df = pd.DataFrame(se_data)
        fig = px.bar(se_df, x='Trait', y='Avg SE', title='Average Standard Error by Trait')
        fig.add_hline(y=0.3, line_dash="dash", annotation_text="Target SE = 0.3")
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Satisfaction Survey Results")

    sat_completed = df[df['satisfaction_completed'] == True] if 'satisfaction_completed' in df.columns else pd.DataFrame()

    if len(sat_completed) == 0:
        st.info("No satisfaction survey responses yet.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            if 'satisfaction_overall_rating' in sat_completed.columns:
                avg_rating = sat_completed['satisfaction_overall_rating'].mean()
                st.metric("Overall Rating", f"{avg_rating:.2f}/5")

                # Star distribution
                fig = px.histogram(sat_completed, x='satisfaction_overall_rating',
                                  title='Rating Distribution',
                                  labels={'satisfaction_overall_rating': 'Rating'})
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'satisfaction_preferred_method' in sat_completed.columns:
                preferred = sat_completed['satisfaction_preferred_method'].value_counts()
                fig = px.pie(values=preferred.values, names=preferred.index,
                            title='Preferred Method')
                st.plotly_chart(fig, use_container_width=True)

        with col3:
            if 'satisfaction_dose_ease_of_use' in sat_completed.columns:
                avg_ease = sat_completed['satisfaction_dose_ease_of_use'].mean()
                st.metric("DOSE Ease of Use", f"{avg_ease:.2f}/7")

            if 'satisfaction_would_recommend' in sat_completed.columns:
                avg_recommend = sat_completed['satisfaction_would_recommend'].mean()
                st.metric("Would Recommend", f"{avg_recommend:.2f}/7")

        # Open feedback
        if 'satisfaction_open_feedback' in sat_completed.columns:
            st.subheader("Open Feedback")
            feedback = sat_completed[sat_completed['satisfaction_open_feedback'].notna()]['satisfaction_open_feedback']
            for i, fb in enumerate(feedback.head(10)):
                if fb and str(fb).strip():
                    st.text_area(f"Response {i+1}", fb, height=100, disabled=True)

with tab5:
    st.header("Raw Data")

    # Column selector
    all_cols = df.columns.tolist()
    selected_cols = st.multiselect("Select columns to display", all_cols, default=all_cols[:10])

    if selected_cols:
        st.dataframe(df[selected_cols], use_container_width=True)

    # Download filtered data
    csv = df.to_csv(index=False)
    st.download_button(
        "Download Full CSV",
        csv,
        "psychological_assessment_data.csv",
        "text/csv"
    )

# Footer
st.divider()
st.markdown("""
**Notes:**
- Survey uses traditional 24-item Mini-IPIP6 questionnaire
- DOSE uses adaptive Item Response Theory (IRT) with dynamic item selection
- Higher Pearson r indicates better convergent validity between methods
- Lower MAE (Mean Absolute Error) indicates closer score agreement
- Item reduction rate shows efficiency gains of adaptive testing
""")
