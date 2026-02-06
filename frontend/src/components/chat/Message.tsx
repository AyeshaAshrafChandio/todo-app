'use client';

import React from 'react';
import type { Message as MessageType } from '@/lib/types/chat';
import { cn } from '@/lib/utils';

interface MessageProps {
  message: MessageType;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';
  const isError = message.status === 'error';

  // Format timestamp
  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  return (
    <div
      className={cn(
        'flex w-full mb-4',
        isUser ? 'justify-end' : 'justify-start'
      )}
      role="article"
      aria-label={`${isUser ? 'User' : 'AI assistant'} message: ${message.content}`}
    >
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-4 py-3 shadow-sm',
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100',
          isError && 'border-2 border-red-500'
        )}
      >
        {/* Message content */}
        <div className="whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {/* Timestamp and status */}
        <div
          className={cn(
            'mt-2 text-xs flex items-center gap-2',
            isUser ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
          )}
        >
          <span>{formatTime(message.timestamp)}</span>
          {message.status === 'sending' && (
            <span className="italic">Sending...</span>
          )}
          {isError && (
            <span className="text-red-500 font-medium">Failed to send</span>
          )}
        </div>
      </div>
    </div>
  );
}
