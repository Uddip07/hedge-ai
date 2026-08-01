import { useEffect, useState, useCallback } from 'react';
import { LiveTickerItem, WsMessagePayload } from '../types/api';
import { wsService, WsConnectionStatus } from '../services/websocketService';

export interface UseWebSocketReturn {
  tickers: Record<string, LiveTickerItem>;
  tickerList: LiveTickerItem[];
  status: WsConnectionStatus;
  errorMessage: string | null;
  lastUpdatedTicker: string | null;
  reconnect: () => void;
  isLoading: boolean;
}

export function useWebSocket(): UseWebSocketReturn {
  const [tickers, setTickers] = useState<Record<string, LiveTickerItem>>({});
  const [status, setStatus] = useState<WsConnectionStatus>('CONNECTING');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastUpdatedTicker, setLastUpdatedTicker] = useState<string | null>(null);

  useEffect(() => {
    wsService.connect();

    const unsubscribeStatus = wsService.onStatusChange((newStatus, error) => {
      setStatus(newStatus);
      if (error) {
        setErrorMessage(error);
      } else if (newStatus === 'CONNECTED') {
        setErrorMessage(null);
      }
    });

    const unsubscribeMessages = wsService.subscribe((message: WsMessagePayload) => {
      if (message.type === 'SNAPSHOT' && Array.isArray(message.data)) {
        const initialMap: Record<string, LiveTickerItem> = {};
        message.data.forEach((item) => {
          initialMap[item.ticker] = item;
        });
        setTickers(initialMap);
      } else if (message.type === 'TICK' && message.data && !Array.isArray(message.data)) {
        const item = message.data;
        setTickers((prev) => ({
          ...prev,
          [item.ticker]: {
            ...prev[item.ticker],
            ...item,
          },
        }));
        setLastUpdatedTicker(item.ticker);
      }
    });

    return () => {
      unsubscribeStatus();
      unsubscribeMessages();
    };
  }, []);

  const reconnect = useCallback(() => {
    setErrorMessage(null);
    wsService.manualReconnect();
  }, []);

  const tickerList = Object.values(tickers);
  const isLoading = status === 'CONNECTING' && tickerList.length === 0;

  return {
    tickers,
    tickerList,
    status,
    errorMessage,
    lastUpdatedTicker,
    reconnect,
    isLoading,
  };
}
