'use client';

import { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

export interface Message {
  id: string;
  role: 'assistant' | 'user';
  content: string;
  itemNumber?: number;
}

interface ChatContainerProps {
  messages: Message[];
  isTyping?: boolean;
  children?: React.ReactNode;
}

export default function ChatContainer({ messages, isTyping = false, children }: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-container">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      {children && (
        <div className="border-t bg-white p-4">
          {children}
        </div>
      )}
    </div>
  );
}
