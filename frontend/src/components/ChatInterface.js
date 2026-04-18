import React, { useState, useRef, useEffect, useCallback } from 'react';
import { askQuestion } from '../services/api';
import { formatResponse, parseMarkdown } from '../utils/formatting';
import './ChatInterface.css';

function ChatInterface({ onStatsUpdate, onMessageUpdate, sessionId: sessionIdProp }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: 'Hello! I\'ve analyzed your PDF. Ask me any questions about it.',
      timestamp: new Date(),
      formatted: true,
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [sessionId] = useState(sessionIdProp || Math.random().toString(36).substring(7));
  const [stats, setStats] = useState({ total: 0, avgConfidence: 0, activeTime: '0s' });
  const [startTime] = useState(Date.now());
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const timerRef = useRef(null);

  // Update active time
  useEffect(() => {
    timerRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      const minutes = Math.floor(elapsed / 60);
      const seconds = elapsed % 60;
      const timeStr = `${minutes}m ${seconds}s`;
      
      setStats(prev => ({
        ...prev,
        activeTime: timeStr
      }));

      if (onStatsUpdate) {
        onStatsUpdate({
          total: stats.total,
          avgConfidence: stats.avgConfidence,
          activeTime: timeStr
        });
      }
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [startTime, stats.total, stats.avgConfidence, onStatsUpdate]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const updateStats = useCallback((confidence) => {
    setStats(prev => {
      const confValue = confidence === 'high' ? 1 : confidence === 'medium' ? 0.5 : 0.2;
      const newStats = {
        ...prev,
        total: prev.total + 1,
        avgConfidence: (prev.avgConfidence * prev.total + confValue) / (prev.total + 1)
      };

      if (onStatsUpdate) {
        onStatsUpdate({
          total: newStats.total,
          avgConfidence: newStats.avgConfidence,
          activeTime: prev.activeTime
        });
      }

      return newStats;
    });
  }, [onStatsUpdate]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError('');

    // Add user message to chat
    const newUserMessage = {
      id: messages.length + 1,
      type: 'user',
      text: userMessage,
      timestamp: new Date(),
      formatted: true,
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await askQuestion(userMessage, sessionId);

      // Format the response for better display
      const formattedAnswer = formatResponse(response.answer);

      const botMessage = {
        id: messages.length + 2,
        type: 'bot',
        text: response.answer,
        formattedText: formattedAnswer,
        timestamp: new Date(),
        status: response.status,
        confidence: response.confidence,
        documentCount: response.relevant_documents?.length || 0,
        documents: response.relevant_documents,
        formatted: true,
      };

      setMessages((prev) => [...prev, botMessage]);
      updateStats(response.confidence);

      // Call message update callback
      if (onMessageUpdate) {
        onMessageUpdate(botMessage);
      }
    } catch (err) {
      setError(err.message || 'Failed to get an answer. Please try again.');

      const errorMessage = {
        id: messages.length + 2,
        type: 'bot-error',
        text: `Error: ${err.message}`,
        timestamp: new Date(),
        formatted: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    const clearedStats = { total: 0, avgConfidence: 0, activeTime: '0s' };
    setMessages([
      {
        id: 1,
        type: 'bot',
        text: 'Chat cleared. Ready for new questions!',
        timestamp: new Date(),
        formatted: true,
      },
    ]);
    setStats(clearedStats);
    
    if (onStatsUpdate) {
      onStatsUpdate(clearedStats);
    }
  };

  const getConfidencePercentage = () => {
    return Math.round(stats.avgConfidence * 100);
  };

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              {message.type === 'user' && <span className="user-icon">👤</span>}
              {(message.type === 'bot' || message.type === 'bot-error') && (
                <span className="bot-icon">🤖</span>
              )}
              <div className="message-wrapper">
                <div className="message-text">
                  {message.formattedText ? (
                    <div className="formatted-content" dangerouslySetInnerHTML={{ __html: message.formattedText }} />
                  ) : (
                    <p>{message.text}</p>
                  )}
                </div>
                {message.type === 'bot' && (
                  <div className="message-metadata">
                    {message.confidence && (
                      <div className={`confidence-badge confidence-${message.confidence}`}>
                        {message.confidence === 'high' && '✓ High confidence'}
                        {message.confidence === 'medium' && '~ Medium confidence'}
                        {message.confidence === 'low' && '⚠ Low confidence'}
                      </div>
                    )}
                    {message.documentCount && (
                      <div className="doc-count">
                        📄 {message.documentCount} document{message.documentCount !== 1 ? 's' : ''}
                      </div>
                    )}
                    {message.status && (
                      <div className={`status-indicator status-${message.status}`}>
                        {message.status === 'success' ? '✓ Success' : '✗ Error'}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
            <span className="message-time">
              {message.timestamp.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          </div>
        ))}

        {isLoading && (
          <div className="message bot loading-message">
            <div className="message-content">
              <span className="bot-icon">🤖</span>
              <div className="message-text">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p className="loading-text">Thinking...</p>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="chat-error">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="chat-input-area">
        <div className="input-field">
          <input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your PDF..."
            disabled={isLoading}
          />
        </div>
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !inputValue.trim()}
          className="send-btn"
          title={isLoading ? 'Waiting for response...' : 'Send message'}
        >
          {isLoading ? 'Wait' : 'SEND'}
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;
