const AUTH_API = '/api/v1';
const ADS_API = '/ads-api/v1';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

function getAuthHeaders(): Record<string, string> {
  const raw = localStorage.getItem('auth');
  if (!raw) return {};
  try {
    const { access_token } = JSON.parse(raw);
    if (access_token) return { Authorization: `Bearer ${access_token}` };
  } catch {}
  return {};
}

async function request<T>(base: string, method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { ...getAuthHeaders() };
  const init: RequestInit = { method, headers };

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    init.body = JSON.stringify(body);
  }

  const response = await fetch(`${base}${path}`, init);

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError(response.status, data.detail || 'Request failed');
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

// Auth API (registrator)
export function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(AUTH_API, 'POST', path, body);
}

// Ads API (adser)
export function adsGet<T>(path: string): Promise<T> {
  return request<T>(ADS_API, 'GET', path);
}

export function adsPost<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(ADS_API, 'POST', path, body);
}

export function adsPatch<T>(path: string, body: unknown): Promise<T> {
  return request<T>(ADS_API, 'PATCH', path, body);
}

export function adsDelete(path: string): Promise<void> {
  return request<void>(ADS_API, 'DELETE', path);
}
