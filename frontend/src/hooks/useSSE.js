import { useState, useEffect } from 'react';

export function useSSE(streamUrl, onMessage) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let eventSource = null;

    const connect = () => {
      try {
        eventSource = new EventSource(streamUrl);

        eventSource.onopen = () => {
          setIsConnected(true);
          setError(null);
        };

        // Listen to custom SSE event 'new_article' emitted by FastAPI stream.py
        eventSource.addEventListener('new_article', (event) => {
          try {
            const data = JSON.parse(event.data);
            if (onMessage) {
              onMessage(data);
            }
          } catch (err) {
            console.error('Failed to parse SSE payload:', err);
          }
        });

        eventSource.onerror = (err) => {
          console.warn('SSE EventSource error connection state:', eventSource.readyState);
          setIsConnected(false);
          setError('Disconnected from live stream engine.');
        };
      } catch (err) {
        setError(err.message);
      }
    };

    connect();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [streamUrl, onMessage]);

  return { isConnected, error };
}
