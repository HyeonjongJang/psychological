'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { submitSatisfactionSurvey, getSatisfactionStatus, type SatisfactionSubmit } from '@/lib/api';
import { useLanguage } from '@/context/LanguageContext';

export default function SatisfactionSurveyPage() {
  const params = useParams();
  const router = useRouter();
  const participantId = params.participantId as string;
  const { language, t } = useLanguage();

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [alreadyCompleted, setAlreadyCompleted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<SatisfactionSubmit>({
    overall_rating: 0,
    preferred_method: 'survey',
    dose_ease_of_use: 0,
    would_recommend: 0,
    open_feedback: '',
    language: language,
  });

  // Check if already completed
  useEffect(() => {
    async function checkStatus() {
      try {
        const status = await getSatisfactionStatus(participantId);
        if (status.has_completed) {
          setAlreadyCompleted(true);
        }
      } catch (err) {
        // If error, assume not completed
      } finally {
        setIsLoading(false);
      }
    }

    checkStatus();
  }, [participantId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (formData.overall_rating === 0) {
      setError(language === 'kr' ? '전반적인 경험을 평가해 주세요.' : 'Please rate your overall experience.');
      return;
    }
    if (formData.dose_ease_of_use === 0) {
      setError(language === 'kr' ? '챗봇 사용 편의성을 평가해 주세요.' : 'Please rate the chatbot ease of use.');
      return;
    }
    if (formData.would_recommend === 0) {
      setError(language === 'kr' ? '추천 의향을 선택해 주세요.' : 'Please indicate your recommendation level.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await submitSatisfactionSurvey(participantId, {
        ...formData,
        language,
      });
      setIsSubmitted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : (language === 'kr' ? '제출 중 오류가 발생했습니다.' : 'Failed to submit survey.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (alreadyCompleted) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-green-50 border border-green-200 rounded-2xl p-8 max-w-md text-center">
          <div className="text-4xl mb-4">✓</div>
          <h2 className="text-xl font-bold text-green-800 mb-2">{t.satisfaction.thankYouTitle}</h2>
          <p className="text-green-700 mb-6">{t.satisfaction.alreadyCompleted}</p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            {t.satisfaction.returnHome}
          </button>
        </div>
      </div>
    );
  }

  if (isSubmitted) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-green-50 border border-green-200 rounded-2xl p-8 max-w-md text-center">
          <div className="text-4xl mb-4">🎉</div>
          <h2 className="text-xl font-bold text-green-800 mb-2">{t.satisfaction.thankYouTitle}</h2>
          <p className="text-green-700 mb-6">{t.satisfaction.thankYouMessage}</p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            {t.satisfaction.returnHome}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{t.satisfaction.title}</h1>
          <p className="text-gray-600">{t.satisfaction.intro}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Overall Rating - Stars */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="font-semibold text-gray-900 mb-2">{t.satisfaction.overallRatingLabel}</h3>
            <p className="text-sm text-gray-600 mb-4">{t.satisfaction.overallRatingDescription}</p>
            <div className="flex gap-2 justify-center">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  onClick={() => setFormData({ ...formData, overall_rating: rating })}
                  className={`text-4xl transition-transform hover:scale-110 ${
                    formData.overall_rating >= rating ? 'text-yellow-400' : 'text-gray-300'
                  }`}
                >
                  ★
                </button>
              ))}
            </div>
            {formData.overall_rating > 0 && (
              <p className="text-center mt-2 text-sm text-gray-600">
                {t.satisfaction.starLabels[formData.overall_rating - 1]}
              </p>
            )}
          </div>

          {/* Preferred Method */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="font-semibold text-gray-900 mb-2">{t.satisfaction.preferredMethodLabel}</h3>
            <p className="text-sm text-gray-600 mb-4">{t.satisfaction.preferredMethodDescription}</p>
            <div className="flex flex-col md:flex-row gap-3">
              <button
                type="button"
                onClick={() => setFormData({ ...formData, preferred_method: 'survey' })}
                className={`flex-1 p-4 rounded-lg border-2 transition-colors ${
                  formData.preferred_method === 'survey'
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-2xl mb-2">📋</div>
                <div className="font-medium">{t.satisfaction.preferredSurvey}</div>
              </button>
              <button
                type="button"
                onClick={() => setFormData({ ...formData, preferred_method: 'dose' })}
                className={`flex-1 p-4 rounded-lg border-2 transition-colors ${
                  formData.preferred_method === 'dose'
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-2xl mb-2">🎯</div>
                <div className="font-medium">{t.satisfaction.preferredDose}</div>
              </button>
            </div>
          </div>

          {/* DOSE Ease of Use - Likert Scale */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="font-semibold text-gray-900 mb-2">{t.satisfaction.doseEaseLabel}</h3>
            <p className="text-sm text-gray-600 mb-4">{t.satisfaction.doseEaseDescription}</p>
            <div className="flex justify-between mb-2 text-xs text-gray-500">
              <span>{t.satisfaction.likertLabels[0]}</span>
              <span>{t.satisfaction.likertLabels[6]}</span>
            </div>
            <div className="flex gap-2 justify-center">
              {[1, 2, 3, 4, 5, 6, 7].map((value) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setFormData({ ...formData, dose_ease_of_use: value })}
                  className={`w-10 h-10 rounded-full font-semibold transition-all ${
                    formData.dose_ease_of_use === value
                      ? 'bg-primary-600 text-white scale-110'
                      : 'bg-gray-100 text-gray-700 hover:bg-primary-50'
                  }`}
                >
                  {value}
                </button>
              ))}
            </div>
            {formData.dose_ease_of_use > 0 && (
              <p className="text-center mt-2 text-sm text-gray-600">
                {t.satisfaction.likertLabels[formData.dose_ease_of_use - 1]}
              </p>
            )}
          </div>

          {/* Would Recommend - Likert Scale */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="font-semibold text-gray-900 mb-2">{t.satisfaction.wouldRecommendLabel}</h3>
            <p className="text-sm text-gray-600 mb-4">{t.satisfaction.wouldRecommendDescription}</p>
            <div className="flex justify-between mb-2 text-xs text-gray-500">
              <span>{t.satisfaction.likertLabels[0]}</span>
              <span>{t.satisfaction.likertLabels[6]}</span>
            </div>
            <div className="flex gap-2 justify-center">
              {[1, 2, 3, 4, 5, 6, 7].map((value) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setFormData({ ...formData, would_recommend: value })}
                  className={`w-10 h-10 rounded-full font-semibold transition-all ${
                    formData.would_recommend === value
                      ? 'bg-primary-600 text-white scale-110'
                      : 'bg-gray-100 text-gray-700 hover:bg-primary-50'
                  }`}
                >
                  {value}
                </button>
              ))}
            </div>
            {formData.would_recommend > 0 && (
              <p className="text-center mt-2 text-sm text-gray-600">
                {t.satisfaction.likertLabels[formData.would_recommend - 1]}
              </p>
            )}
          </div>

          {/* Open Feedback */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="font-semibold text-gray-900 mb-2">{t.satisfaction.openFeedbackLabel}</h3>
            <textarea
              value={formData.open_feedback}
              onChange={(e) => setFormData({ ...formData, open_feedback: e.target.value })}
              placeholder={t.satisfaction.openFeedbackPlaceholder}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
            />
          </div>

          {/* Error message */}
          {error && (
            <div className="bg-red-50 text-red-700 p-4 rounded-lg">
              {error}
            </div>
          )}

          {/* Submit button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-4 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? t.satisfaction.submitting : t.satisfaction.submitButton}
          </button>
        </form>
      </div>
    </div>
  );
}
