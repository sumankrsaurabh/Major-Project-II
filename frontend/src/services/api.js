import axios from 'axios';

/**
 * HttpClient - Singleton class wrapping axios to manage global configs.
 */
class HttpClient {
  constructor() {
    if (HttpClient.instance) {
      return HttpClient.instance;
    }

    this.client = axios.create({
      baseURL: '', // Handled by Vite proxy
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 300000, // 5 min timeout for processing large PDFs
    });

    // Interceptors for requests/responses can go here
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        const errorMsg = error.response?.data?.detail || error.message || 'An unexpected error occurred';
        console.error('API Error:', errorMsg);
        return Promise.reject(new Error(errorMsg));
      }
    );

    HttpClient.instance = this;
  }

  getClient() {
    return this.client;
  }
}

const httpClientInstance = new HttpClient();
export const client = httpClientInstance.getClient();

/**
 * BaseApiService - Implements Template Method Pattern for API calls.
 */
class BaseApiService {
  constructor() {
    this.http = client;
  }

  async request(method, url, data = null, config = {}) {
    try {
      const response = await this.http({
        method,
        url,
        data,
        ...config,
      });
      return response.data;
    } catch (error) {
      this.handleError(error, url);
      throw error;
    }
  }

  handleError(error, url) {
    console.error(`Error in call to ${url}:`, error.message);
  }
}

/**
 * PDFService - Handles operations related to PDF document upload and status.
 */
class PDFService extends BaseApiService {
  async uploadPDF(file, onUploadProgress) {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request('POST', '/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  }

  async getStatus() {
    return this.request('GET', '/status');
  }

  async getHealth() {
    return this.request('GET', '/health');
  }
}

/**
 * ChatService - Manages chat dialogue and conversational context retrieval.
 */
class ChatService extends BaseApiService {
  async askQuestion(question, sessionId = null) {
    return this.request('POST', '/chat', {
      question,
      session_id: sessionId,
    });
  }

  async clearConversation(sessionId) {
    return this.request('POST', '/clear-conversation', {
      session_id: sessionId,
    });
  }
}

/**
 * AnalysisService - Exposes the backend's rich NLP and machine learning capabilities.
 */
class AnalysisService extends BaseApiService {
  async analyzeDocument(text, detailed = true) {
    const response = await this.request('POST', '/api/analysis/document', {
      text,
      detailed,
    });
    if (response.status === 'success') {
      return response.data;
    }
    throw new Error(response.error || 'Failed to analyze document');
  }

  async analyzeQuery(query) {
    const response = await this.request('POST', '/api/analysis/query', {
      query,
    });
    if (response.status === 'success') {
      return response.data;
    }
    throw new Error(response.error || 'Failed to analyze query');
  }

  async extractInsights(text) {
    const response = await this.request('POST', '/api/analysis/insights', {
      text,
    });
    if (response.status === 'success') {
      return response.data;
    }
    throw new Error(response.error || 'Failed to extract insights');
  }

  async compareTexts(text1, text2) {
    const response = await this.request('POST', '/api/analysis/compare', {
      text1,
      text2,
    });
    if (response.status === 'success') {
      return response.data;
    }
    throw new Error(response.error || 'Failed to compare texts');
  }

  async generateAnswer(question, context) {
    const response = await this.request('POST', '/api/analysis/answer', {
      question,
      context,
    });
    if (response.status === 'success') {
      return response.data;
    }
    throw new Error(response.error || 'Failed to generate answer');
  }

  async getCapabilities() {
    const response = await this.request('GET', '/api/analysis/capabilities');
    if (response.status === 'success') {
      return response.data;
    }
    throw new Error(response.error || 'Failed to get capabilities');
  }
}

// Export Singleton Service Instances
export const pdfService = new PDFService();
export const chatService = new ChatService();
export const analysisService = new AnalysisService();
export default { pdfService, chatService, analysisService };
