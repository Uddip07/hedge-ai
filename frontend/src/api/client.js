import { useSettingsStore } from '../store/useSettingsStore';

export async function apiClient(endpoint, options = {}) {
  const { backendUrl, addApiLog } = useSettingsStore.getState();
  const startTime = performance.now();

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${backendUrl}${cleanEndpoint}`;

  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    'X-API-Key': import.meta.env.VITE_AUTOMATION_KEY || 'dev-automation-secret-key',
    ...(options.headers || {}),
  };

  const method = (options.method || 'GET').toUpperCase();

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const endTime = performance.now();
    const latencyMs = Math.round(endTime - startTime);

    const responseText = await response.text();
    const responseSizeBytes = new Blob([responseText]).size;

    let data;
    try {
      data = JSON.parse(responseText);
    } catch {
      data = responseText;
    }

    addApiLog({
      method,
      endpoint: cleanEndpoint,
      status: response.status,
      latencyMs,
      responseSizeBytes,
      timestamp: new Date().toISOString(),
      requestBody: options.body ? (typeof options.body === 'string' ? JSON.parse(options.body) : options.body) : undefined,
      responseBody: data,
    });

    if (!response.ok) {
      const errorMsg =
        data?.error?.message ||
        data?.detail ||
        (typeof data === 'string' ? data : `HTTP ${response.status}: ${response.statusText}`);
      throw new Error(errorMsg);
    }

    return { data, latencyMs, status: response.status };
  } catch (error) {
    const endTime = performance.now();
    const latencyMs = Math.round(endTime - startTime);

    addApiLog({
      method,
      endpoint: cleanEndpoint,
      status: 'ERR',
      latencyMs,
      responseSizeBytes: 0,
      timestamp: new Date().toISOString(),
      requestBody: options.body ? (typeof options.body === 'string' ? JSON.parse(options.body) : options.body) : undefined,
      error: error.message || 'Network error',
    });

    throw error;
  }
}
