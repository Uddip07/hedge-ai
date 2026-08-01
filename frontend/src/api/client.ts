import { useSettingsStore } from '../store/useSettingsStore';

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ data: T; latencyMs: number; status: number }> {
  const { backendUrl, addApiLog } = useSettingsStore.getState();
  const startTime = performance.now();

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${backendUrl}${cleanEndpoint}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(options.headers as Record<string, string>),
  };

  const method = (options.method || 'GET').toUpperCase() as 'GET' | 'POST' | 'PUT' | 'DELETE';

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const endTime = performance.now();
    const latencyMs = Math.round(endTime - startTime);

    const responseText = await response.text();
    const responseSizeBytes = new Blob([responseText]).size;

    let data: T;
    try {
      data = JSON.parse(responseText);
    } catch {
      data = responseText as unknown as T;
    }

    addApiLog({
      method,
      endpoint: cleanEndpoint,
      status: response.status,
      latencyMs,
      responseSizeBytes,
      timestamp: new Date().toISOString(),
      requestBody: options.body ? JSON.parse(options.body as string) : undefined,
      responseBody: data,
    });

    if (!response.ok) {
      const errorMsg =
        (data as any)?.error?.message ||
        (data as any)?.detail ||
        `HTTP ${response.status}: ${response.statusText}`;
      throw new Error(errorMsg);
    }

    return { data, latencyMs, status: response.status };
  } catch (error: any) {
    const endTime = performance.now();
    const latencyMs = Math.round(endTime - startTime);

    addApiLog({
      method,
      endpoint: cleanEndpoint,
      status: 'ERR',
      latencyMs,
      responseSizeBytes: 0,
      timestamp: new Date().toISOString(),
      requestBody: options.body ? JSON.parse(options.body as string) : undefined,
      error: error.message || 'Network error',
    });

    throw error;
  }
}
