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

// Predefined welding websets
const WELDING_WEBSETS = {
  general: '01k1mg4mgxy888g6ecgm2kd8ae', // Primary welding webset
  advanced: '01k5wykkgac0ddwcm6k9d7aar1', // Advanced welding webset
  standards: '01k1mg4mgxy888g6ecgm2kd8ae', // Standards-focused
  research: '01k5wykkgac0ddwcm6k9d7aar1', // Research and advanced topics
  safety: '01k1mg4mgxy888g6ecgm2kd8ae', // Safety guidelines
  procedures: '01k5wykkgac0ddwcm6k9d7aar1' // Advanced procedures
};

interface WebsetSearchResponse {
  webset_id: string;
  query: string;
  results: Array<{
    id: string;
    title: string;
    url: string;
    snippet: string;
    published_date?: string;
    author?: string;
    score: number;
    highlights?: string[];
    source_type: 'curated_web' | 'curated_research' | 'curated_standard';
  }>;
  total: number;
  requestId: string;
}

// Search within welding websets
router.get('/websets/search', async (req: RequestWithAuth, res: Response<WebsetSearchResponse>) => {
  const query = req.query.q as string || '';
  const websetType = (req.query.webset as keyof typeof WELDING_WEBSETS) || 'general';
  const numResults = parseInt(req.query.num_results as string) || 10;
  const includeHighlights = req.query.highlights === 'true';

  if (!query) {
    return res.status(400).json({
      error: 'Bad Request',
      message: 'Query parameter "q" is required',
      code: 'WEBSET_SEARCH_MISSING_QUERY',
      requestId: req.requestId || 'unknown',
      timestamp: new Date().toISOString()
    } as any);
  }

  try {
    const websetId = WELDING_WEBSETS[websetType];
    
    console.log(`Searching webset ${websetId} for: "${query}"`);

    // Search within the specific webset
    const searchParams = {
      query: query,
      numResults: Math.min(numResults, 50),
      useAutoprompt: true,
      includeText: true
    };

    // Use Exa's webset search functionality
    const exaClient = getExaClient();
    const exaResults = await exaClient.searchAndContents(searchParams);

    // Transform results with webset-specific enhancements
    const results = exaResults.results.map((result: any, index: number) => {
      // Determine source type for curated content
      let sourceType: 'curated_web' | 'curated_research' | 'curated_standard' = 'curated_web';
      const url = result.url.toLowerCase();
      
      if (url.includes('aws.org') || url.includes('asme.org') || url.includes('api.org') || 
          url.includes('iso.org') || url.includes('astm.org')) {
        sourceType = 'curated_standard';
      } else if (url.includes('research') || url.includes('journal') || url.includes('.edu') ||
                 url.includes('sciencedirect') || url.includes('ieee')) {
        sourceType = 'curated_research';
      }

      return {
        id: result.id || `webset-${websetId}-${index}`,
        title: result.title || 'Untitled',
        url: result.url,
        snippet: result.text ? result.text.substring(0, 400) + '...' : 'No content available',
        published_date: result.publishedDate || undefined,
        author: result.author || undefined,
        score: result.score || 0,
        highlights: result.highlights || [],
        source_type: sourceType
      };
    });

    const response: WebsetSearchResponse = {
      webset_id: websetId,
      query,
      results,
      total: results.length,
      requestId: req.requestId || 'unknown'
    };

    res.json(response);

  } catch (error) {
    console.error('Webset search error:', error);
    
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
      
      if (error.message.includes('webset')) {
        return res.status(404).json({
          error: 'Not Found',
          message: 'Webset not found or inaccessible',
          code: 'WEBSET_NOT_FOUND',
          requestId: req.requestId || 'unknown',
          timestamp: new Date().toISOString()
        } as any);
      }
    }

    res.status(500).json({
      error: 'Internal Server Error',
      message: 'Webset search failed',
      code: 'WEBSET_SEARCH_ERROR',
      requestId: req.requestId || 'unknown',
      timestamp: new Date().toISOString()
    } as any);
  }
});

// Get webset metadata and sample content
router.get('/websets/:websetId/info', async (req: RequestWithAuth, res: Response) => {
  const websetId = req.params.websetId;

  try {
    // Get a sample of content from the webset to show what's available
    const sampleResults = await exa.searchAndContents({
      query: 'welding standards procedures',
      numResults: 5,
      useAutoprompt: false,
      includeText: true
    });

    const websetInfo = {
      webset_id: websetId,
      name: getWebsetName(websetId),
      description: getWebsetDescription(websetId),
      sample_content: sampleResults.results.slice(0, 3).map((result: any) => ({
        title: result.title,
        url: result.url,
        snippet: result.text?.substring(0, 200) + '...' || ''
      })),
      total_estimated_documents: sampleResults.results.length * 20, // Rough estimate
      categories: ['welding', 'standards', 'procedures', 'safety', 'certification'],
      requestId: req.requestId || 'unknown'
    };

    res.json(websetInfo);

  } catch (error) {
    console.error('Webset info error:', error);
    res.status(500).json({
      error: 'Failed to fetch webset information',
      requestId: req.requestId || 'unknown'
    });
  }
});

