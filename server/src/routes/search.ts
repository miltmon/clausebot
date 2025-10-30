import { Router, Response } from 'express';
import { RequestWithAuth, SearchResponse, SearchQuery } from '../types';

const router = Router();

router.get('/search', (req: RequestWithAuth, res: Response<SearchResponse>) => {
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

  // Stub implementation - replace with real search logic
  const mockResults = [
    {
      id: 'clause-4-1',
      title: 'AWS D1.1 Clause 4.1 - General Requirements',
      content: 'This clause covers the general requirements for welding procedures...',
      category: 'Fundamentals',
      relevance: 0.95,
      metadata: {
        clause: '4.1',
        section: 'General Requirements'
      }
    },
    {
      id: 'clause-4-2',
      title: 'AWS D1.1 Clause 4.2 - Welding Procedure Specifications',
      content: 'Welding procedure specifications shall be established...',
      category: 'Procedures',
      relevance: 0.87,
      metadata: {
        clause: '4.2',
        section: 'WPS Requirements'
      }
    }
  ].filter(result => 
    result.title.toLowerCase().includes(query.q.toLowerCase()) ||
    result.content.toLowerCase().includes(query.q.toLowerCase())
  ).slice(query.offset, query.offset + query.limit);

  const searchResponse: SearchResponse = {
    query: query.q,
    results: mockResults,
    total: mockResults.length,
    limit: query.limit,
    offset: query.offset,
    requestId: req.requestId || 'unknown'
  };

  res.json(searchResponse);
});

export default router;
