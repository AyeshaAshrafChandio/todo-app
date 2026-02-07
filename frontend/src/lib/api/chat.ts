// Chat API client
import { apiClient } from './client';
import type { ChatRequest, ChatResponse } from '../types/chat';

/**
 * Send a message to the AI assistant
 * @param message - User message content
 * @param conversationId - Optional conversation ID to continue existing conversation
 * @returns AI assistant response
 */
export async function sendMessage(
  message: string,
  conversationId: number | null = null
): Promise<ChatResponse> {
  return apiClient<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    } as ChatRequest),
  });
}
