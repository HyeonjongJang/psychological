"""Data export API endpoints for admin/research use."""
import csv
import io
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..core.database import get_db
from ..models import (
    Participant, AssessmentSession, AssessmentResult,
    SatisfactionSurvey, SessionStatus
)

router = APIRouter()


@router.get("/participants/csv")
async def export_all_participants_csv(
    db: AsyncSession = Depends(get_db)
):
    """
    Export all participants' data as CSV.

    Includes:
    - Participant demographics
    - Condition order
    - Survey results (scores for each trait)
    - DOSE results (scores for each trait)
    - Satisfaction survey responses
    """
    # Query all participants with related data
    result = await db.execute(
        select(Participant)
        .options(
            selectinload(Participant.sessions).selectinload(AssessmentSession.result)
        )
        .order_by(Participant.created_at)
    )
    participants = result.scalars().all()

    # Query satisfaction surveys separately
    satisfaction_result = await db.execute(select(SatisfactionSurvey))
    satisfaction_surveys = {s.participant_id: s for s in satisfaction_result.scalars().all()}

    # Create CSV in memory
    output = io.StringIO()

    # Define CSV headers
    headers = [
        # Participant info
        'participant_id',
        'participant_code',
        'age',
        'gender',
        'condition_order',
        'created_at',

        # Survey results
        'survey_completed',
        'survey_extraversion',
        'survey_agreeableness',
        'survey_conscientiousness',
        'survey_neuroticism',
        'survey_openness',
        'survey_honesty_humility',
        'survey_duration_seconds',
        'survey_items',

        # DOSE results
        'dose_completed',
        'dose_extraversion',
        'dose_agreeableness',
        'dose_conscientiousness',
        'dose_neuroticism',
        'dose_openness',
        'dose_honesty_humility',
        'dose_extraversion_se',
        'dose_agreeableness_se',
        'dose_conscientiousness_se',
        'dose_neuroticism_se',
        'dose_openness_se',
        'dose_honesty_humility_se',
        'dose_duration_seconds',
        'dose_items',
        'dose_item_reduction_rate',

        # Satisfaction survey
        'satisfaction_completed',
        'satisfaction_overall_rating',
        'satisfaction_preferred_method',
        'satisfaction_dose_ease_of_use',
        'satisfaction_would_recommend',
        'satisfaction_open_feedback',
        'satisfaction_language',
    ]

    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()

    for participant in participants:
        row = {
            'participant_id': participant.id,
            'participant_code': participant.participant_code,
            'age': participant.age,
            'gender': participant.gender,
            'condition_order': json.dumps(participant.condition_order),
            'created_at': participant.created_at.isoformat() if participant.created_at else '',
        }

        # Find survey and dose sessions
        survey_session = None
        dose_session = None

        for session in participant.sessions:
            if session.session_type.value == 'survey' and session.status == SessionStatus.COMPLETED:
                survey_session = session
            elif session.session_type.value == 'dose' and session.status == SessionStatus.COMPLETED:
                dose_session = session

        # Survey results
        if survey_session and survey_session.result:
            result = survey_session.result
            row.update({
                'survey_completed': True,
                'survey_extraversion': result.extraversion_score,
                'survey_agreeableness': result.agreeableness_score,
                'survey_conscientiousness': result.conscientiousness_score,
                'survey_neuroticism': result.neuroticism_score,
                'survey_openness': result.openness_score,
                'survey_honesty_humility': result.honesty_humility_score,
                'survey_duration_seconds': result.total_duration_seconds,
                'survey_items': result.total_items_administered,
            })
        else:
            row.update({
                'survey_completed': False,
                'survey_extraversion': '',
                'survey_agreeableness': '',
                'survey_conscientiousness': '',
                'survey_neuroticism': '',
                'survey_openness': '',
                'survey_honesty_humility': '',
                'survey_duration_seconds': '',
                'survey_items': '',
            })

        # DOSE results
        if dose_session and dose_session.result:
            result = dose_session.result
            row.update({
                'dose_completed': True,
                'dose_extraversion': result.extraversion_score,
                'dose_agreeableness': result.agreeableness_score,
                'dose_conscientiousness': result.conscientiousness_score,
                'dose_neuroticism': result.neuroticism_score,
                'dose_openness': result.openness_score,
                'dose_honesty_humility': result.honesty_humility_score,
                'dose_extraversion_se': result.extraversion_se,
                'dose_agreeableness_se': result.agreeableness_se,
                'dose_conscientiousness_se': result.conscientiousness_se,
                'dose_neuroticism_se': result.neuroticism_se,
                'dose_openness_se': result.openness_se,
                'dose_honesty_humility_se': result.honesty_humility_se,
                'dose_duration_seconds': result.total_duration_seconds,
                'dose_items': result.total_items_administered,
                'dose_item_reduction_rate': result.item_reduction_rate,
            })
        else:
            row.update({
                'dose_completed': False,
                'dose_extraversion': '',
                'dose_agreeableness': '',
                'dose_conscientiousness': '',
                'dose_neuroticism': '',
                'dose_openness': '',
                'dose_honesty_humility': '',
                'dose_extraversion_se': '',
                'dose_agreeableness_se': '',
                'dose_conscientiousness_se': '',
                'dose_neuroticism_se': '',
                'dose_openness_se': '',
                'dose_honesty_humility_se': '',
                'dose_duration_seconds': '',
                'dose_items': '',
                'dose_item_reduction_rate': '',
            })

        # Satisfaction survey
        satisfaction = satisfaction_surveys.get(participant.id)
        if satisfaction:
            row.update({
                'satisfaction_completed': True,
                'satisfaction_overall_rating': satisfaction.overall_rating,
                'satisfaction_preferred_method': satisfaction.preferred_method,
                'satisfaction_dose_ease_of_use': satisfaction.dose_ease_of_use,
                'satisfaction_would_recommend': satisfaction.would_recommend,
                'satisfaction_open_feedback': satisfaction.open_feedback or '',
                'satisfaction_language': satisfaction.language,
            })
        else:
            row.update({
                'satisfaction_completed': False,
                'satisfaction_overall_rating': '',
                'satisfaction_preferred_method': '',
                'satisfaction_dose_ease_of_use': '',
                'satisfaction_would_recommend': '',
                'satisfaction_open_feedback': '',
                'satisfaction_language': '',
            })

        writer.writerow(row)

    # Prepare response
    output.seek(0)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"psychological_assessment_data_{timestamp}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/participants/json")
