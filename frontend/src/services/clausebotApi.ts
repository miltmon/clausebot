// ClauseBot.Ai API Integration
const API_BASE_URL = 'https://clausebot-api.onrender.com';

export interface Question {
  id: string;
  question: string;
  category: string;
  difficulty: 'basic' | 'intermediate' | 'advanced';
  tags: string[];
}

export interface Answer {
  id: string;
  answer: string;
  confidence: number;
  citations: string[];
  verdict: 'VERIFIED' | 'INSUFFICIENT_EVIDENCE' | 'ERROR';
  timestamp: string;
}

export interface VerifyAnswerRequest {
  question: string;
  intent: 'audit' | 'clause_lookup' | 'study_help' | 'visual' | 'fallback';
  mode: 'audit' | 'standard';
}

class ClauseBotAPIService {
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} - ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`ClauseBot API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Health check endpoints
  async checkHealth(): Promise<{ status: string }> {
    return this.makeRequest('/ready');
  }

  async getEdition(): Promise<{ version: string; edition: string }> {
    return this.makeRequest('/v1/edition');
  }

  // Question search
  async searchQuestions(query: string): Promise<Question[]> {
    return this.makeRequest(`/v1/questions/search?q=${encodeURIComponent(query)}`);
  }

  // Answer verification
  async verifyAnswer(request: VerifyAnswerRequest): Promise<Answer> {
    return this.makeRequest('/v1/answers/verify', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get question by ID
  async getQuestion(id: string): Promise<Question> {
    return this.makeRequest(`/v1/questions/${id}`);
  }

  // Get answer by ID  
  async getAnswer(id: string): Promise<Answer> {
    return this.makeRequest(`/v1/answers/${id}`);
  }
}

export const clausebotApi = new ClauseBotAPIService();
export default clausebotApi;