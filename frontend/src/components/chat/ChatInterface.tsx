'use client';

import React from 'react';
import { useChat } from '@/contexts/ChatContext';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';
import { ErrorMessage } from './ErrorMessage';

export function ChatInterface() {
  const {
    messages,
    isLoading,
    error,
    inputValue,
    sendMessage,
    retryMessage,
    clearError,
    setInputValue,
  } = useChat();

  const handleSend = async () => {
    await sendMessage(inputValue);
  };

  const handleRetry = async () => {
    // Find the last failed user message
    const lastFailedMessage = [...messages]
      .reverse()
      .find(msg => msg.role === 'user' && msg.status === 'error');

    if (lastFailedMessage) {
      await retryMessage(lastFailedMessage.id);
    }
    clearError();
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          AI Todo Assistant
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Ask me to help you manage your tasks
        </p>
      </div>

      {/* Error message */}
      {error && (
        <div className="px-4 pt-4">
          <ErrorMessage message={error} onRetry={handleRetry} onDismiss={clearError} />
        </div>
      )}

      {/* Messages */}
      <MessageList messages={messages} />

      {/* Typing indicator */}
      {isLoading && (
        <div className="px-4">
          <TypingIndicator />
        </div>
      )}

      {/* Input */}
      <MessageInput
        value={inputValue}
        onChange={setInputValue}
        onSend={handleSend}
        disabled={isLoading}
      />
    </div>
  );
}
