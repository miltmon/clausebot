# ClauseBot WebSocket Implementation Guide

**Document Version:** 1.0.0  
**Status:** Future Feature - Implementation Ready  
**Last Updated:** October 26, 2025

---

## 🎯 Overview

This guide provides a **battle-tested blueprint** for adding real-time WebSocket features to ClauseBot when needed. The current Vercel configuration is **WebSocket-ready** with proper cache headers and CSP policies already in place.

---

## 🚀 Use Cases for WebSocket Integration

### Potential Real-Time Features
1. **Live Quiz Leaderboard** - Real-time score updates during quizzes
2. **Collaborative Learning** - Multiple users studying the same clause together
3. **System Health Streaming** - Live backend metrics (CPU, memory, API latency)
4. **Admin Notifications** - Real-time alerts for compliance issues
5. **Cursor-Based Pagination** - Stream large result sets incrementally

---

## 📋 Prerequisites

### Vercel Configuration (✅ Already Complete)
- [x] CSP includes `wss://clausebot-api.onrender.com`
- [x] `/ws/*` and `/stream/*` routes have `no-cache` headers
- [x] `X-Accel-Buffering: no` set for streaming endpoints
- [x] Function timeout set to 300s (sufficient for long-lived connections)

### Backend Requirements (🔮 Future Implementation)
- [ ] FastAPI WebSocket endpoint (e.g., `/ws/quiz-realtime`)
- [ ] WebSocket connection manager
- [ ] Authentication via JWT or session token
- [ ] Heartbeat/ping-pong mechanism (30s interval)
- [ ] Graceful disconnect handling

---

## 🛠️ Backend Implementation (FastAPI)

### Step 1: Add WebSocket Dependencies
```bash
# backend/requirements.txt
fastapi[all]>=0.104.0
websockets>=12.0
```

### Step 2: Create WebSocket Endpoint
```python
# backend/api/routers/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
    
    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass  # Client disconnected

manager = ConnectionManager()

@router.websocket("/ws/quiz-realtime/{room_id}")
async def quiz_realtime(websocket: WebSocket, room_id: str):
    """
    Real-time quiz leaderboard WebSocket endpoint
    
    Message Format:
    {
        "type": "score_update",
        "user_id": "user123",
        "score": 850,
        "rank": 3,
        "timestamp": "2025-10-26T10:00:00Z"
    }
    """
    await manager.connect(websocket, room_id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "room_id": room_id,
            "message": "Connected to quiz leaderboard"
        })
        
        # Heartbeat task
        async def heartbeat():
            while True:
                try:
                    await websocket.send_json({"type": "ping"})
                    await asyncio.sleep(30)
                except:
                    break
        
        heartbeat_task = asyncio.create_task(heartbeat())
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "pong":
                continue  # Heartbeat response
            
            elif message.get("type") == "score_update":
                # Broadcast score update to all clients in room
                await manager.broadcast(message, room_id)
            
            elif message.get("type") == "join":
                # User joined the quiz
                await manager.broadcast({
                    "type": "user_joined",
                    "user_id": message.get("user_id"),
                    "timestamp": message.get("timestamp")
                }, room_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast({
            "type": "user_left",
            "room_id": room_id
        }, room_id)
    
    finally:
        heartbeat_task.cancel()
        manager.disconnect(websocket, room_id)
```

### Step 3: Register WebSocket Router
```python
# backend/api/main.py
from .routers.websocket import router as websocket_router

app.include_router(websocket_router, tags=["websocket"])
```

---

## 💻 Frontend Implementation (React/TypeScript)

