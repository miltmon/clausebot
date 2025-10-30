import { Router, Response } from 'express';
import { createClient } from '@supabase/supabase-js';
import { RequestWithAuth, SearchResponse, SearchQuery } from '../types';

const router = Router();

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
const supabase = createClient(supabaseUrl, supabaseKey);

router.get('/search', async (req: RequestWithAuth, res: Response<SearchResponse>) => {
  const query: SearchQuery = {
    q: req.query.q as string || '',
    limit: parseInt(req.query.limit as string) || 10,
    offset: parseInt(req.query.offset as string) || 0,
    category: req.query.category as string
  };

  if (!query.q) {
    return res.status(400).json({
      error: 'Bad Request',
      message: 'Query parameter "q" is required',
      code: 'SEARCH_MISSING_QUERY',
      requestId: req.requestId || 'unknown',
      timestamp: new Date().toISOString()
    } as any);
  }

  try {
    // Build the search query for AWS CWI Questions table
    let searchQuery = supabase
      .from('aws_cwi_questions')
      .select(`
        id,
        question_id,
        scenario,
        specific_challenge,
        answer_choice_a,
        answer_choice_b,
        answer_choice_c,
        answer_choice_d,
        correct_answer,
        difficulty_level,
        primary_code_reference,
        explanation,
        question_category,
        critical_thinking,
        field_situation
      `)
      .range(query.offset, query.offset + query.limit - 1);

    // Add text search across multiple fields
    if (query.q) {
      searchQuery = searchQuery.or(`
        scenario.ilike.%${query.q}%,
        specific_challenge.ilike.%${query.q}%,
        primary_code_reference.ilike.%${query.q}%,
        explanation.ilike.%${query.q}%,
        question_category.ilike.%${query.q}%
      `);
    }

    // Add category filter if specified
    if (query.category) {
      searchQuery = searchQuery.eq('question_category', query.category);
    }

    // Execute the query
    const { data, error, count } = await searchQuery;

    if (error) {
      console.error('Supabase search error:', error);
      return res.status(500).json({
        error: 'Internal Server Error',
        message: 'Search query failed',
        code: 'SEARCH_QUERY_ERROR',
        requestId: req.requestId || 'unknown',
        timestamp: new Date().toISOString()
      } as any);
    }

    // Transform Supabase data to SearchResult format
    const results = (data || []).map((item, index) => {
      // Calculate relevance based on match quality
      const relevance = calculateRelevance(query.q, item);
      
      return {
        id: item.question_id || item.id,
        title: `AWS D1.1 ${item.primary_code_reference || 'Question'} - ${item.question_category || 'General'}`,
        content: item.scenario || item.specific_challenge || 'No content available',
        category: item.question_category || 'General',
        relevance,
        metadata: {
          difficulty: item.difficulty_level,
          clause: item.primary_code_reference,
          explanation: item.explanation,
          critical_thinking: item.critical_thinking,
          field_situation: item.field_situation,
          options: {
            a: item.answer_choice_a,
            b: item.answer_choice_b,
            c: item.answer_choice_c,
            d: item.answer_choice_d
          },
          correct_answer: item.correct_answer
        }
      };
    });

    // Sort by relevance
    results.sort((a, b) => b.relevance - a.relevance);

    const searchResponse: SearchResponse = {
      query: query.q,
      results,
      total: count || results.length,
      limit: query.limit,
      offset: query.offset,
      requestId: req.requestId || 'unknown'
    };

    res.json(searchResponse);

  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({
      error: 'Internal Server Error',
      message: 'An unexpected error occurred during search',
      code: 'SEARCH_UNEXPECTED_ERROR',
      requestId: req.requestId || 'unknown',
      timestamp: new Date().toISOString()
    } as any);
  }
});

// Helper function to calculate search relevance
function calculateRelevance(searchTerm: string, item: any): number {
  const term = searchTerm.toLowerCase();
  let score = 0;

  // Exact matches get highest score
  const fields = [
    { field: item.primary_code_reference, weight: 1.0 },
    { field: item.question_category, weight: 0.8 },
    { field: item.scenario, weight: 0.6 },
    { field: item.specific_challenge, weight: 0.6 },
    { field: item.explanation, weight: 0.4 }
  ];

  for (const { field, weight } of fields) {
    if (field && typeof field === 'string') {
      const fieldLower = field.toLowerCase();
      if (fieldLower.includes(term)) {
        // Exact match gets full weight
        if (fieldLower === term) {
          score += weight * 1.0;
        }
        // Starts with term gets high weight
        else if (fieldLower.startsWith(term)) {
          score += weight * 0.8;
        }
        // Contains term gets medium weight
        else {
          score += weight * 0.5;
        }
      }
    }
  }

  // Normalize score to 0-1 range
  return Math.min(score, 1.0);
}

export default router;
