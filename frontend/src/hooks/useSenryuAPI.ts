import { useState, useCallback } from 'react';
import type { DetectRequest, DetectResponse, ErrorResponse } from '../types/api';

const API_BASE_URL = __API_BASE_URL__;

interface UseSenryuAPIResult {
  detect: (text: string, onlyValid?: boolean) => Promise<DetectResponse>;
  loading: boolean;
  error: string | null;
  clearError: () => void;
}

export const useSenryuAPI = (): UseSenryuAPIResult => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const detect = useCallback(async (text: string, onlyValid = false): Promise<DetectResponse> => {
    setLoading(true);
    setError(null);

    try {
      const request: DetectRequest = {
        text,
        only_valid: onlyValid,
      };

      const response = await fetch(`${API_BASE_URL}/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData: ErrorResponse = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result: DetectResponse = await response.json();
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '不明なエラーが発生しました';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    detect,
    loading,
    error,
    clearError,
  };
};
