'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { startSurvey, getSurveyItems, submitSurvey } from '@/lib/api';
import { useLanguage } from '@/context/LanguageContext';
import { getItemText } from '@/lib/i18n';

interface SurveyItem {
  number: number;
  text: string;
  trait: string;
}

export default function SurveyPage() {
  const params = useParams();
  const router = useRouter();
  const participantId = params.participantId as string;
  const { language, t } = useLanguage();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [items, setItems] = useState<SurveyItem[]>([]);
  const [responses, setResponses] = useState<Record<number, number>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function initSurvey() {
      try {
        const session = await startSurvey(participantId);
        setSessionId(session.id);

        const itemsData = await getSurveyItems(session.id);
        setItems(itemsData.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to start survey');
      } finally {
        setIsLoading(false);
      }
    }

    initSurvey();
  }, [participantId]);

  const handleResponseChange = (itemNumber: number, value: number) => {
    setResponses((prev) => ({ ...prev, [itemNumber]: value }));
  };

  const handleSubmit = async () => {
    if (!sessionId) return;

    const unanswered = items.filter((item) => !responses[item.number]);
    if (unanswered.length > 0) {
      setError(language === 'kr'
        ? `아직 답변하지 않은 문항이 ${unanswered.length}개 있습니다. 모든 문항에 답변해 주시면 감사하겠습니다.`
        : `There are ${unanswered.length} unanswered questions remaining. Please complete all questions before submitting.`
      );
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const formattedResponses = Object.entries(responses).map(([num, value]) => ({
        item_number: parseInt(num),
        value,
      }));

      await submitSurvey(sessionId, formattedResponses);
      router.push(`/assessment/${participantId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : (language === 'kr' ? '설문 제출 중 오류가 발생했습니다. 다시 시도해 주세요.' : 'Failed to submit survey. Please try again.'));
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

  if (error && !sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-red-50 text-red-700 p-6 rounded-xl max-w-md">
          <h2 className="font-bold mb-2">{t.common.error}</h2>
          <p>{error}</p>
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

  const answeredCount = Object.keys(responses).length;
  const progress = (answeredCount / items.length) * 100;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-bold text-lg">{t.survey.title}</h1>
              <p className="text-sm text-gray-500">
                {language === 'kr'
                  ? `${items.length}개 문항 중 ${answeredCount}개 응답 완료`
                  : `${answeredCount} of ${items.length} questions answered`
                }
              </p>
            </div>
            <button
              onClick={handleSubmit}
              disabled={isSubmitting || answeredCount < items.length}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                answeredCount === items.length
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              {isSubmitting
                ? (language === 'kr' ? '제출 중...' : 'Submitting...')
                : t.common.submit
              }
            </button>
          </div>
          <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 mb-6">
          <p className="text-blue-800">
            {t.survey.instructions}
          </p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Survey items */}
        <div className="space-y-6">
          {items.map((item) => {
            const itemText = getItemText(item.number, language);
            return (
              <div
                key={item.number}
                className={`bg-white rounded-xl shadow-sm p-6 border-2 transition-colors ${
                  responses[item.number]
                    ? 'border-green-200'
                    : 'border-transparent'
                }`}
              >
                <div className="flex gap-4">
                  <span className="text-lg font-semibold text-gray-400">
                    {item.number}.
                  </span>
                  <div className="flex-1">
                    <p className="text-lg text-gray-900 mb-4">{itemText}</p>
                    <div className="flex flex-wrap gap-2">
                      {t.likert.labels.map((label, index) => {
                        const value = index + 1;
                        const isSelected = responses[item.number] === value;
                        return (
                          <button
                            key={value}
                            onClick={() => handleResponseChange(item.number, value)}
                            className={`px-3 py-2 text-sm rounded-lg border-2 transition-all ${
                              isSelected
                                ? 'border-primary-500 bg-primary-50 text-primary-700 font-medium'
                                : 'border-gray-200 hover:border-gray-300 text-gray-600'
                            }`}
                          >
                            {value}. {label}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom submit button */}
        <div className="mt-8 text-center">
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || answeredCount < items.length}
            className={`px-8 py-3 rounded-lg font-semibold transition-colors ${
              answeredCount === items.length
                ? 'bg-primary-600 text-white hover:bg-primary-700'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            {isSubmitting
              ? (language === 'kr' ? '제출 중...' : 'Submitting...')
              : answeredCount === items.length
                ? t.survey.submitButton
                : (language === 'kr'
                    ? `나머지 ${items.length - answeredCount}개 문항에 답변해 주세요`
                    : `Answer all ${items.length - answeredCount} remaining questions`
                  )
            }
          </button>
        </div>
      </div>
    </div>
  );
}
