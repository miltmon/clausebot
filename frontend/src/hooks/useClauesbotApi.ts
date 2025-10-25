import { useState, useCallback } from 'react';
import { clausebotApi, type Question, type Answer, type VerifyAnswerRequest } from '@/services/clausebotApi';
import { toast } from 'sonner';

export const useClausebotApi = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleApiCall = useCallback(async <T>(
    apiCall: () => Promise<T>,
    errorMessage: string = 'An error occurred'
  ): Promise<T | null> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await apiCall();
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : errorMessage;
      setError(message);
      toast.error(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const searchQuestions = useCallback(async (query: string): Promise<Question[] | null> => {
    return handleApiCall(
      () => clausebotApi.searchQuestions(query),
      'Failed to search questions'
    );
  }, [handleApiCall]);

  const verifyAnswer = useCallback(async (request: VerifyAnswerRequest): Promise<Answer | null> => {
    return handleApiCall(
      () => clausebotApi.verifyAnswer(request),
      'Failed to verify answer'
    );
  }, [handleApiCall]);

  const checkHealth = useCallback(async () => {
    return handleApiCall(
      () => clausebotApi.checkHealth(),
      'Failed to check API health'
    );
  }, [handleApiCall]);

  const getEdition = useCallback(async () => {
    return handleApiCall(
      () => clausebotApi.getEdition(),
      'Failed to get API edition'
    );
  }, [handleApiCall]);

  return {
    isLoading,
    error,
    searchQuestions,
    verifyAnswer,
    checkHealth,
    getEdition,
  };
};

export default useClausebotApi;