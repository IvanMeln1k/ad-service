import { apiPost } from '@/shared/api/client';
import type { AuthResponse, RegisterPayload, LoginPayload, LogoutPayload } from './model';

export function registerUser(payload: RegisterPayload) {
  return apiPost<AuthResponse>('/register', payload);
}

export function loginUser(payload: LoginPayload) {
  return apiPost<AuthResponse>('/login', payload);
}

export function logoutUser(payload: LogoutPayload) {
  return apiPost<{ status: string }>('/logout', payload);
}
