import { wsService } from '../services/websocketService';

export function runWebSocketTests(): void {
  wsService.disconnect();

  // Test 1: Initial status
  const initialStatus = wsService.getStatus();
  if (initialStatus !== 'DISCONNECTED') {
    throw new Error(`Expected DISCONNECTED, got ${initialStatus}`);
  }

  // Test 2: Status listener registration
  let currentStatus = '';
  const unsubscribe = wsService.onStatusChange((status) => {
    currentStatus = status;
  });

  if (currentStatus !== 'DISCONNECTED') {
    throw new Error(`Expected listener to receive DISCONNECTED, got ${currentStatus}`);
  }

  unsubscribe();
  console.log('[Test Passed] WebSocket Service Unit Tests');
}
