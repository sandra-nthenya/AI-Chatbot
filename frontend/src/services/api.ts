// API service for communicating with the backend

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Message {
  id?: string;
  session_id: string;
  sender: 'user' | 'bot';
  content: string;
  timestamp?: string;
}

export interface ChatSession {
  session_id: string;
  tenant_id?: string;
  user_id?: string;
  created_at?: string;
  last_activity?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  tenant_id?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/health');
  }

  // Create a new chat session
  async createSession(tenant_id?: string): Promise<{ session_id: string }> {
    const params = tenant_id ? `?tenant_id=${tenant_id}` : '';
    return this.request(`/sessions${params}`, {
      method: 'POST',
    });
  }

  // Get session details
  async getSession(session_id: string): Promise<ChatSession> {
    return this.request(`/sessions/${session_id}`);
  }

  // Send a chat message
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get chat history
  async getMessages(session_id: string): Promise<Message[]> {
    return this.request(`/chat/${session_id}/messages`);
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();

// Fallback mock service for development when backend is not available
export class MockApiService {
  private sessions: Map<string, Message[]> = new Map();

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return { status: 'healthy', timestamp: new Date().toISOString() };
  }

  async createSession(tenant_id?: string): Promise<{ session_id: string }> {
    const session_id = `mock-session-${Date.now()}`;
    this.sessions.set(session_id, []);
    return { session_id };
  }

  async getSession(session_id: string): Promise<ChatSession> {
    return {
      session_id,
      created_at: new Date().toISOString(),
      last_activity: new Date().toISOString(),
    };
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const session_id = request.session_id || `mock-session-${Date.now()}`;
    
    // Add user message to session
    const messages = this.sessions.get(session_id) || [];
    messages.push({
      id: `msg-${Date.now()}`,
      session_id,
      sender: 'user',
      content: request.message,
      timestamp: new Date().toISOString(),
    });

    // Generate mock bot response
    const botResponse = `Thanks for your message: "${request.message}". This is a mock response from the AI. (Session: ${session_id})`;
    
    messages.push({
      id: `msg-${Date.now() + 1}`,
      session_id,
      sender: 'bot',
      content: botResponse,
      timestamp: new Date().toISOString(),
    });

    this.sessions.set(session_id, messages);

    return {
      message: botResponse,
      session_id,
    };
  }

  async getMessages(session_id: string): Promise<Message[]> {
    return this.sessions.get(session_id) || [];
  }
}

export const mockApiService = new MockApiService(); 