async def export_all_participants_json(
    db: AsyncSession = Depends(get_db)
):
    """
    Export all participants' data as JSON.

    Returns a comprehensive JSON object with all participant data.
    """
    # Query all participants with related data
    result = await db.execute(
        select(Participant)
        .options(
            selectinload(Participant.sessions).selectinload(AssessmentSession.result)
        )
        .order_by(Participant.created_at)
    )
    participants = result.scalars().all()

    # Query satisfaction surveys separately
    satisfaction_result = await db.execute(select(SatisfactionSurvey))
    satisfaction_surveys = {s.participant_id: s for s in satisfaction_result.scalars().all()}

    export_data = {
        "export_timestamp": datetime.utcnow().isoformat(),
        "total_participants": len(participants),
        "participants": []
    }

    for participant in participants:
        participant_data = {
            "id": participant.id,
            "participant_code": participant.participant_code,
            "demographics": {
                "age": participant.age,
                "gender": participant.gender,
            },
            "condition_order": participant.condition_order,
            "created_at": participant.created_at.isoformat() if participant.created_at else None,
            "sessions": [],
            "satisfaction_survey": None,
        }

        for session in participant.sessions:
            session_data = {
                "session_id": session.id,
                "session_type": session.session_type.value,
                "sequence_number": session.sequence_number,
                "status": session.status.value,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "result": None,
            }

            if session.result:
                session_data["result"] = session.result.to_dict()

            participant_data["sessions"].append(session_data)

        satisfaction = satisfaction_surveys.get(participant.id)
        if satisfaction:
            participant_data["satisfaction_survey"] = satisfaction.to_dict()

        export_data["participants"].append(participant_data)

    return export_data


@router.get("/summary")
async def get_data_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Get a summary of all collected data.

    Useful for admin dashboard to see data collection progress.
    """
    # Count participants
    result = await db.execute(select(Participant))
    participants = result.scalars().all()
    total_participants = len(participants)

    # Count completed sessions by type
    result = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.status == SessionStatus.COMPLETED)
    )
    completed_sessions = result.scalars().all()

    survey_completed = sum(1 for s in completed_sessions if s.session_type.value == 'survey')
    dose_completed = sum(1 for s in completed_sessions if s.session_type.value == 'dose')

    # Count satisfaction surveys
    result = await db.execute(select(SatisfactionSurvey))
    satisfaction_count = len(result.scalars().all())

    # Count fully completed (both assessments + satisfaction)
    fully_completed = 0
    for p in participants:
        sessions = [s for s in completed_sessions if s.participant_id == p.id]
        has_survey = any(s.session_type.value == 'survey' for s in sessions)
        has_dose = any(s.session_type.value == 'dose' for s in sessions)
        has_satisfaction = any(s.participant_id == p.id for s in completed_sessions)
        if has_survey and has_dose:
            fully_completed += 1

    return {
        "total_participants": total_participants,
        "survey_completed": survey_completed,
        "dose_completed": dose_completed,
        "both_assessments_completed": fully_completed,
        "satisfaction_surveys_completed": satisfaction_count,
        "export_endpoints": {
            "csv": "/api/export/participants/csv",
            "json": "/api/export/participants/json",
        }
    }
