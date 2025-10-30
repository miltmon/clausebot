import { Request } from 'express';

export interface ApiKey {
  key: string;
  scope: 'READ_ONLY' | 'ADMIN';
}

export interface RequestWithAuth extends Request {
  apiKey?: ApiKey;
  requestId?: string;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  uptime: number;
  requestId: string;
}

export interface IntelResponse {
  service: string;
  version: string;
  environment: string;
  features: string[];
  capabilities: string[];
  requestId: string;
}

export interface SearchQuery {
  q: string;
  limit?: number;
  offset?: number;
  category?: string;
}

export interface SearchResult {
  id: string;
  title: string;
  content: string;
  category: string;
  relevance: number;
  metadata?: Record<string, any>;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
  limit: number;
  offset: number;
  requestId: string;
}

export interface QuizGenerateRequest {
  topic: string;
  count: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  category?: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: string;
  category: string;
  difficulty: string;
  explanation?: string;
}

export interface QuizGenerateResponse {
  topic: string;
  questions: QuizQuestion[];
  count: number;
  requestId: string;
}

export interface ApiError {
  error: string;
  message: string;
  code: string;
  requestId: string;
  timestamp: string;
}
