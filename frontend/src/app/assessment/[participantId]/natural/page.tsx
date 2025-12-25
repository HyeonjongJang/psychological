'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ChatContainer, { type Message } from '@/components/chat/ChatContainer';
import { startNaturalChatbot, sendNaturalMessage, analyzeNaturalConversation } from '@/lib/api';

export default function NaturalChatbotPage() {
  const params = useParams();
  const router = useRouter();
  const participantId = params.participantId as string;

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [turnCount, setTurnCount] = useState(0);
  const [canAnalyze, setCanAnalyze] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const MIN_TURNS = 10;

  useEffect(() => {
    async function initSession() {
      setIsLoading(true);
      try {
        const response = await startNaturalChatbot(participantId);
        setSessionId(response.session_id);
        setTurnCount(1);

        setMessages([
          {
            id: '1',
            role: 'assistant',
            content: response.message,
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

  const handleSendMessage = async () => {
    if (!sessionId || !inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setIsLoading(true);

    setMessages((prev) => [
      ...prev,
      {
        id: `user-${Date.now()}`,
        role: 'user',
        content: userMessage,
      },
    ]);

    try {
      const response = await sendNaturalMessage(sessionId, userMessage);
      setTurnCount(response.turn_count);
      setCanAnalyze(response.can_analyze);

      setMessages((prev) => [
        ...prev,
        {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.message,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleAnalyze = async () => {
    if (!sessionId || !canAnalyze) return;

    setIsAnalyzing(true);
    setMessages((prev) => [
      ...prev,
      {
        id: `system-${Date.now()}`,
        role: 'assistant',
        content: "I'm now analyzing our conversation to understand your personality traits. This may take a moment...",
      },
    ]);

    try {
      const response = await analyzeNaturalConversation(sessionId);
      setIsComplete(true);

      const traitSummary = Object.entries(response.inferred_traits)
        .map(([trait, data]) => {
          const label = trait.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase());
          return `${label}: ${data.score.toFixed(1)}/7`;
        })
        .join('\n');

      setMessages((prev) => [
        ...prev,
        {
          id: `result-${Date.now()}`,
          role: 'assistant',
          content: `Thank you for our conversation! Based on our chat, here's what I observed about your personality:\n\n${traitSummary}\n\nThis analysis was based on ${response.conversation_turns} conversation exchanges.`,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze conversation');
      setIsAnalyzing(false);
    }
  };

  const handleFinish = () => {
    router.push(`/assessment/${participantId}`);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (error && !sessionId) {
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
            <h1 className="font-bold text-lg">Natural Conversation</h1>
            <p className="text-sm text-gray-500">
              Exchanges: {turnCount} / {MIN_TURNS} minimum
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500 transition-all duration-300"
                style={{ width: `${Math.min((turnCount / MIN_TURNS) * 100, 100)}%` }}
              />
            </div>
            {canAnalyze && !isComplete && (
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {isAnalyzing ? 'Analyzing...' : 'Finish & Analyze'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 overflow-hidden bg-gray-50">
        <div className="h-full max-w-4xl mx-auto">
          <ChatContainer messages={messages} isTyping={isLoading || isAnalyzing}>
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

      {/* Input area */}
      {!isComplete && (
        <div className="bg-white border-t px-4 py-4">
          <div className="max-w-4xl mx-auto">
            {error && (
              <div className="mb-2 text-sm text-red-600">{error}</div>
            )}
            <div className="flex gap-3">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={isLoading || isAnalyzing}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading || isAnalyzing}
                className="px-6 py-3 bg-primary-600 text-white font-medium rounded-xl hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
            <p className="mt-2 text-xs text-gray-500 text-center">
              Have a natural conversation about yourself, your interests, and how you handle different situations.
              {!canAnalyze && ` (${MIN_TURNS - turnCount} more exchanges needed before analysis)`}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
