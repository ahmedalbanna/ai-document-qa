import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import apiService from '../services/api';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: any[];
  timestamp: Date;
}

interface ChatInterfaceProps {
  documentId?: string;
  hasDocuments: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ documentId, hasDocuments }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Create placeholder for assistant message
    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      type: 'assistant',
      content: '',
      sources: [],
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      let fullAnswer = '';
      let sources: any[] = [];

      await apiService.chatStream(
        input,
        (chunk) => {
          fullAnswer += chunk;
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: fullAnswer }
                : msg
            )
          );
        },
        (receivedSources) => {
          sources = receivedSources;
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, sources: receivedSources }
                : msg
            )
          );
        },
        (error) => {
          console.error('Streaming error:', error);
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: 'Error: Failed to get response. Please try again.' }
                : msg
            )
          );
        },
        () => {
          setIsLoading(false);
        },
        documentId
      );
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, content: 'Error: Failed to get response. Please try again.' }
            : msg
        )
      );
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-[calc(100%-5rem)]">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-6xl mb-4">💬</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-500 max-w-md">
              {hasDocuments
                ? 'Ask any question about your uploaded documents. The AI will use RAG to find relevant information and provide accurate answers.'
                : 'Upload some documents first to start asking questions!'}
            </p>
            {hasDocuments && (
              <div className="mt-6 text-left">
                <p className="text-sm font-medium text-gray-700 mb-2">Example questions:</p>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• "What is the main topic of this document?"</li>
                  <li>• "Summarize the key points"</li>
                  <li>• "What does it say about [specific topic]?"</li>
                </ul>
              </div>
            )}
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="mb-2 text-xs text-gray-500 hover:text-gray-700 transition-colors"
          >
            Clear conversation
          </button>
        )}
        
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={hasDocuments ? "Ask a question about your documents..." : "Upload documents first..."}
            disabled={!hasDocuments || isLoading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!hasDocuments || !input.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {isLoading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Thinking...
              </span>
            ) : (
              'Send'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
