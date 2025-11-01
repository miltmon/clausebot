// ws-test.js - WebSocket smoke test
import WebSocket from 'ws';

const WS_URL = process.env.WS || 'wss://clausebot-api.onrender.com/ws';

console.log(`🔌 Testing WebSocket connection to ${WS_URL}`);

const ws = new WebSocket(WS_URL);

ws.on('open', () => {
  console.log('✅ WebSocket connected');
  
  // Subscribe to wps_published events
  ws.send(JSON.stringify({ type: 'subscribe', channel: 'wps_published' }));
  console.log('📡 Subscribed to wps_published channel');
  
  // Send a test clause query
  setTimeout(() => {
    ws.send(JSON.stringify({ 
      type: 'clause_query', 
      trace_id: 'test_' + Date.now(), 
      user_id: 'demo_user', 
      payload: { q: '3G vertical welding position' } 
    }));
    console.log('🔍 Sent test clause query');
  }, 1000);
  
  // Close after 10 seconds
  setTimeout(() => {
    console.log('⏰ Test complete, closing connection');
    ws.close();
  }, 10000);
});

ws.on('message', (data) => { 
  const msg = JSON.parse(data.toString());
  console.log('📨 Received:', msg.type || 'unknown', msg.channel ? `(${msg.channel})` : '');
  if (msg.type === 'ai_stream_chunk' || msg.type === 'wps_published') {
    console.log('   ✅ Expected event type received');
  }
});

ws.on('error', (err) => { 
  console.error('❌ WebSocket error:', err.message); 
});

ws.on('close', (code, reason) => {
  console.log(`🔌 Connection closed: ${code} ${reason}`);
  process.exit(0);
});
