import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface StreamingTextProps {
  content: string;
  isStreaming: boolean;
  speed?: number; // characters per interval
}

const StreamingText: React.FC<StreamingTextProps> = ({ 
  content, 
  isStreaming, 
  speed = 3 
}) => {
  const [displayedContent, setDisplayedContent] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!isStreaming) {
      // If not streaming, show full content immediately
      setDisplayedContent(content);
      setCurrentIndex(content.length);
      return;
    }

    // Typewriter effect
    if (currentIndex < content.length) {
      const timer = setTimeout(() => {
        const nextIndex = Math.min(currentIndex + speed, content.length);
        setDisplayedContent(content.slice(0, nextIndex));
        setCurrentIndex(nextIndex);
      }, 30); // 30ms interval for smooth animation

      return () => clearTimeout(timer);
    }
  }, [content, currentIndex, isStreaming, speed]);

  // Reset when content changes significantly (new message)
  useEffect(() => {
    if (content.length < displayedContent.length) {
      setDisplayedContent('');
      setCurrentIndex(0);
    }
  }, [content.length, displayedContent.length]);

  return (
    <div className="relative">
      <ReactMarkdown
        className="prose prose-sm max-w-none"
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={oneDark}
                language={match[1]}
                PreTag="div"
                className="rounded-md my-2"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className="bg-gray-100 text-red-600 px-1 py-0.5 rounded text-sm" {...props}>
                {children}
              </code>
            );
          },
          p({ children }) {
            return <p className="mb-2 last:mb-0">{children}</p>;
          },
          ul({ children }) {
            return <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>;
          },
          ol({ children }) {
            return <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>;
          },
          h1({ children }) {
            return <h1 className="text-xl font-bold mb-2 mt-3">{children}</h1>;
          },
          h2({ children }) {
            return <h2 className="text-lg font-bold mb-2 mt-3">{children}</h2>;
          },
          h3({ children }) {
            return <h3 className="text-md font-semibold mb-2 mt-2">{children}</h3>;
          },
          blockquote({ children }) {
            return (
              <blockquote className="border-l-4 border-gray-300 pl-4 italic my-2 text-gray-700">
                {children}
              </blockquote>
            );
          },
          a({ href, children }) {
            return (
              <a 
                href={href} 
                className="text-blue-600 hover:underline" 
                target="_blank" 
                rel="noopener noreferrer"
              >
                {children}
              </a>
            );
          },
        }}
      >
        {displayedContent}
      </ReactMarkdown>
      
      {/* Blinking cursor during streaming */}
      {isStreaming && currentIndex < content.length && (
        <span className="inline-block w-2 h-4 bg-blue-600 ml-1 animate-blink" />
      )}
    </div>
  );
};

export default StreamingText;
