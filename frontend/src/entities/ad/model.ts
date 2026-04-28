export interface AdPhoto {
  id: string;
  s3_key: string;
  position: number;
}

export interface Author {
  user_id: string;
  name: string;
  email?: string;
  city?: string;
  avatar_url?: string;
}

export interface Ad {
  id: string;
  user_id: string;
  title: string;
  description: string;
  status: string;
  price?: number;
  city?: string;
  category?: string;
  is_banned: boolean;
  ban_reason?: string;
  photos: AdPhoto[];
  author?: Author;
  created_at: string;
  updated_at: string;
}

export interface CreateAdPayload {
  title: string;
  description: string;
  price?: number;
  city?: string;
  category?: string;
}

export interface UpdateAdPayload {
  title?: string;
  description?: string;
  price?: number;
  city?: string;
  category?: string;
}

export interface PresignResponse {
  upload_url: string;
  s3_key: string;
  max_file_size: number;
}

export interface ListAdsParams {
  search?: string;
  category?: string;
  city?: string;
  price_min?: number;
  price_max?: number;
  sort_by?: 'created_at' | 'price' | 'title';
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

export interface ListAdsResponse {
  items: Ad[];
  total: number;
  limit: number;
  offset: number;
}

export interface CityContext {
  city: string;
  country?: string;
  temperature_c?: number;
  weather_description?: string;
  source: string;
  available: boolean;
  unavailable_reason?: string;
}
