class WebSocketService {
  constructor() {
    this.socket = null;
    this.messageListeners = new Set();
    this.statusListeners = new Set();
    this.status = 'DISCONNECTED';

    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.baseDelayMs = 1000;
    this.maxDelayMs = 30000;
    this.reconnectTimeoutId = null;
    this.pingIntervalId = null;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || 'localhost:8000';
    // Fallback to backend port 8000 if running on Vite dev server (port 5173 / 3000)
    const wsHost = host.includes(':5173') || host.includes(':3000') ? 'localhost:8000' : host;
    this.url = `${protocol}//${wsHost}/ws/market-data`;
  }

  connect() {
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

      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.notifyListeners(message);
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', err);
        }
      };

      this.socket.onerror = (event) => {
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

  disconnect() {
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

  manualReconnect() {
    this.disconnect();
    this.reconnectAttempts = 0;
    this.connect();
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.warn('[WebSocket] Cannot send message, socket is not open');
    }
  }

  subscribe(handler) {
    this.messageListeners.add(handler);
    return () => {
      this.messageListeners.delete(handler);
    };
  }

  onStatusChange(handler) {
    this.statusListeners.add(handler);
    handler(this.status);
    return () => {
      this.statusListeners.delete(handler);
    };
  }

  getStatus() {
    return this.status;
  }

  setStatus(status, error) {
    this.status = status;
    this.statusListeners.forEach((listener) => listener(status, error));
  }

  notifyListeners(message) {
    this.messageListeners.forEach((listener) => listener(message));
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.setStatus('ERROR', 'Max reconnection attempts reached. Click retry.');
      return;
    }

    this.setStatus('RECONNECTING');
    const delay = Math.min(
      this.baseDelayMs * Math.pow(1.5, this.reconnectAttempts),
      this.maxDelayMs
    );
    this.reconnectAttempts += 1;

    this.reconnectTimeoutId = setTimeout(() => {
      this.connect();
    }, delay);
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.pingIntervalId = setInterval(() => {
      this.send({ type: 'PING' });
    }, 25000);
  }

  stopHeartbeat() {
    if (this.pingIntervalId) {
      clearInterval(this.pingIntervalId);
      this.pingIntervalId = null;
    }
  }
}

export const wsService = new WebSocketService();
