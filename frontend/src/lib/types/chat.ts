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
  conversation_id: number | null;
}

export interface ToolCall {
  tool: string;
  arguments: Record<string, any>;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
}
