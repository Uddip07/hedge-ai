import { LiveTickerItem, WsMessagePayload } from '../types/api';

export type WsConnectionStatus = 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' | 'RECONNECTING' | 'ERROR';

type MessageHandler = (message: WsMessagePayload) => void;
type StatusHandler = (status: WsConnectionStatus, error?: string) => void;

class WebSocketService {
  private socket: WebSocket | null = null;
  private url: string;
  private messageListeners: Set<MessageHandler> = new Set();
  private statusListeners: Set<StatusHandler> = new Set();
  private status: WsConnectionStatus = 'DISCONNECTED';
  
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private baseDelayMs = 1000;
  private maxDelayMs = 30000;
  private reconnectTimeoutId: ReturnType<typeof setTimeout> | null = null;
  private pingIntervalId: ReturnType<typeof setInterval> | null = null;

  constructor() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || 'localhost:8000';
    // Fallback to backend port 8000 if running on Vite dev server (port 5173 / 3000)
    const wsHost = host.includes(':5173') || host.includes(':3000') ? 'localhost:8000' : host;
    this.url = `${protocol}//${wsHost}/ws/market-data`;
  }

  public connect(): void {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.setStatus('CONNECTING');

    try {
      this.socket = new WebSocket(this.url);

      this.socket.onopen = () => {
        this.reconnectAttempts = 0;
        this.setStatus('CONNECTED');
        this.startHeartbeat();
      };

      this.socket.onmessage = (event: MessageEvent) => {
        try {
          const message: WsMessagePayload = JSON.parse(event.data);
          this.notifyListeners(message);
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', err);
        }
      };

      this.socket.onerror = (event: Event) => {
        console.warn('[WebSocket] Connection error:', event);
        this.setStatus('ERROR', 'WebSocket connection error');
      };

      this.socket.onclose = () => {
        this.stopHeartbeat();
        this.socket = null;
        if (this.status !== 'DISCONNECTED') {
          this.scheduleReconnect();
        }
      };
    } catch (err) {
      console.error('[WebSocket] Connection failed:', err);
      this.setStatus('ERROR', 'Failed to initialize WebSocket');
      this.scheduleReconnect();
    }
  }

  public disconnect(): void {
    this.setStatus('DISCONNECTED');
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }
    this.stopHeartbeat();

    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  public manualReconnect(): void {
    this.disconnect();
    this.reconnectAttempts = 0;
    this.connect();
  }

  public send(data: unknown): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.warn('[WebSocket] Cannot send message, socket is not open');
    }
  }

  public subscribe(handler: MessageHandler): () => void {
    this.messageListeners.add(handler);
    return () => {
      this.messageListeners.delete(handler);
    };
  }

  public onStatusChange(handler: StatusHandler): () => void {
    this.statusListeners.add(handler);
    handler(this.status);
    return () => {
      this.statusListeners.delete(handler);
    };
  }

  public getStatus(): WsConnectionStatus {
    return this.status;
  }

  private setStatus(status: WsConnectionStatus, error?: string): void {
    this.status = status;
    this.statusListeners.forEach((listener) => listener(status, error));
  }

  private notifyListeners(message: WsMessagePayload): void {
    this.messageListeners.forEach((listener) => listener(message));
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.setStatus('ERROR', 'Max reconnection attempts reached. Please click retry.');
      return;
    }

    this.setStatus('RECONNECTING');
    const delay = Math.min(
      this.baseDelayMs * Math.pow(1.5, this.reconnectAttempts),
      this.maxDelayMs
    );
    this.reconnectAttempts += 1;

    console.log(`[WebSocket] Reconnecting in ${Math.round(delay)}ms (Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.reconnectTimeoutId = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.pingIntervalId = setInterval(() => {
      this.send({ type: 'PING' });
    }, 25000);
  }

  private stopHeartbeat(): void {
    if (this.pingIntervalId) {
      clearInterval(this.pingIntervalId);
      this.pingIntervalId = null;
    }
  }
}

export const wsService = new WebSocketService();