// Search across multiple websets simultaneously
router.get('/websets/multi-search', async (req: RequestWithAuth, res: Response) => {
  const query = req.query.q as string || '';
  const websetTypes = (req.query.websets as string)?.split(',') || ['general', 'advanced'];
  const numResultsPerWebset = parseInt(req.query.num_results as string) || 5;

  if (!query) {
    return res.status(400).json({
      error: 'Bad Request',
      message: 'Query parameter "q" is required',
      code: 'MULTI_WEBSET_SEARCH_MISSING_QUERY',
      requestId: req.requestId || 'unknown',
      timestamp: new Date().toISOString()
    } as any);
  }

  try {
    console.log(`Multi-webset search for: "${query}" across websets: ${websetTypes.join(', ')}`);

    // Search each webset in parallel
    const searchPromises = websetTypes.map(async (websetType) => {
      const websetId = WELDING_WEBSETS[websetType as keyof typeof WELDING_WEBSETS];
      if (!websetId) return { webset_type: websetType, results: [], error: 'Unknown webset type' };

      try {
        const searchParams = {
          query,
          numResults: numResultsPerWebset,
          useAutoprompt: true,
          includeText: true
        };

        const exaResults = await exa.searchAndContents(searchParams);

        const results = exaResults.results.map((result: any, index: number) => ({
          id: `${websetType}-${result.id || index}`,
          title: result.title || 'Untitled',
          url: result.url,
          snippet: result.text ? result.text.substring(0, 300) + '...' : 'No content available',
          published_date: result.publishedDate || undefined,
          author: result.author || undefined,
          score: result.score || 0,
          webset_type: websetType,
          webset_id: websetId,
          source_type: determineSourceType(result.url)
        }));

        return {
          webset_type: websetType,
          webset_id: websetId,
          results,
          count: results.length
        };
      } catch (error) {
        console.error(`Error searching webset ${websetType}:`, error);
        return {
          webset_type: websetType,
          webset_id: websetId,
          results: [],
          error: error instanceof Error ? error.message : 'Search failed'
        };
      }
    });

    const websetResults = await Promise.all(searchPromises);

    // Combine and rank results
    const allResults = websetResults.flatMap(wr => 
      wr.results.map(r => ({ ...r, webset_name: getWebsetName(wr.webset_id || '') }))
    );

    // Sort by score and diversify by webset
    allResults.sort((a, b) => b.score - a.score);

    const response = {
      query,
      websets_searched: websetResults.map(wr => ({
        type: wr.webset_type,
        id: wr.webset_id,
        name: getWebsetName(wr.webset_id || ''),
        count: wr.count || 0,
        error: wr.error
      })),
      results: allResults,
      total: allResults.length,
      requestId: req.requestId || 'unknown'
    };

    res.json(response);

  } catch (error) {
    console.error('Multi-webset search error:', error);
    res.status(500).json({
      error: 'Internal Server Error',
      message: 'Multi-webset search failed',
      code: 'MULTI_WEBSET_SEARCH_ERROR',
      requestId: req.requestId || 'unknown',
      timestamp: new Date().toISOString()
    });
  }
});

// List available websets
router.get('/websets', async (req: RequestWithAuth, res: Response) => {
  const websets = Object.entries(WELDING_WEBSETS).map(([type, id]) => ({
    type,
    webset_id: id,
    name: getWebsetName(id),
    description: getWebsetDescription(id),
    categories: getWebsetCategories(type)
  }));

  res.json({
    websets,
    total: websets.length,
    requestId: req.requestId || 'unknown'
  });
});

// Helper functions
function getWebsetName(websetId: string): string {
  const names: Record<string, string> = {
    '01k1mg4mgxy888g6ecgm2kd8ae': 'Welding Industry Knowledge Base',
    '01k5wykkgac0ddwcm6k9d7aar1': 'Advanced Welding Research & Procedures'
  };
  return names[websetId] || 'Unknown Webset';
}

function getWebsetDescription(websetId: string): string {
  const descriptions: Record<string, string> = {
    '01k1mg4mgxy888g6ecgm2kd8ae': 'Curated collection of welding standards, procedures, safety guidelines, and industry best practices from authoritative sources.',
    '01k5wykkgac0ddwcm6k9d7aar1': 'Advanced welding research, cutting-edge procedures, metallurgy studies, and specialized welding techniques from academic and industry sources.'
  };
  return descriptions[websetId] || 'No description available';
}

function getWebsetCategories(type: string): string[] {
  const categories: Record<string, string[]> = {
    general: ['welding', 'standards', 'procedures', 'safety'],
    advanced: ['research', 'metallurgy', 'advanced-procedures', 'innovation'],
    standards: ['AWS', 'ASME', 'API', 'ISO', 'ASTM'],
    research: ['metallurgy', 'materials', 'innovation', 'testing'],
    safety: ['OSHA', 'PPE', 'hazards', 'regulations'],
    procedures: ['WPS', 'PQR', 'advanced-techniques', 'automation']
  };
  return categories[type] || ['welding'];
}

function determineSourceType(url: string): 'curated_web' | 'curated_research' | 'curated_standard' {
  const urlLower = url.toLowerCase();
  
  if (urlLower.includes('aws.org') || urlLower.includes('asme.org') || urlLower.includes('api.org') || 
      urlLower.includes('iso.org') || urlLower.includes('astm.org')) {
    return 'curated_standard';
  } else if (urlLower.includes('research') || urlLower.includes('journal') || urlLower.includes('.edu') ||
             urlLower.includes('sciencedirect') || urlLower.includes('ieee')) {
    return 'curated_research';
  }
  return 'curated_web';
}

export default router;
