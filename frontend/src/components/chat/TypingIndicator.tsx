'use client';

import React from 'react';

export function TypingIndicator() {
  return (
    <div className="flex w-full mb-4 justify-start" aria-live="polite">
      <div className="max-w-[80%] rounded-lg px-4 py-3 bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-sm">AI is typing</span>
          <div className="flex gap-1">
            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
