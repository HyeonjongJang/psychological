'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getParticipantProgress, type ParticipantProgress } from '@/lib/api';
import { useLanguage } from '@/context/LanguageContext';

const CONDITION_ICONS = {
  survey: '📋',
  dose: '🎯',
};

export default function AssessmentHub() {
  const params = useParams();
  const router = useRouter();
  const participantId = params.participantId as string;
  const { t } = useLanguage();

  const [progress, setProgress] = useState<ParticipantProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProgress() {
      try {
        const data = await getParticipantProgress(participantId);
        setProgress(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load progress');
      } finally {
        setLoading(false);
      }
    }

    fetchProgress();
  }, [participantId]);

  const handleStartCondition = (condition: string) => {
    router.push(`/assessment/${participantId}/${condition}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !progress) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-50 text-red-700 p-4 rounded-lg">
          {error || 'Failed to load progress'}
        </div>
      </div>
    );
  }

  const allComplete = progress.sessions_completed === 2;

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{t.hub.title}</h1>
              <p className="text-gray-600">{t.hub.participantLabel}: {progress.participant_code}</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-primary-600">
                {progress.sessions_completed}/2
              </div>
              <div className="text-sm text-gray-500">{t.hub.completedLabel}</div>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-4 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 transition-all duration-500"
              style={{ width: `${(progress.sessions_completed / 2) * 100}%` }}
            />
          </div>
        </div>

        {/* Condition cards */}
        <div className="space-y-4">
          {progress.condition_order.map((condition, index) => {
            const conditionKey = condition as keyof typeof t.hub.conditionNames;
            const name = t.hub.conditionNames[conditionKey];
            const description = t.hub.conditionDescriptions[conditionKey];
            const icon = CONDITION_ICONS[condition as keyof typeof CONDITION_ICONS];
            const isCompleted = progress.completed_conditions.includes(condition);
            const isNext = condition === progress.next_condition;

            return (
              <div
                key={condition}
                className={`
                  bg-white rounded-xl shadow-md p-6 border-2 transition-all
                  ${isCompleted ? 'border-green-200 bg-green-50' : ''}
                  ${isNext ? 'border-primary-300 shadow-lg' : 'border-transparent'}
                `}
              >
                <div className="flex items-center gap-4">
                  <div className="text-4xl">{icon}</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {index + 1}. {name}
                      </h3>
                      {isCompleted && (
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">
                          {t.common.completed}
                        </span>
                      )}
                      {isNext && (
                        <span className="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded-full">
                          {t.common.next}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 text-sm mt-1">{description}</p>
                  </div>
                  <button
                    onClick={() => handleStartCondition(condition)}
                    disabled={isCompleted}
                    className={`
                      px-6 py-2 rounded-lg font-medium transition-colors
                      ${isCompleted
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : isNext
                          ? 'bg-primary-600 text-white hover:bg-primary-700'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }
                    `}
                  >
                    {isCompleted ? t.common.done : t.common.start}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Completion message */}
        {allComplete && (
          <div className="mt-6 bg-green-50 border border-green-200 rounded-xl p-6 text-center">
            <div className="text-4xl mb-2">🎉</div>
            <h2 className="text-xl font-bold text-green-800">{t.hub.allComplete.title}</h2>
            <p className="text-green-600 mt-1">
              {t.hub.allComplete.message}
            </p>
            <button
              onClick={() => router.push(`/results/${participantId}`)}
              className="mt-4 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              {t.hub.allComplete.viewResults}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
