'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getParticipantResults, type ParticipantResultsResponse } from '@/lib/api';
import { useLanguage } from '@/context/LanguageContext';
import { getAllTraitDescriptions, type ScoreLevel } from '@/lib/personality-descriptions';

const SESSION_TYPE_COLORS: Record<string, string> = {
  survey: '#6B7280',
  dose: '#10B981',
};

const SCORE_LEVEL_COLORS: Record<ScoreLevel, string> = {
  low: 'bg-blue-100 text-blue-800',
  moderate: 'bg-gray-100 text-gray-800',
  high: 'bg-green-100 text-green-800',
};

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const participantId = params.participantId as string;
  const { language, t } = useLanguage();

  const [results, setResults] = useState<ParticipantResultsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Session type labels based on language
  const sessionTypeLabels: Record<string, string> = {
    survey: t.hub.conditionNames.survey,
    dose: t.hub.conditionNames.dose,
  };

  useEffect(() => {
    async function fetchResults() {
      try {
        const data = await getParticipantResults(participantId);
        setResults(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load results');
      } finally {
        setLoading(false);
      }
    }

    fetchResults();
  }, [participantId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-red-50 text-red-700 p-6 rounded-xl max-w-md">
          <h2 className="font-bold mb-2">{t.common.error}</h2>
          <p>{error || (language === 'kr' ? '결과를 불러오는데 실패했습니다' : 'Failed to load results')}</p>
          <button
            onClick={() => router.push(`/assessment/${participantId}`)}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            {t.common.returnToHub}
          </button>
        </div>
      </div>
    );
  }

  const traits = Object.keys(t.traits) as Array<keyof typeof t.traits>;

  // Get primary scores (prefer survey as it's the complete assessment)
  const surveySession = results.sessions.find(s => s.session_type === 'survey');
  const primaryScores = surveySession?.scores || results.sessions[0]?.scores || {};
  const personalityDescriptions = getAllTraitDescriptions(primaryScores, language);

  // Score level labels
  const scoreLevelLabels: Record<ScoreLevel, string> = {
    low: t.results.scoreLevelLow,
    moderate: t.results.scoreLevelModerate,
    high: t.results.scoreLevelHigh,
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{t.results.title}</h1>
              <p className="text-gray-600">{t.results.participantLabel}: {results.participant_code}</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-primary-600">
                {results.sessions_completed}/2
              </div>
              <div className="text-sm text-gray-500">{t.results.assessmentsComplete}</div>
            </div>
          </div>
        </div>

        {/* Personality Profile */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-2">{t.results.personalityProfileTitle}</h2>
          <p className="text-gray-600 mb-6">{t.results.personalityProfileIntro}</p>

          <div className="space-y-6">
            {personalityDescriptions.map((desc) => (
              <div key={desc.trait} className="border rounded-xl p-5 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-gray-900">{desc.name}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${SCORE_LEVEL_COLORS[desc.level]}`}>
                      {scoreLevelLabels[desc.level]}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-bold text-primary-600">{desc.score.toFixed(1)}</span>
                    <span className="text-sm text-gray-400">/7</span>
                  </div>
                </div>
                <div className="mb-3 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-500 rounded-full transition-all duration-500"
                    style={{ width: `${(desc.score / 7) * 100}%` }}
                  />
                </div>
                <p className="text-gray-700 leading-relaxed">{desc.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Trait Scores Comparison */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">{t.results.traitComparison}</h2>

          {/* Legend */}
          <div className="flex flex-wrap gap-4 mb-6">
            {results.sessions.map((session) => (
              <div key={session.session_type} className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: SESSION_TYPE_COLORS[session.session_type] }}
                />
                <span className="text-sm text-gray-600">
                  {sessionTypeLabels[session.session_type]}
                </span>
              </div>
            ))}
          </div>

          {/* Bar Chart */}
          <div className="space-y-6">
            {traits.map((trait) => (
              <div key={trait}>
                <div className="flex justify-between mb-2">
                  <span className="font-medium text-gray-700">{t.traits[trait]}</span>
                </div>
                <div className="space-y-2">
                  {results.sessions.map((session) => {
                    const score = session.scores[trait] || 0;
                    const percentage = (score / 7) * 100;
                    return (
                      <div key={session.session_type} className="flex items-center gap-3">
                        <div className="w-24 text-xs text-gray-500 text-right">
                          {sessionTypeLabels[session.session_type].split(' ')[0]}
                        </div>
                        <div className="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${percentage}%`,
                              backgroundColor: SESSION_TYPE_COLORS[session.session_type],
                            }}
                          />
                        </div>
                        <div className="w-12 text-sm font-medium text-gray-700">
                          {score.toFixed(2)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Efficiency Metrics */}
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          {results.sessions.map((session) => (
            <div key={session.session_type} className="bg-white rounded-xl shadow-md p-4">
              <div className="flex items-center gap-2 mb-3">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: SESSION_TYPE_COLORS[session.session_type] }}
                />
                <h3 className="font-semibold text-gray-900">
                  {sessionTypeLabels[session.session_type]}
                </h3>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">{t.results.items}:</span>
                  <span className="font-medium">{session.metrics.total_items}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">{t.results.duration}:</span>
                  <span className="font-medium">
                    {Math.round(session.metrics.duration_seconds / 60)}m {session.metrics.duration_seconds % 60}s
                  </span>
                </div>
                {session.metrics.item_reduction_rate !== null && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">{t.results.reduction}:</span>
                    <span className="font-medium text-green-600">
                      {(session.metrics.item_reduction_rate * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Accuracy Comparison with Survey */}
        {results.comparisons_with_survey && (
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {t.results.accuracyTitle}
            </h2>
            <div className="grid md:grid-cols-1 gap-6 max-w-md">
              {Object.entries(results.comparisons_with_survey).map(([type, comparison]) => (
                <div key={type} className="border rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: SESSION_TYPE_COLORS[type] }}
                    />
                    <h3 className="font-semibold">{sessionTypeLabels[type]}</h3>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <div className="text-sm text-gray-500 mb-1">{t.results.correlation}</div>
                      <div className={`text-2xl font-bold ${
                        comparison.pearson_r >= 0.9 ? 'text-green-600' :
                        comparison.pearson_r >= 0.7 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {comparison.pearson_r.toFixed(3)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500 mb-1">{t.results.mae}</div>
                      <div className="text-lg font-semibold text-gray-700">
                        {comparison.mean_absolute_error.toFixed(3)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500 mb-2">{t.results.traitDifferences}</div>
                      <div className="space-y-1">
                        {Object.entries(comparison.trait_differences).map(([trait, diff]) => (
                          <div key={trait} className="flex justify-between text-xs">
                            <span className="text-gray-500">{t.traits[trait as keyof typeof t.traits]}:</span>
                            <span className={diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : 'text-gray-600'}>
                              {diff > 0 ? '+' : ''}{diff.toFixed(2)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Research Insights */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <h2 className="text-lg font-bold text-blue-800 mb-3">{t.results.insightsTitle}</h2>
          <div className="text-blue-700 space-y-2">
            <p>
              {t.results.insightsDescription}
            </p>
            {results.comparisons_with_survey && (
              <>
                {Object.entries(results.comparisons_with_survey).find(([_, c]) => c.pearson_r >= 0.9) && (
                  <p className="font-medium">
                    {t.results.strongCorrelation}
                  </p>
                )}
                {results.sessions.find(s => s.session_type === 'dose' && s.metrics.item_reduction_rate && s.metrics.item_reduction_rate >= 0.5) && (
                  <p className="font-medium">
                    {t.results.doseEfficiency}
                  </p>
                )}
              </>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="mt-6 flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => router.push(`/assessment/${participantId}`)}
            className="px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors"
          >
            {t.results.backButton}
          </button>
          <button
            onClick={() => router.push(`/satisfaction/${participantId}`)}
            className="px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
          >
            {t.results.continueToFeedback}
          </button>
        </div>
      </div>
    </div>
  );
}
