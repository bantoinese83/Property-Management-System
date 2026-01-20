import { useState, useEffect, useCallback, useRef } from 'react';
import client from '../api/client';

interface UseApiOptions {
  skip?: boolean;
  refetchInterval?: number;
  retryOnError?: number;
}

interface UseApiResponse<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;
}

export function useApi<T>(
  url: string,
  options: UseApiOptions = {}
): UseApiResponse<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(!options.skip);
  const [error, setError] = useState<Error | null>(null);
  const [isRefetching, setIsRefetching] = useState(false);
  const retryCount = useRef(0);

  const fetchData = useCallback(async () => {
    if (options.skip) return;

    try {
      setIsRefetching(true);
      setError(null);
      const response = await client.get<T>(url);
      setData(response.data);
      retryCount.current = 0;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error occurred');
      setError(error);

      if (
        options.retryOnError &&
        retryCount.current < options.retryOnError &&
        (err as any).response?.status >= 500
      ) {
        retryCount.current++;
        setTimeout(() => fetchData(), 1000 * Math.pow(2, retryCount.current));
      }
    } finally {
      setIsRefetching(false);
      setLoading(false);
    }
  }, [url, options.skip, options.retryOnError]);

  useEffect(() => {
    if (!options.skip) {
      fetchData();
    }
  }, [url, options.skip, fetchData]);

  useEffect(() => {
    if (options.refetchInterval) {
      const interval = setInterval(fetchData, options.refetchInterval);
      return () => clearInterval(interval);
    }
  }, [options.refetchInterval, fetchData]);

  return { data, loading, error, refetch: fetchData, isRefetching };
}