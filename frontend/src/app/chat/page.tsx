import type { Metadata } from 'next';
import { ChatPageClient } from './ChatPageClient';

export const metadata: Metadata = {
  title: 'Chat - AI Todo Assistant',
  description: 'Chat with your AI Todo Assistant to manage tasks through natural language',
};

export default function ChatPage() {
  return <ChatPageClient />;
}
