import React, { useState } from 'react';
import StreamingText from './StreamingText';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: any[];
  timestamp: Date;
  isStreaming?: boolean;
}

interface MessageBubbleProps {
  message: Message;
  onCopy?: (content: string) => void;
  onRegenerate?: (messageId: string) => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onCopy, onRegenerate }) => {
  const [showSources, setShowSources] = useState(false);
  const [copied, setCopied] = useState(false);

  const isUser = message.type === 'user';

  const handleCopy = () => {
    if (onCopy) {
      onCopy(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRegenerate = () => {
    if (onRegenerate) {
      onRegenerate(message.id);
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
      <div className={`max-w-3xl ${isUser ? 'w-auto' : 'w-full'}`}>
        <div
          className={`
            rounded-lg px-4 py-3 shadow-sm transition-all duration-300
            ${isUser
              ? 'bg-blue-600 text-white'
              : 'bg-white border border-gray-200 text-gray-900'
            }
          `}
        >
          {/* Message Content */}
          <div className="break-words">
            {message.content ? (
              isUser ? (
                <div className="whitespace-pre-wrap">{message.content}</div>
              ) : (
                <StreamingText 
                  content={message.content} 
                  isStreaming={message.isStreaming || false}
                />
              )
            ) : (
              <div className="flex items-center space-x-2 text-gray-400">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <span className="text-sm">AI is thinking...</span>
              </div>
            )}
          </div>

          {/* Timestamp and Actions */}
          <div className="flex items-center justify-between mt-2">
            <div
              className={`
                text-xs
                ${isUser ? 'text-blue-100' : 'text-gray-500'}
              `}
            >
              {message.timestamp.toLocaleTimeString()}
            </div>
            
            {/* Message Actions */}
            {message.content && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleCopy}
                  className={`text-xs px-2 py-1 rounded transition-all ${
                    isUser 
                      ? 'text-blue-100 hover:bg-blue-500' 
                      : 'text-gray-500 hover:bg-gray-100'
                  }`}
                  title="Copy message"
                >
                  {copied ? '✓ Copied' : '📋 Copy'}
                </button>
                
                {!isUser && !message.isStreaming && onRegenerate && (
                  <button
                    onClick={handleRegenerate}
                    className="text-xs px-2 py-1 rounded text-gray-500 hover:bg-gray-100 transition-all"
                    title="Regenerate response"
                  >
                    🔄 Regenerate
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Sources Section */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2">
            <button
              onClick={() => setShowSources(!showSources)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
            >
              <svg
                className={`w-4 h-4 mr-1 transition-transform ${showSources ? 'rotate-90' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
              {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
            </button>

            {showSources && (
              <div className="mt-2 space-y-2">
                {message.sources.map((source, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-sm"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">
                          📄 {source.filename}
                        </p>
                        <p className="text-xs text-gray-500">
                          Chunk #{source.chunk_id} • Relevance: {(source.score * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                    <p className="text-gray-700 text-xs italic">
                      "{source.text}"
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
