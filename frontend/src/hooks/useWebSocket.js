import { useState, useEffect, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { wsService } from '../services/websocketService';

export function useWebSocket() {
  const queryClient = useQueryClient();
  const [tickerMap, setTickerMap] = useState({});
  const [status, setStatus] = useState(wsService.getStatus());
  const [errorMessage, setErrorMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    wsService.connect();

    const unsubscribeStatus = wsService.onStatusChange((newStatus, error) => {
      setStatus(newStatus);
      if (error) setErrorMessage(error);
      if (newStatus === 'CONNECTED') {
        setErrorMessage(null);
      }
    });

    const updateQueryCache = (item) => {
      if (!item || !item.ticker) return;
      const baseSym = item.symbol || item.ticker.split('.')[0];
      const payload = { data: item, latencyMs: 0 };
      queryClient.setQueryData(['marketQuote', item.ticker], payload);
      if (baseSym && baseSym !== item.ticker) {
        queryClient.setQueryData(['marketQuote', baseSym], payload);
      }
    };

    const unsubscribeMessages = wsService.subscribe((message) => {
      if (message.type === 'SNAPSHOT' && Array.isArray(message.data)) {
        const nextMap = {};
        message.data.forEach((item) => {
          nextMap[item.ticker] = item;
          updateQueryCache(item);
        });
        setTickerMap(nextMap);
        setIsLoading(false);
      } else if (message.type === 'TICK' && message.data) {
        const item = message.data;
        setTickerMap((prev) => ({
          ...prev,
          [item.ticker]: item,
        }));
        updateQueryCache(item);
        setIsLoading(false);
      }
    });

    return () => {
      unsubscribeStatus();
      unsubscribeMessages();
    };
  }, [queryClient]);

  const reconnect = useCallback(() => {
    wsService.manualReconnect();
  }, []);

  const tickerList = Object.values(tickerMap);

  return {
    tickerMap,
    tickerList,
    status,
    errorMessage,
    isLoading: isLoading && tickerList.length === 0,
    reconnect,
  };
}
