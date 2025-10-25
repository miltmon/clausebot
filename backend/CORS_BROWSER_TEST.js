// CORS Browser Test - Run this in browser console (F12)
// This tests the REAL CORS behavior that frontend experiences

console.log('🔍 Testing ClauseBot API CORS...');

fetch('https://clausebot-api.onrender.com/v1/quiz?count=2', {
  method: 'GET',
  headers: { 
    'Authorization': 'Bearer cb_admin_2025_secure_key_admin',
    'Content-Type': 'application/json'
  },
  mode: 'cors',
  credentials: 'omit'
})
.then(response => {
  console.log('✅ CORS SUCCESS - Response received');
  console.log('Status:', response.status);
  console.log('Headers:', [...response.headers.entries()]);
  return response.json();
})
.then(data => {
  console.log('✅ DATA SUCCESS:', data);
  console.log('Questions received:', data.questions?.length || 0);
  console.log('Source:', data.source);
})
.catch(error => {
  console.error('❌ CORS ERROR:', error);
  console.error('Error type:', error.name);
  console.error('Error message:', error.message);
  
  if (error.message.includes('CORS')) {
    console.error('🚨 CORS POLICY BLOCKING REQUEST');
    console.error('This means the server CORS headers are not allowing this origin');
  } else if (error.message.includes('Failed to fetch')) {
    console.error('🚨 NETWORK ERROR - Could be CORS or server down');
  }
});

// Also test a simple health check
console.log('🔍 Testing simple health endpoint...');
fetch('https://clausebot-api.onrender.com/health', {
  mode: 'cors'
})
.then(r => r.json())
.then(d => console.log('✅ Health check SUCCESS:', d))
.catch(e => console.error('❌ Health check ERROR:', e));