### Step 1: Create WebSocket Hook
```typescript
// frontend/src/hooks/useWebSocket.ts
import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export const useWebSocket = ({
  url,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
}: UseWebSocketOptions) => {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectCount, setReconnectCount] = useState(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setReconnectCount(0);
        onConnect?.();
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle heartbeat
          if (data.type === 'ping') {
            ws.current?.send(JSON.stringify({ type: 'pong' }));
            return;
          }
          
          onMessage?.(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        onDisconnect?.();

        // Attempt reconnection
        if (reconnectCount < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Reconnecting... (attempt ${reconnectCount + 1})`);
            setReconnectCount((prev) => prev + 1);
            connect();
          }, reconnectInterval * Math.pow(2, reconnectCount)); // Exponential backoff
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }, [url, onMessage, onConnect, onDisconnect, onError, reconnectCount, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    ws.current?.close();
    ws.current = null;
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((data: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [url]);

  return {
    isConnected,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
};
```

### Step 2: Use WebSocket in Component
```typescript
// frontend/src/components/QuizLeaderboard.tsx
import { useWebSocket } from '../hooks/useWebSocket';
import { useState } from 'react';

interface ScoreUpdate {
  type: 'score_update';
  user_id: string;
  score: number;
  rank: number;
  timestamp: string;
}

export const QuizLeaderboard = ({ roomId }: { roomId: string }) => {
  const [scores, setScores] = useState<ScoreUpdate[]>([]);
  
  const { isConnected, sendMessage } = useWebSocket({
    url: `wss://clausebot-api.onrender.com/ws/quiz-realtime/${roomId}`,
    onMessage: (data) => {
      if (data.type === 'score_update') {
        setScores((prev) => {
          const updated = [...prev];
          const index = updated.findIndex((s) => s.user_id === data.user_id);
          if (index >= 0) {
            updated[index] = data;
          } else {
            updated.push(data);
          }
          return updated.sort((a, b) => b.score - a.score);
        });
      }
    },
    onConnect: () => {
      console.log('Connected to quiz leaderboard');
    },
    onDisconnect: () => {
      console.log('Disconnected from quiz leaderboard');
    },
  });

  return (
    <div>
      <h2>Live Leaderboard {isConnected ? '🟢' : '🔴'}</h2>
      <ul>
        {scores.map((score, index) => (
          <li key={score.user_id}>
            #{index + 1} - {score.user_id}: {score.score} points
          </li>
        ))}
      </ul>
    </div>
  );
};
```

---

## 🔒 Security Considerations

### 1. Authentication
```python
# backend/api/routers/websocket.py
from fastapi import WebSocket, Query, HTTPException

@router.websocket("/ws/quiz-realtime/{room_id}")
async def quiz_realtime(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(...)  # JWT token in query param
):
    # Verify JWT token before accepting connection
    try:
        user = verify_jwt_token(token)
    except:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    await manager.connect(websocket, room_id, user)
```

### 2. Rate Limiting
```python
# backend/api/routers/websocket.py
from collections import defaultdict
import time

rate_limit_tracker = defaultdict(list)

async def check_rate_limit(user_id: str, max_messages: int = 10, window: int = 60):
    """Allow max_messages per window (seconds)"""
    now = time.time()
    rate_limit_tracker[user_id] = [
        t for t in rate_limit_tracker[user_id] if now - t < window
    ]
    
    if len(rate_limit_tracker[user_id]) >= max_messages:
        return False
    
    rate_limit_tracker[user_id].append(now)
    return True
```

### 3. Message Validation
```python
from pydantic import BaseModel, ValidationError

class ScoreUpdateMessage(BaseModel):
    type: str
    user_id: str
    score: int
    timestamp: str

# In WebSocket handler
try:
    validated_message = ScoreUpdateMessage(**message)
except ValidationError:
    await websocket.send_json({"type": "error", "message": "Invalid message format"})
    continue
```

---

## 📊 Monitoring & Observability

### 1. WebSocket Metrics
```python
# backend/api/routers/websocket.py
from prometheus_client import Counter, Gauge

ws_connections = Gauge('websocket_connections', 'Active WebSocket connections')
ws_messages_sent = Counter('websocket_messages_sent', 'Messages sent via WebSocket')
ws_messages_received = Counter('websocket_messages_received', 'Messages received via WebSocket')

@router.websocket("/ws/quiz-realtime/{room_id}")
async def quiz_realtime(websocket: WebSocket, room_id: str):
    ws_connections.inc()
    try:
        # ... connection logic ...
        pass
    finally:
        ws_connections.dec()
```

### 2. Frontend Tracking (GA4)
```typescript
// Track WebSocket events
gtag('event', 'websocket_connect', {
  room_id: roomId,
  timestamp: new Date().toISOString(),
});

gtag('event', 'websocket_disconnect', {
  room_id: roomId,
  duration_seconds: connectionDuration,
  reconnect_attempts: reconnectCount,
});
```

---

## 🚨 Troubleshooting

### Issue: WebSocket Connection Fails
**Symptoms:** Client shows "🔴 Disconnected"  
**Checks:**
1. ✅ Verify CSP includes `wss://clausebot-api.onrender.com`
2. ✅ Check backend WebSocket endpoint is running
3. ✅ Test with `wscat`: `wscat -c wss://clausebot-api.onrender.com/ws/quiz-realtime/test`
4. ✅ Check Render logs for errors

### Issue: High Reconnection Rate
**Symptoms:** Frequent disconnect/reconnect cycles  
**Checks:**
1. ✅ Verify heartbeat mechanism (30s ping/pong)
2. ✅ Check Render free tier cold start delays
3. ✅ Implement exponential backoff (already in `useWebSocket` hook)

### Issue: Messages Not Received
**Symptoms:** Frontend doesn't update with new data  
**Checks:**
1. ✅ Verify `onMessage` callback is registered
2. ✅ Check browser console for parsing errors
3. ✅ Use browser DevTools > Network > WS tab to inspect messages

---

## 📋 Deployment Checklist

### Before Going Live
- [ ] Backend WebSocket endpoint deployed and tested
- [ ] Frontend WebSocket hook tested with reconnection
- [ ] CSP verified to include `wss://` origin
- [ ] Cache headers verified (`no-store` for `/ws/*`)
- [ ] Authentication/authorization tested
- [ ] Rate limiting implemented and tested
- [ ] Heartbeat/ping-pong mechanism working
- [ ] Error handling and graceful disconnect tested
- [ ] Load testing completed (concurrent connections)
- [ ] Monitoring/metrics dashboard configured
- [ ] GA4 events firing correctly
- [ ] Documentation updated in this guide

---

## 📞 Support

**WebSocket Feature Owner:** mjewell@miltmon.com  
**Implementation Questions:** File issue in GitHub  
**Vercel WebSocket Docs:** https://vercel.com/docs/functions/streaming

---

**Status:** This guide is ready for implementation when real-time features are needed. All infrastructure prerequisites are in place.

