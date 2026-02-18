'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { sendMessage as sendMessageApi } from '@/lib/api/chat';
import type { Message, ChatState } from '@/lib/types/chat';

interface ChatContextValue extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  retryMessage: (messageId: string) => Promise<void>;
  clearError: () => void;
  setInputValue: (value: string) => void;
}

const ChatContext = createContext<ChatContextValue | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

export function ChatProvider({ children }: ChatProviderProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [conversationId, setConversationId] = useState<number | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Create user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
      status: 'sent',
    };

    // Add user message to state
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    setInputValue('');

    try {
      // Send message to API with conversation ID
      const response = await sendMessageApi(content.trim(), conversationId);

      // Update conversation ID if this is a new conversation
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Create AI message
      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: response.response, // Use 'response' field from backend
        timestamp: new Date(),
        status: 'sent',
      };

      // Add AI message to state
      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      // Handle error
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);

      // Update user message status to error
      setMessages(prev =>
        prev.map(msg =>
          msg.id === userMessage.id ? { ...msg, status: 'error' as const } : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  const retryMessage = useCallback(async (messageId: string) => {
    const message = messages.find(msg => msg.id === messageId);
    if (!message || message.role !== 'user') return;

    // Remove error message and retry
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
    await sendMessage(message.content);
  }, [messages, sendMessage]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: ChatContextValue = {
    messages,
    isLoading,
    error,
    inputValue,
    sendMessage,
    retryMessage,
    clearError,
    setInputValue,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
}
