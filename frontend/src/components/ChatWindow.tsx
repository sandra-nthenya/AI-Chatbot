import React, { useState, useRef, useEffect } from 'react';
import type { Theme } from './ChatWidget';
import { apiService, mockApiService, type Message } from '../services/api';

interface ChatWindowProps {
  onClose: () => void;
  theme: 'light' | 'dark';
}

const windowStyle: React.CSSProperties = {
  position: 'absolute',
  bottom: 72,
  right: 0,
  width: 340,
  height: 480,
  background: 'var(--chat-bg)',
  borderRadius: 16,
  boxShadow: '0 4px 24px rgba(0,0,0,0.18)',
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
};

const headerStyle: React.CSSProperties = {
  background: 'var(--chat-header-bg)',
  color: 'var(--chat-header-text)',
  padding: '1rem',
  fontWeight: 600,
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
};

const messagesStyle: React.CSSProperties = {
  flex: 1,
  padding: '1rem',
  overflowY: 'auto',
  background: 'var(--chat-messages-bg)',
  display: 'flex',
  flexDirection: 'column',
  gap: '0.5rem',
};

const inputContainerStyle: React.CSSProperties = {
  display: 'flex',
  borderTop: '1px solid var(--chat-input-border)',
  padding: '0.75rem',
  background: 'var(--chat-input-bg)',
};

const inputStyle: React.CSSProperties = {
  flex: 1,
  border: '1px solid var(--chat-input-border)',
  borderRadius: 8,
  padding: '0.5rem 1rem',
  fontSize: 16,
  outline: 'none',
  background: 'var(--chat-input-bg)',
  color: 'var(--chat-input-text)',
};

const sendButtonStyle: React.CSSProperties = {
  marginLeft: 8,
  background: 'var(--chat-send-bg)',
  color: 'var(--chat-send-text)',
  border: 'none',
  borderRadius: 8,
  padding: '0.5rem 1.25rem',
  fontWeight: 600,
  cursor: 'pointer',
  fontSize: 16,
};

const loadingStyle: React.CSSProperties = {
  alignSelf: 'flex-start',
  background: 'var(--chat-bot-bg)',
  color: 'var(--chat-bot-text)',
  borderRadius: 16,
  padding: '0.5rem 1rem',
  maxWidth: '80%',
  fontSize: 15,
  fontStyle: 'italic',
  opacity: 0.7,
};

const messageBubble = (sender: 'user' | 'bot'): React.CSSProperties => ({
  alignSelf: sender === 'user' ? 'flex-end' : 'flex-start',
  background: sender === 'user' ? 'var(--chat-user-bg)' : 'var(--chat-bot-bg)',
  color: sender === 'user' ? 'var(--chat-user-text)' : 'var(--chat-bot-text)',
  borderRadius: 16,
  padding: '0.5rem 1rem',
  maxWidth: '80%',
  fontSize: 15,
  boxShadow: sender === 'user' ? '0 2px 8px var(--chat-user-shadow)' : '0 2px 8px var(--chat-bot-shadow)',
});

const ChatWindow: React.FC<ChatWindowProps> = ({ onClose }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [useMockApi, setUseMockApi] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session and load messages
  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Try real API first
        const service = apiService;
        await service.healthCheck();
        
        // Create session
        const { session_id } = await service.createSession();
        setSessionId(session_id);
        
        // Load existing messages
        const existingMessages = await service.getMessages(session_id);
        setMessages(existingMessages);
        
        setUseMockApi(false);
      } catch (error) {
        console.warn('Real API not available, using mock service:', error);
        setUseMockApi(true);
        
        // Use mock service
        const { session_id } = await mockApiService.createSession();
        setSessionId(session_id);
        
        // Add welcome message
        setMessages([
          {
            id: 'welcome',
            session_id,
            sender: 'bot',
            content: 'How can we help you?',
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    };

    initializeChat();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !sessionId || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      session_id: sessionId,
      sender: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const service = useMockApi ? mockApiService : apiService;
      const response = await service.sendMessage({
        message: input,
        session_id: sessionId,
      });

      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        session_id: sessionId,
        sender: 'bot',
        content: response.message,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        session_id: sessionId,
        sender: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={windowStyle}>
      <div style={headerStyle}>
        AI Chat Support {useMockApi && '(Mock)'}
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--chat-header-text)', fontSize: 20, cursor: 'pointer' }}>&times;</button>
      </div>
      <div style={messagesStyle}>
        {messages.map((msg) => (
          <div key={msg.id} style={messageBubble(msg.sender)}>{msg.content}</div>
        ))}
        {isLoading && (
          <div style={loadingStyle}>AI is thinking...</div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div style={inputContainerStyle}>
        <input
          style={inputStyle}
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button 
          style={{...sendButtonStyle, opacity: isLoading ? 0.6 : 1}} 
          onClick={handleSend}
          disabled={isLoading}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatWindow; 