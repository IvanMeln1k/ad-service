export interface TokenInfo {
  token: string;
  expires_at: string | null;
}

export interface AuthResponse {
  user_id: string;
  access_token: string;
  refresh_token: TokenInfo;
}

export interface RegisterPayload {
  email: string;
  name: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LogoutPayload {
  user_id: string;
  refresh_token: string;
}
