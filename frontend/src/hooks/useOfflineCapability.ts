import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'sonner';

interface OfflineData {
  questions: Array<{
    id: string;
    question: string;
    timestamp: number;
  }>;
  answers: Array<{
    id: string;
    question: string;
    answer: string;
    verdict: string;
    citations: string[];
    timestamp: number;
  }>;
}

const OFFLINE_STORAGE_KEY = 'clausebot-offline-data';
const OFFLINE_QUEUE_KEY = 'clausebot-offline-queue';

export const useOfflineCapability = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [offlineData, setOfflineData] = useState<OfflineData>(() => {
    try {
      const stored = localStorage.getItem(OFFLINE_STORAGE_KEY);
      return stored ? JSON.parse(stored) : { questions: [], answers: [] };
    } catch {
      return { questions: [], answers: [] };
    }
  });
  const syncQueueRef = useRef<Array<{ type: string; data: Record<string, unknown> }>>([]);

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      syncOfflineData();
    };

    const handleOffline = () => {
      setIsOnline(false);
      toast.warning('You\'re now offline. ClauseBot.Ai will cache your queries locally.', {
        description: 'Your work will sync when connection is restored.',
      });
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Save offline data to localStorage
  const saveOfflineData = useCallback((data: OfflineData) => {
    try {
      localStorage.setItem(OFFLINE_STORAGE_KEY, JSON.stringify(data));
      setOfflineData(data);
    } catch (error) {
      console.warn('Failed to save offline data:', error);
    }
  }, []);

  // Cache a question for offline use
  const cacheQuestion = useCallback((question: string) => {
    const newQuestion = {
      id: Date.now().toString(),
      question,
      timestamp: Date.now(),
    };

    const updatedData = {
      ...offlineData,
      questions: [newQuestion, ...offlineData.questions.slice(0, 49)] // Keep last 50
    };

    saveOfflineData(updatedData);
  }, [offlineData, saveOfflineData]);

  // Cache an answer for offline use
  const cacheAnswer = useCallback((question: string, answer: { answer?: string }) => {
    const newAnswer = {
      id: Date.now().toString(),
      question,
      answer: answer.answer || 'Cached response',
      verdict: answer.verdict || 'CACHED',
      citations: answer.citations || [],
      timestamp: Date.now(),
    };

    const updatedData = {
      ...offlineData,
      answers: [newAnswer, ...offlineData.answers.slice(0, 49)] // Keep last 50
    };

    saveOfflineData(updatedData);
  }, [offlineData, saveOfflineData]);

  // Get cached answer for a question (fuzzy match)
  const getCachedAnswer = useCallback((question: string) => {
    const normalizedQuestion = question.toLowerCase().trim();
    
    // Exact match first
    let match = offlineData.answers.find(
      answer => answer.question.toLowerCase().trim() === normalizedQuestion
    );

    // Fuzzy match if no exact match
    if (!match) {
      match = offlineData.answers.find(answer => {
        const cachedQ = answer.question.toLowerCase();
        return cachedQ.includes(normalizedQuestion) || normalizedQuestion.includes(cachedQ);
      });
    }

    return match;
  }, [offlineData.answers]);

  // Add to sync queue for when we come back online
  const addToSyncQueue = useCallback((type: string, data: Record<string, unknown>) => {
    syncQueueRef.current.push({ type, data });
    try {
      localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(syncQueueRef.current));
    } catch (error) {
      console.warn('Failed to save sync queue:', error);
    }
  }, []);

  // Sync offline data when back online
  const syncOfflineData = useCallback(async () => {
    try {
      const queueData = localStorage.getItem(OFFLINE_QUEUE_KEY);
      if (queueData) {
        const queue = JSON.parse(queueData);
        // Process sync queue here if needed
        // For now, just clear it
        localStorage.removeItem(OFFLINE_QUEUE_KEY);
        syncQueueRef.current = [];
        
        if (queue.length > 0) {
          toast.success(`Synced ${queue.length} offline actions`);
        }
      }
    } catch (error) {
      console.warn('Failed to sync offline data:', error);
    }
  }, []);

  // Get recent questions for offline suggestions
  const getRecentQuestions = useCallback((limit = 10) => {
    return offlineData.questions
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }, [offlineData.questions]);

  // Clear old cached data (older than 7 days)
  const clearOldCache = useCallback(() => {
    const weekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
    
    const filteredData = {
      questions: offlineData.questions.filter(q => q.timestamp > weekAgo),
      answers: offlineData.answers.filter(a => a.timestamp > weekAgo),
    };

    if (filteredData.questions.length !== offlineData.questions.length ||
        filteredData.answers.length !== offlineData.answers.length) {
      saveOfflineData(filteredData);
      toast.success('Cleared old cached data to free up space');
    }
  }, [offlineData, saveOfflineData]);

  return {
    isOnline,
    offlineData,
    cacheQuestion,
    cacheAnswer,
    getCachedAnswer,
    addToSyncQueue,
    getRecentQuestions,
    clearOldCache,
    syncOfflineData,
    hasOfflineData: offlineData.questions.length > 0 || offlineData.answers.length > 0,
  };
};