import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Copy, Check, AlertCircle } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const MAX_MESSAGES = 100;
const MAX_CHAR_LIMIT = 500;

export default function ChatWindow({ onUploadNew }) {
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('chat_history');
    if (saved) {
      try {
        return JSON.parse(saved).slice(-MAX_MESSAGES);
      } catch (e) {
        return [];
      }
    }
    return [{ 
      role: 'bot', 
      content: 'Hello! I have analyzed your document. Ask me any questions about it.',
      sources: [], 
      timestamp: new Date(),
      id: Date.now()
    }];
  });

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    try {
      const data = messages.slice(-MAX_MESSAGES);
      localStorage.setItem('chat_history', JSON.stringify(data));
    } catch (e) {
      console.warn('Failed to save chat history:', e);
    }
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = {
      role: 'user',
      content: input,
      timestamp: new Date(),
      id: Date.now()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    const fetchResponse = async (attempt = 0) => {
      const maxAttempts = 3;
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000);

        const response = await fetch(`${API_URL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: userMsg.content }),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || `HTTP ${response.status}`);
        }

        const data = await response.json();

        setMessages(prev => [...prev, {
          role: 'bot',
          content: data.answer || 'No response generated',
          sources: data.sources || [],
          status: data.status || 'success',
          confidence: data.confidence || 'unknown',
          timestamp: new Date(),
          id: Date.now()
        }]);

      } catch (error) {
        console.error(`Attempt ${attempt + 1} failed:`, error);

        if (error.name === 'AbortError' && attempt < maxAttempts - 1) {
          attempt++;
          await new Promise(r => setTimeout(r, 1000 * attempt));
          return fetchResponse(attempt);
        }

        const errorMsg = error.name === 'AbortError' 
          ? 'Request timeout. Server might be busy.'
          : error.message || 'Failed to get response';

        setMessages(prev => [...prev, {
          role: 'bot',
          content: `Error: ${errorMsg}\n\nPlease try again.`,
          sources: [],
          status: 'error',
          timestamp: new Date(),
          id: Date.now()
        }]);
      } finally {
        setIsLoading(false);
      }
    };

    await fetchResponse();
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, idx) => (
          <div 
            key={msg.id || idx} 
            className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-xs lg:max-w-md ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
              {/* Message Bubble */}
              <div className={`px-4 py-3 rounded-lg relative group ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-br-none' 
                  : 'bg-gray-100 text-gray-900 rounded-bl-none'
              }`}>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                
                {/* Copy Button */}
                <button
                  onClick={() => handleCopy(msg.content, msg.id)}
                  className={`absolute top-2 right-2 p-1.5 rounded opacity-0 group-hover:opacity-100 transition-opacity ${
                    msg.role === 'user' 
                      ? 'hover:bg-blue-700' 
                      : 'hover:bg-gray-200'
                  }`}
                >
                  {copiedId === msg.id ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <Copy className={`w-4 h-4 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`} />
                  )}
                </button>
              </div>

              {/* Sources */}
              {msg.role === 'bot' && msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 space-y-2">
                  <p className="text-xs font-semibold text-gray-600 uppercase">Sources:</p>
                  {msg.sources.map((src, cidx) => (
                    <div key={cidx} className="text-xs bg-gray-50 border border-gray-200 rounded p-2 text-gray-700">
                      <p className="line-clamp-2 font-mono">{src.content.substring(0, 120)}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Error Indicator */}
              {msg.role === 'bot' && msg.status === 'error' && (
                <div className="flex items-center gap-1 mt-2 text-xs text-red-600">
                  <AlertCircle className="w-3 h-3" />
                  Error
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-4">
            <div className="max-w-xs lg:max-w-md">
              <div className="px-4 py-3 rounded-lg rounded-bl-none bg-gray-100 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <span className="text-sm text-gray-600">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-gray-50 p-4">
        <form onSubmit={handleSend} className="space-y-2">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value.slice(0, MAX_CHAR_LIMIT))}
              placeholder="Ask a question..."
              className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              disabled={isLoading}
              maxLength={MAX_CHAR_LIMIT}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="flex justify-between text-xs text-gray-500">
            <span>AI can make mistakes. Verify important information.</span>
            <span>{input.length}/{MAX_CHAR_LIMIT}</span>
          </div>
        </form>
      </div>
    </div>
  );
}
