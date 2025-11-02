import { Suspense } from 'react';

// Server component that can safely use server-only features
export default async function ServerOnlyContent() {
  // Optional: Server-side health check
  let healthStatus = null;
  try {
    const healthResponse = await fetch(`${process.env.VITE_API_URL || 'https://clausebot-api.onrender.com'}/v1/health`, {
      cache: 'no-store' // Always fresh for health checks
    });
    
    if (healthResponse.ok) {
      healthStatus = await healthResponse.json();
    }
  } catch (error) {
    console.error('Health check failed:', error);
  }

  return (
    <>
      {/* Optional: Show health status */}
      {healthStatus && (
        <div className="mb-4 p-2 bg-green-50 border border-green-200 rounded">
          <span className="text-green-800 text-sm">
            ✅ API Status: {healthStatus.status || 'healthy'}
          </span>
        </div>
      )}
      
      <Suspense fallback={<div className="animate-pulse bg-gray-200 h-32 rounded mb-4">Loading ClauseBot...</div>}>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">ClauseBot Assistant</h2>
          <p className="text-gray-600">ClauseBot widget will load here...</p>
        </div>
      </Suspense>
      
      <Suspense fallback={<div className="animate-pulse bg-gray-200 h-32 rounded">Loading Quiz...</div>}>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Welding Quiz</h2>
          <p className="text-gray-600">Quiz component will load here...</p>
        </div>
      </Suspense>
    </>
  );
}
