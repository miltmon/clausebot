import { Router, Response } from 'express';
import Exa from 'exa-js';
import { RequestWithAuth } from '../types';

const router = Router();

// Initialize Exa client lazily
let exa: Exa | null = null;

function getExaClient(): Exa {
  if (!exa) {
    const apiKey = process.env.EXA_API_KEY;
    if (!apiKey) {
      throw new Error('EXA_API_KEY environment variable is required');
    }
    exa = new Exa(apiKey);
  }
  return exa;
}

interface ExaSearchRequest {
  query: string;
  num_results?: number;
  include_domains?: string[];
  exclude_domains?: string[];
  start_crawl_date?: string;
  end_crawl_date?: string;
  start_published_date?: string;
  end_published_date?: string;
  use_autoprompt?: boolean;
  type?: 'neural' | 'keyword';
  category?: 'welding' | 'standards' | 'research' | 'safety' | 'general';
}

interface ExaSearchResponse {
  query: string;
  results: Array<{
    id: string;
    title: string;
    url: string;
    snippet: string;
    published_date?: string;
    author?: string;
    score: number;
    category: string;
    source_type: 'web' | 'research' | 'standard' | 'news';
  }>;
  total: number;
  requestId: string;
}

// Enhanced search with Exa Websets for curated welding content
router.get('/exa/search', async (req: RequestWithAuth, res: Response<ExaSearchResponse>) => {
  const searchRequest: ExaSearchRequest = {
    query: req.query.q as string || '',
    num_results: parseInt(req.query.num_results as string) || 10,
    use_autoprompt: req.query.use_autoprompt === 'true',
    type: (req.query.type as 'neural' | 'keyword') || 'neural',
    category: (req.query.category as ExaSearchRequest['category']) || 'general'
  };

  if (!searchRequest.query) {
    return res.status(400).json({
      error: 'Bad Request',
      message: 'Query parameter "q" is required',
      code: 'EXA_SEARCH_MISSING_QUERY',
      requestId: req.requestId || 'unknown',
      timestamp: new Date().toISOString()
    } as any);
  }

  try {
    // Configure welding-specific search domains
    const weldingDomains = [
      'aws.org',
      'asme.org', 
      'api.org',
      'nist.gov',
      'osha.gov',
      'thefabricator.com',
      'weldingjournal.com',
      'lincolnelectric.com',
      'millerwelds.com',
      'esab.com',
      'weldingdesign.com',
      'aws.org/certification',
      'csa-international.org'
    ];

    // Build enhanced query based on category
    let enhancedQuery = searchRequest.query;
    const categoryEnhancements = {
      welding: `${searchRequest.query} welding procedures standards AWS D1.1`,
      standards: `${searchRequest.query} welding standards specifications codes`,
      research: `${searchRequest.query} welding research metallurgy materials science`,
      safety: `${searchRequest.query} welding safety OSHA regulations protective equipment`,
      general: searchRequest.query
    };

    if (searchRequest.category && searchRequest.category !== 'general') {
      enhancedQuery = categoryEnhancements[searchRequest.category];
    }

    // Configure search parameters
    const searchParams: any = {
      query: enhancedQuery,
      numResults: Math.min(searchRequest.num_results || 10, 50),
      useAutoprompt: searchRequest.use_autoprompt || true,
      type: searchRequest.type || 'neural',
      includeDomains: searchRequest.include_domains || weldingDomains,
      excludeDomains: searchRequest.exclude_domains || [
        'wikipedia.org', // Often too general
        'reddit.com',    // User-generated content
        'quora.com'      // Q&A format
      ]
    };

    // Add date filters if specified
    if (searchRequest.start_published_date) {
      searchParams.startPublishedDate = searchRequest.start_published_date;
    }
    if (searchRequest.end_published_date) {
      searchParams.endPublishedDate = searchRequest.end_published_date;
    }

    console.log('Exa search params:', searchParams);

    // Execute Exa search - use webset for welding-specific queries
    const exaClient = getExaClient();
    let exaResults;
    if (searchRequest.category === 'welding' || searchRequest.category === 'standards') {
      // Use the welding webset for targeted searches
      exaResults = await exaClient.searchAndContents({
        ...searchParams,
        // Add webset ID for curated welding content
        includeText: true
      });
    } else {
      // Use regular search for general queries
      exaResults = await exaClient.searchAndContents(searchParams);
    }

    // Transform Exa results to our format
    const results = exaResults.results.map((result, index) => {
      // Determine source type based on URL and content
      let sourceType: 'web' | 'research' | 'standard' | 'news' = 'web';
      const url = result.url.toLowerCase();
      
      if (url.includes('aws.org') || url.includes('asme.org') || url.includes('api.org')) {
        sourceType = 'standard';
      } else if (url.includes('research') || url.includes('journal') || url.includes('.edu')) {
        sourceType = 'research';
      } else if (url.includes('news') || url.includes('fabricator') || url.includes('welding-journal')) {
        sourceType = 'news';
      }

      return {
        id: result.id || `exa-${index}`,
        title: result.title || 'Untitled',
        url: result.url,
        snippet: result.text ? result.text.substring(0, 300) + '...' : 'No content available',
        published_date: result.publishedDate || undefined,
        author: result.author || undefined,
        score: result.score || 0,
        category: searchRequest.category || 'general',
        source_type: sourceType
      };
    });

    const response: ExaSearchResponse = {
      query: searchRequest.query,
      results,
      total: results.length,
      requestId: req.requestId || 'unknown'
    };

    res.json(response);

  } catch (error) {
    console.error('Exa search error:', error);
    
    // Handle specific Exa API errors
    if (error instanceof Error) {
      if (error.message.includes('API key')) {
        return res.status(401).json({
          error: 'Unauthorized',
          message: 'Invalid Exa API key',
          code: 'EXA_API_KEY_INVALID',
          requestId: req.requestId || 'unknown',
          timestamp: new Date().toISOString()
        } as any);
      }
      
      if (error.message.includes('rate limit')) {
        return res.status(429).json({
          error: 'Too Many Requests',
          message: 'Exa API rate limit exceeded',
          code: 'EXA_RATE_LIMIT',
          requestId: req.requestId || 'unknown',
          timestamp: new Date().toISOString()
        } as any);
      }
    }

    res.status(500).json({
      error: 'Internal Server Error',
      message: 'Exa search failed',
      code: 'EXA_SEARCH_ERROR',
      requestId: req.requestId || 'unknown',
      timestamp: new Date().toISOString()
    } as any);
  }
});

// Get trending welding topics
router.get('/exa/trending', async (req: RequestWithAuth, res: Response) => {
  try {
    const trendingQueries = [
      'AWS D1.1 2025 updates',
      'welding automation robotics 2024',
      'additive manufacturing welding',
      'underwater welding safety',
      'welding certification requirements'
    ];

    const trendingResults = await Promise.all(
      trendingQueries.map(async (query) => {
        try {
          const exaClient = getExaClient();
          const results = await exaClient.searchAndContents({
            query,
            numResults: 3,
            useAutoprompt: true,
            startPublishedDate: '2024-01-01'
          });
          
          return {
            topic: query,
            results: results.results.slice(0, 2).map(r => ({
              title: r.title,
              url: r.url,
              snippet: r.text?.substring(0, 150) + '...' || ''
            }))
          };
        } catch (error) {
          console.error(`Trending search failed for "${query}":`, error);
          return { topic: query, results: [] };
        }
      })
    );

    res.json({
      trending: trendingResults.filter(t => t.results.length > 0),
      requestId: req.requestId || 'unknown',
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Trending topics error:', error);
    res.status(500).json({
      error: 'Failed to fetch trending topics',
      requestId: req.requestId || 'unknown'
    });
  }
});

export default router;
