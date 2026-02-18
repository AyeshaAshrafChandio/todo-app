'use client';

import React, { useState, useRef, KeyboardEvent } from 'react';
import { cn } from '@/lib/utils';

interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
  placeholder?: string;
}

const MAX_CHARACTERS = 10000;

export function MessageInput({
  value,
  onChange,
  onSend,
  disabled = false,
  placeholder = 'Type your message...',
}: MessageInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = useState(false);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter without Shift sends message
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !disabled) {
        onSend();
      }
    }

    // Escape clears input
    if (e.key === 'Escape') {
      onChange('');
      textareaRef.current?.blur();
    }
  };

  const handleSend = () => {
    if (value.trim() && !disabled) {
      onSend();
    }
  };

  const remainingChars = MAX_CHARACTERS - value.length;
  const isNearLimit = remainingChars < 100;
  const isOverLimit = remainingChars < 0;

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
      <div
        className={cn(
          'relative rounded-lg border transition-colors',
          isFocused
            ? 'border-blue-500 ring-2 ring-blue-500 ring-opacity-50'
            : 'border-gray-300 dark:border-gray-600',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          disabled={disabled}
          placeholder={placeholder}
          aria-label="Type your message"
          aria-describedby="char-counter"
          className="w-full px-4 py-3 pr-24 resize-none bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none min-h-[60px] max-h-[200px]"
          rows={2}
        />

        {/* Character counter */}
        {isNearLimit && (
          <div
            id="char-counter"
            className={cn(
              'absolute bottom-2 left-4 text-xs',
              isOverLimit ? 'text-red-500' : 'text-gray-500'
            )}
          >
            {remainingChars} characters remaining
          </div>
        )}

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim() || isOverLimit}
          aria-label="Send message"
          aria-disabled={disabled || !value.trim()}
          className={cn(
            'absolute bottom-2 right-2 px-4 py-2 rounded-md font-medium transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
            disabled || !value.trim() || isOverLimit
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500'
              : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'
          )}
        >
          Send
        </button>
      </div>

      {/* Helper text */}
      <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
