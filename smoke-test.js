// smoke-test.js (Node 18+)
import fetch from 'node-fetch';

const API = process.env.API || 'https://clausebot-api.onrender.com';

async function run() {
  const endpoints = [
    '/v1/health/welding-resources',
    '/v1/welding-symbols?limit=5',
    '/v1/cwi-resources?limit=5',
    '/v1/welding-resources/search?q=fillet'
  ];

  console.log(`🧪 Testing API endpoints at ${API}`);
  console.log('=' .repeat(50));

  for (const ep of endpoints) {
    try {
      const res = await fetch(API + ep, { timeout: 10000 });
      const json = await res.json();
      const itemCount = json.articles ? json.articles.length : Object.keys(json).length;
      
      console.log(`✅ ${ep} -> status ${res.status}, items: ${itemCount}`);
      
      if (res.status !== 200) {
        console.log(`   Response: ${JSON.stringify(json, null, 2)}`);
      }
    } catch (e) {
      console.error(`❌ ${ep} -> ERROR: ${e.message}`);
    }
  }
  
  console.log('=' .repeat(50));
  console.log('🎯 Smoke test complete');
}

run().catch(console.error);
