import React, { useState, useRef, useEffect } from 'react';
import { askQuestion } from '../services/api';
import './ChatInterface.css';

function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: 'Hello! I\'ve analyzed your PDF. Feel free to ask me any questions about it.',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await askQuestion(userMessage);

      const botMessage = {
        id: messages.length + 2,
        type: 'bot',
        text: response.answer || response.answer,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError(err.message || 'Failed to get an answer. Please try again.');

      const errorMessage = {
        id: messages.length + 2,
        type: 'bot-error',
        text: `Error: ${err.message}`,
        timestamp: new Date(),
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
    setMessages([
      {
        id: 1,
        type: 'bot',
        text: 'Chat cleared. Feel free to ask me new questions!',
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Chat</h2>
        <button className="clear-btn" onClick={clearChat} title="Clear chat">
          🗑️
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              {message.type === 'user' && <span className="user-icon">👤</span>}
              {(message.type === 'bot' || message.type === 'bot-error') && (
                <span className="bot-icon">🤖</span>
              )}
              <div className="message-text">
                <p>{message.text}</p>
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
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="chat-error">
          <span>⚠️ {error}</span>
        </div>
      )}

      <div className="chat-input-area">
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your PDF..."
            disabled={isLoading}
            rows="1"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="send-btn"
          >
            ➤
          </button>
        </div>
        <p className="input-hint">Press Enter to send, Shift+Enter for new line</p>
      </div>
    </div>
  );
}

export default ChatInterface;
