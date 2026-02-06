// Chat types for AI Todo Chatbot

export type MessageRole = 'user' | 'assistant';

export type MessageStatus = 'sending' | 'sent' | 'error';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  status: MessageStatus;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  inputValue: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  reply: string;
}
