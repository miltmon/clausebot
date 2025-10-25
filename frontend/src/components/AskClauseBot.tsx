import React, { useState } from "react";
import { useOfflineCapability } from "@/hooks/useOfflineCapability";
import { toast } from "sonner";

const API_BASE = "https://clausebot-api.onrender.com/v1";

interface VerifyResponse {
  id?: string;
  answer?: string;
  confidence?: number;
  citations?: string[] | Array<{ standard: string; clause: string }>;
  verdict?: 'VERIFIED' | 'INSUFFICIENT_EVIDENCE' | 'ERROR' | 'CACHED';
  timestamp?: string;
  notes?: string[];
}

const AskClauseBot = () => {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<VerifyResponse | null>(null);
  const { 
    isOnline, 
    cacheQuestion, 
    cacheAnswer, 
    getCachedAnswer, 
    getRecentQuestions,
    hasOfflineData 
  } = useOfflineCapability();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    setLoading(true);
    setResponse(null);
    
    // Cache the question for offline use
    cacheQuestion(question);
    
    // Check for cached answer first if offline
    if (!isOnline) {
      const cachedAnswer = getCachedAnswer(question);
      if (cachedAnswer) {
        setResponse({
          answer: cachedAnswer.answer,
          verdict: 'CACHED',
          citations: cachedAnswer.citations,
          notes: ['This is a cached response from previous queries']
        });
        setLoading(false);
        toast.info('Showing cached response - you\'re currently offline', {
          description: 'Connect to internet for fresh results'
        });
        return;
      } else {
        setResponse({ 
          verdict: "INSUFFICIENT_EVIDENCE", 
          notes: ["offline_no_cache", "Connect to internet for fresh results"] 
        });
        setLoading(false);
        toast.warning('No cached data available for this query', {
          description: 'Connect to internet to get fresh results'
        });
        return;
      }
    }
    
    try {
      const res = await fetch(`${API_BASE}/answers/verify`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({
          question: question,
          intent: "clause_lookup",
          mode: "audit"
        })
      });
      
      const data = await res.json();
      setResponse(data);
      
      // Cache successful responses
      if (data && data.verdict !== 'ERROR') {
        cacheAnswer(question, data);
      }
      
      // Track GA4 event
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'answer_verify', {
          verdict: data?.verdict || 'N/A',
          has_citations: !!(data?.citations?.length),
          is_cached: false,
        });
      }
    } catch (err) {
      console.error('API Error:', err);
      
      // Try cached response as fallback
      const cachedAnswer = getCachedAnswer(question);
      if (cachedAnswer) {
        setResponse({
          answer: cachedAnswer.answer,
          verdict: 'CACHED',
          citations: cachedAnswer.citations,
          notes: ['Network error - showing cached response']
        });
        toast.warning('Network error - showing cached response');
      } else {
        setResponse({ 
          verdict: "ERROR", 
          notes: ["network_error", "No cached data available"] 
        });
        toast.error('Network error and no cached data available');
      }
    } finally {
      setLoading(false);
    }
  };

  const recentQuestions = getRecentQuestions(5);

  return (
    <section className="bg-white" id="ask-clausebot">
      <div className="max-w-6xl mx-auto px-6 py-14">
        <div className="flex items-center gap-3 mb-2">
          <h2 className="text-xl md:text-2xl font-semibold">Ask ClauseBot</h2>
          {!isOnline && (
            <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
              Offline Mode
            </span>
          )}
          {hasOfflineData && (
            <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
              Cached Data Available
            </span>
          )}
        </div>
        <p className="text-gray-600 mt-1">
          Get clause-cited, audit-ready answers. {!isOnline ? 'Working with cached data while offline.' : 'Live API connection active.'}
        </p>

        <form onSubmit={handleSubmit} className="mt-6 flex gap-3">
          <input
            className="flex-1 border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#0D47A1] focus:border-transparent"
            placeholder="e.g., What is the undercut limit in AWS D1.1:2025 Clause 8?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={loading}
          />
          <button 
            type="submit"
            className="px-5 py-3 rounded-lg bg-[#0D47A1] text-white hover:bg-[#0A3A85] disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            disabled={loading || !question.trim()}
          >
            {loading ? "Checking…" : isOnline ? "Verify" : "Search Cache"}
          </button>
        </form>

        {/* Recent Questions for Offline Use */}
        {recentQuestions.length > 0 && (
          <div className="mt-4">
            <p className="text-sm text-gray-500 mb-2">Recent questions {!isOnline ? '(available offline)' : ''}:</p>
            <div className="flex flex-wrap gap-2">
              {recentQuestions.map((q) => (
                <button
                  key={q.id}
                  onClick={() => setQuestion(q.question)}
                  className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
                  disabled={loading}
                >
                  {q.question.length > 50 ? `${q.question.substring(0, 50)}...` : q.question}
                </button>
              ))}
            </div>
          </div>
        )}

        {response && (
          <div className="mt-6 rounded-lg border bg-gray-50 p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-500">Verdict</div>
              {response.verdict === 'CACHED' && (
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                  Cached Response
                </span>
              )}
            </div>
            <div className={`text-lg font-semibold ${
              response.verdict === 'VERIFIED' ? 'text-green-600' :
              response.verdict === 'CACHED' ? 'text-blue-600' :
              response.verdict === 'INSUFFICIENT_EVIDENCE' ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {response.verdict || "—"}
            </div>

            {response.answer && (
              <div className="mt-3">
                <div className="text-sm text-gray-500">Answer</div>
                <div className="text-gray-700">{response.answer}</div>
              </div>
            )}

            {response.citations && response.citations.length > 0 && (
              <div className="mt-3">
                <div className="text-sm text-gray-500">Citations</div>
                <ul className="list-disc ml-5 text-gray-700">
                  {response.citations.map((citation, i) => (
                    <li key={i}>
                      {typeof citation === "string" 
                        ? citation 
                        : `${citation.standard} — ${citation.clause}`
                      }
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {response.notes && response.notes.length > 0 && (
              <div className="mt-3 text-sm text-gray-600">
                Notes: {response.notes.join(", ")}
              </div>
            )}

            {response.confidence !== undefined && (
              <div className="mt-3 text-sm text-gray-600">
                Confidence: {Math.round(response.confidence * 100)}%
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
};

export default AskClauseBot;