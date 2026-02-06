// Chat API client
import { apiClient } from './client';
import type { ChatRequest, ChatResponse } from '../types/chat';

/**
 * Send a message to the AI assistant
 * @param message - User message content
 * @returns AI assistant response
 */
export async function sendMessage(message: string): Promise<ChatResponse> {
  return apiClient<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message } as ChatRequest),
  });
}
