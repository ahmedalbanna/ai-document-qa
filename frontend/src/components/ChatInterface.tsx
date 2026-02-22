import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import apiService from '../services/api';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: any[];
  timestamp: Date;
  isStreaming?: boolean;
}

interface ChatInterfaceProps {
  documentId?: string;
  hasDocuments: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ documentId, hasDocuments }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [retryAttempt, setRetryAttempt] = useState(0);
  const [models, setModels] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [streamStats, setStreamStats] = useState<{ wordsPerSec: number; totalWords: number } | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const streamStartTimeRef = useRef<number>(0);
  const lastWordCountRef = useRef<number>(0);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load available models
    const loadModels = async () => {
      try {
        const response = await apiService.getModels();
        setModels(response.models);
        setSelectedModel(response.default);
      } catch (error) {
        console.error('Failed to load models:', error);
      }
    };
    loadModels();
  }, []);

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
    setIsSearching(true);
    setRetryAttempt(0);
    setStreamStats(null);

    // Create abort controller
    abortControllerRef.current = new AbortController();

    // Create placeholder for assistant message
    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      type: 'assistant',
      content: '',
      sources: [],
      timestamp: new Date(),
      isStreaming: true,
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      let fullAnswer = '';
      let sources: any[] = [];
      streamStartTimeRef.current = 0;
      lastWordCountRef.current = 0;

      await apiService.chatStream(
        userMessage.content,
        (chunk) => {
          if (streamStartTimeRef.current === 0) {
            streamStartTimeRef.current = Date.now();
          }
          
          fullAnswer += chunk;
          
          // Calculate streaming stats
          const wordCount = fullAnswer.trim().split(/\s+/).length;
          const elapsedSeconds = (Date.now() - streamStartTimeRef.current) / 1000;
          const wordsPerSec = elapsedSeconds > 0 ? wordCount / elapsedSeconds : 0;
          
          setStreamStats({ wordsPerSec, totalWords: wordCount });
          lastWordCountRef.current = wordCount;
          
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: fullAnswer, isStreaming: true }
                : msg
            )
          );
        },
        (receivedSources) => {
          sources = receivedSources;
          setIsSearching(false);
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
          const errorMessage = error.message.includes('cancelled') 
            ? 'Generation stopped by user.' 
            : `Error: ${error.message}. Please check your connection and try again.`;
          
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: errorMessage, isStreaming: false }
                : msg
            )
          );
          setIsSearching(false);
          setStreamStats(null);
        },
        () => {
          setIsLoading(false);
          setIsSearching(false);
          setStreamStats(null);
          // Mark streaming as complete
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, isStreaming: false }
                : msg
            )
          );
        },
        documentId,
        5,
        selectedModel || undefined,
        abortControllerRef.current.signal,
        (attempt) => {
          setRetryAttempt(attempt);
        }
      );
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, content: 'Error: Failed to get response. Please try again.', isStreaming: false }
            : msg
        )
      );
      setIsLoading(false);
      setIsSearching(false);
      setStreamStats(null);
    }
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  };

  const handleRegenerateResponse = async (messageId: string) => {
    // Find the message and the user message before it
    const messageIndex = messages.findIndex(m => m.id === messageId);
    if (messageIndex <= 0) return;
    
    const userMessageIndex = messageIndex - 1;
    const userMessage = messages[userMessageIndex];
    
    if (userMessage.type !== 'user') return;
    
    // Remove the old assistant message
    setMessages(prev => prev.filter(m => m.id !== messageId));
    
    // Resend the question
    setInput(userMessage.content);
    setTimeout(() => {
      const form = document.querySelector('form');
      if (form) {
        form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      }
    }, 100);
  };

  const handleCopyMessage = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      // Could add a toast notification here
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleExportConversation = () => {
    const markdown = messages.map(msg => {
      const header = msg.type === 'user' ? '## User' : '## Assistant';
      const timestamp = msg.timestamp.toLocaleString();
      let content = `${header}\n*${timestamp}*\n\n${msg.content}\n\n`;
      
      if (msg.sources && msg.sources.length > 0) {
        content += '### Sources\n';
        msg.sources.forEach((source, idx) => {
          content += `${idx + 1}. **${source.filename}** (Chunk #${source.chunk_id}, Relevance: ${(source.score * 100).toFixed(1)}%)\n`;
          content += `   > ${source.text}\n\n`;
        });
      }
      
      return content;
    }).join('---\n\n');
    
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversation-${new Date().toISOString().slice(0, 10)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Ctrl+K or Cmd+K to clear chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      clearChat();
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
              <MessageBubble 
                key={message.id} 
                message={message}
                onCopy={handleCopyMessage}
                onRegenerate={handleRegenerateResponse}
              />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        {/* Status indicators */}
        {(isSearching || retryAttempt > 0 || streamStats) && (
          <div className="mb-3 flex items-center justify-between text-xs">
            <div className="flex items-center space-x-3">
              {isSearching && (
                <span className="flex items-center text-blue-600">
                  <svg className="animate-spin h-3 w-3 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Searching documents...
                </span>
              )}
              {retryAttempt > 0 && (
                <span className="text-amber-600">
                  🔄 Retrying (attempt {retryAttempt}/3)...
                </span>
              )}
              {streamStats && (
                <span className="text-green-600">
                  ⚡ {streamStats.wordsPerSec.toFixed(1)} words/sec • {streamStats.totalWords} words
                </span>
              )}
            </div>
            {isLoading && (
              <button
                onClick={handleStopGeneration}
                className="text-red-600 hover:text-red-700 font-medium"
              >
                ⬛ Stop
              </button>
            )}
          </div>
        )}

        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            {messages.length > 0 && (
              <>
                <button
                  onClick={clearChat}
                  className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
                  title="Clear conversation"
                >
                  🗑️ Clear
                </button>
                <span className="text-gray-300">|</span>
                <button
                  onClick={handleExportConversation}
                  className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
                  title="Export as Markdown"
                >
                  📥 Export
                </button>
              </>
            )}
            <span className="text-xs text-gray-400 ml-2">
              Tip: Press Ctrl+K to clear
            </span>
          </div>
          
          {models.length > 0 && (
            <div className="flex items-center space-x-2">
              <label htmlFor="model-select" className="text-xs text-gray-600 font-medium">
                Model:
              </label>
              <select
                id="model-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              >
                {models.map((model) => (
                  <option key={model.name} value={model.name}>
                    {model.name === 'aya' && '🌍 '}
                    {model.name === 'llama3.2' && '⚡ '}
                    {model.name === 'llama2' && '📚 '}
                    {model.name} - {model.description}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
        
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
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
