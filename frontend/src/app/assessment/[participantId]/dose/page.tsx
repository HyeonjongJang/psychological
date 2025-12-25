'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ChatContainer, { type Message } from '@/components/chat/ChatContainer';
import LikertScale from '@/components/ui/LikertScale';
import { startDOSEChatbot, respondDOSEChatbot, type DOSERespondResponse } from '@/lib/api';
import { useLanguage } from '@/context/LanguageContext';
import { getItemText } from '@/lib/i18n';

interface CurrentItem {
  number: number;
  text: string;
  trait: string;
}

interface TraitProgress {
  theta: number;
  se: number;
  items_administered: number;
  completed: boolean;
}

export default function DOSEChatbotPage() {
  const params = useParams();
  const router = useRouter();
  const participantId = params.participantId as string;
  const { language, t } = useLanguage();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentItem, setCurrentItem] = useState<CurrentItem | null>(null);
  const [traitProgress, setTraitProgress] = useState<Record<string, TraitProgress>>({});
  const [totalItems, setTotalItems] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedValue, setSelectedValue] = useState<number | null>(null);

  // Initialize session
  useEffect(() => {
    async function initSession() {
      setIsLoading(true);
      try {
        const response = await startDOSEChatbot(participantId);
        setSessionId(response.session_id);
        setCurrentItem(response.current_item);
        setTraitProgress(response.current_estimates);

        const itemText = getItemText(response.current_item.number, language);
        const firstQuestionIntro = language === 'kr'
          ? '첫 번째 문항입니다:'
          : "Here's your first statement:";

        // Add welcome message
        setMessages([
          {
            id: '1',
            role: 'assistant',
            content: t.dose.welcomeMessage,
          },
          {
            id: '2',
            role: 'assistant',
            content: `${firstQuestionIntro}\n\n"${itemText}"\n\n${t.dose.itemPrompt}`,
            itemNumber: response.current_item.number,
          },
        ]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to start session');
      } finally {
        setIsLoading(false);
      }
    }

    initSession();
  }, [participantId, language, t.dose.welcomeMessage, t.dose.itemPrompt]);

  const handleResponse = async (value: number) => {
    if (!sessionId || !currentItem || isLoading) return;

    setIsLoading(true);
    setSelectedValue(value);

    // Add user response message
    const responseLabel = t.likert.labels[value - 1];
    setMessages((prev) => [
      ...prev,
      {
        id: `user-${Date.now()}`,
        role: 'user',
        content: `${value} - ${responseLabel}`,
      },
    ]);

    try {
      const response: DOSERespondResponse = await respondDOSEChatbot(sessionId, value);

      setTraitProgress(response.current_estimates);
      setTotalItems(response.progress.items_administered);

      if (response.action === 'complete') {
        setIsComplete(true);
        setCurrentItem(null);
        const reductionMessage = t.dose.itemReductionMessage.replace('{count}', response.progress.items_administered.toString());
        setMessages((prev) => [
          ...prev,
          {
            id: `complete-${Date.now()}`,
            role: 'assistant',
            content: `${t.dose.completeMessage}\n\n${reductionMessage}`,
          },
        ]);
      } else if (response.next_item) {
        const nextItem = response.next_item;
        const nextItemText = getItemText(nextItem.number, language);
        setCurrentItem(nextItem);
        setSelectedValue(null);
        setMessages((prev) => [
          ...prev,
          {
            id: `item-${Date.now()}`,
            role: 'assistant',
            content: `${t.dose.nextItemIntro}\n\n"${nextItemText}"\n\n${t.dose.itemPrompt}`,
            itemNumber: nextItem.number,
          },
        ]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit response');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFinish = () => {
    router.push(`/assessment/${participantId}`);
  };

  if (error) {
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

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="font-bold text-lg">{t.dose.title}</h1>
            <p className="text-sm text-gray-500">
              {t.dose.questionsLabel}: {totalItems} | {t.dose.seThreshold}
            </p>
          </div>
          <div className="flex items-center gap-4">
            {/* Trait progress indicators */}
            <div className="hidden md:flex gap-2">
              {Object.entries(traitProgress).map(([trait, data]) => (
                <div
                  key={trait}
                  className={`px-2 py-1 text-xs rounded ${
                    data.completed
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                  title={`${trait}: SE=${data.se.toFixed(3)}`}
                >
                  {trait.substring(0, 3).toUpperCase()}
                  {data.completed && ' ✓'}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 overflow-hidden bg-gray-50">
        <div className="h-full max-w-4xl mx-auto">
          <ChatContainer messages={messages} isTyping={isLoading}>
            {!isComplete && currentItem && (
              <div className="space-y-4">
                <LikertScale
                  onSelect={handleResponse}
                  disabled={isLoading}
                  selected={selectedValue}
                />
                <div className="text-center text-sm text-gray-500">
                  {t.dose.assessingLabel}: {t.traits[currentItem.trait as keyof typeof t.traits] || currentItem.trait.replace('_', ' ')}
                </div>
              </div>
            )}
            {isComplete && (
              <div className="text-center">
                <button
                  onClick={handleFinish}
                  className="px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors"
                >
                  {t.dose.continueButton}
                </button>
              </div>
            )}
          </ChatContainer>
        </div>
      </div>
    </div>
  );
}
