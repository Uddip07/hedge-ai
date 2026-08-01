import { apiClient } from '../api/client';
import { HealthResponse, RootResponse, VersionResponse } from '../types/api';

export async function fetchHealth(): Promise<{ data: HealthResponse; latencyMs: number }> {
  const { data, latencyMs } = await apiClient<HealthResponse>('/health');
  return { data, latencyMs };
}

export async function fetchRoot(): Promise<{ data: RootResponse; latencyMs: number }> {
  const { data, latencyMs } = await apiClient<RootResponse>('/');
  return { data, latencyMs };
}

export async function fetchVersion(): Promise<{ data: VersionResponse; latencyMs: number }> {
  const { data, latencyMs } = await apiClient<VersionResponse>('/version');
  return { data, latencyMs };
}
