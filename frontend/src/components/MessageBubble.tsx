import React, { useState } from 'react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: any[];
  timestamp: Date;
}

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const [showSources, setShowSources] = useState(false);

  const isUser = message.type === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-3xl ${isUser ? 'w-auto' : 'w-full'}`}>
        <div
          className={`
            rounded-lg px-4 py-3 shadow-sm
            ${isUser
              ? 'bg-blue-600 text-white'
              : 'bg-white border border-gray-200 text-gray-900'
            }
          `}
        >
          {/* Message Content */}
          <div className="whitespace-pre-wrap break-words">
            {message.content || (
              <span className="flex items-center text-gray-400">
                <svg className="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating response...
              </span>
            )}
          </div>

          {/* Timestamp */}
          <div
            className={`
              text-xs mt-2
              ${isUser ? 'text-blue-100' : 'text-gray-500'}
            `}
          >
            {message.timestamp.toLocaleTimeString()}
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
