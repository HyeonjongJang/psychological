'use client';

import type { Message } from './ChatContainer';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isAssistant = message.role === 'assistant';

  return (
    <div className={`flex ${isAssistant ? 'justify-start' : 'justify-end'}`}>
      <div
        className={`
          max-w-[80%] rounded-2xl px-4 py-3 shadow-sm
          ${isAssistant
            ? 'bg-white text-gray-800 rounded-tl-sm'
            : 'bg-primary-600 text-white rounded-tr-sm'
          }
        `}
      >
        {isAssistant && (
          <div className="flex items-center gap-2 mb-1">
            <div className="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center">
              <span className="text-xs">AI</span>
            </div>
            <span className="text-xs text-gray-500">Assistant</span>
          </div>
        )}
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.itemNumber && (
          <div className="mt-2 text-xs opacity-70">
            Question {message.itemNumber}
          </div>
        )}
      </div>
    </div>
  );
}
