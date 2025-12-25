'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ChatContainer, { type Message } from '@/components/chat/ChatContainer';
import LikertScale from '@/components/ui/LikertScale';
import { startStaticChatbot, respondStaticChatbot } from '@/lib/api';

export default function StaticChatbotPage() {
  const params = useParams();
  const router = useRouter();
  const participantId = params.participantId as string;

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentItem, setCurrentItem] = useState<{ number: number; text: string } | null>(null);
  const [progress, setProgress] = useState('0/24');
  const [isComplete, setIsComplete] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedValue, setSelectedValue] = useState<number | null>(null);

  useEffect(() => {
    async function initSession() {
      setIsLoading(true);
      try {
        const response = await startStaticChatbot(participantId);
        setSessionId(response.session_id);
        setCurrentItem({ number: response.current_item, text: response.item_text });
        setProgress(`0/${response.total_items}`);

        setMessages([
          {
            id: '1',
            role: 'assistant',
            content: response.message,
          },
          {
            id: '2',
            role: 'assistant',
            content: `I "${response.item_text}"\n\nHow accurately does this describe you?`,
            itemNumber: response.current_item,
          },
        ]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to start session');
      } finally {
        setIsLoading(false);
      }
    }

    initSession();
  }, [participantId]);

  const handleResponse = async (value: number) => {
    if (!sessionId || !currentItem || isLoading) return;

    setIsLoading(true);
    setSelectedValue(value);

    const responseLabel = ['Very Inaccurate', 'Inaccurate', 'Somewhat Inaccurate', 'Neutral', 'Somewhat Accurate', 'Accurate', 'Very Accurate'][value - 1];
    setMessages((prev) => [
      ...prev,
      {
        id: `user-${Date.now()}`,
        role: 'user',
        content: `${value} - ${responseLabel}`,
      },
    ]);

    try {
      const response = await respondStaticChatbot(sessionId, value);
      setProgress(response.progress);

      if (response.is_complete) {
        setIsComplete(true);
        setCurrentItem(null);
        setMessages((prev) => [
          ...prev,
          {
            id: `complete-${Date.now()}`,
            role: 'assistant',
            content: response.message || 'Thank you for completing all 24 questions!',
          },
        ]);
      } else if (response.next_item_text) {
        setCurrentItem({ number: response.next_item_number!, text: response.next_item_text });
        setSelectedValue(null);
        setMessages((prev) => [
          ...prev,
          {
            id: `item-${Date.now()}`,
            role: 'assistant',
            content: `I "${response.next_item_text}"\n\nHow accurately does this describe you?`,
            itemNumber: response.next_item_number!,
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
          <h2 className="font-bold mb-2">Error</h2>
          <p>{error}</p>
          <button
            onClick={() => router.push(`/assessment/${participantId}`)}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Return to Hub
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
            <h1 className="font-bold text-lg">Static Chatbot</h1>
            <p className="text-sm text-gray-500">
              Progress: {progress}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500 transition-all duration-300"
                style={{ width: `${(parseInt(progress.split('/')[0]) / 24) * 100}%` }}
              />
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
              </div>
            )}
            {isComplete && (
              <div className="text-center">
                <button
                  onClick={handleFinish}
                  className="px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Continue to Next Assessment
                </button>
              </div>
            )}
          </ChatContainer>
        </div>
      </div>
    </div>
  );
}
