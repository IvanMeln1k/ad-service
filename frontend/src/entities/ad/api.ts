import { adsGet, adsPost, adsPatch, adsDelete } from '@/shared/api/client';
import type {
  Ad,
  CreateAdPayload,
  UpdateAdPayload,
  PresignResponse,
  AdPhoto,
  ListAdsParams,
  ListAdsResponse,
  CityContext,
} from './model';

export function listAds(params?: ListAdsParams) {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.category) query.set('category', params.category);
  if (params?.city) query.set('city', params.city);
  if (params?.price_min !== undefined) query.set('price_min', String(params.price_min));
  if (params?.price_max !== undefined) query.set('price_max', String(params.price_max));
  if (params?.sort_by) query.set('sort_by', params.sort_by);
  if (params?.sort_order) query.set('sort_order', params.sort_order);
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  const qs = query.toString();
  return adsGet<ListAdsResponse>(`/ads${qs ? `?${qs}` : ''}`);
}

export function getAd(adId: string) {
  return adsGet<Ad>(`/ads/${adId}`);
}

export function listMyAds(params?: { limit?: number; offset?: number }) {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  const qs = query.toString();
  return adsGet<Ad[]>(`/ads/my${qs ? `?${qs}` : ''}`);
}

export function createAd(payload: CreateAdPayload) {
  return adsPost<Ad>('/ads', payload);
}

export function updateAd(adId: string, payload: UpdateAdPayload) {
  return adsPatch<Ad>(`/ads/${adId}`, payload);
}

export function deleteAd(adId: string) {
  return adsDelete(`/ads/${adId}`);
}

export function closeAd(adId: string) {
  return adsPost<{ status: string }>(`/ads/${adId}/close`);
}

export function reopenAd(adId: string) {
  return adsPost<{ status: string }>(`/ads/${adId}/reopen`);
}

export function presignPhoto(adId: string, fileName: string, contentType: string, fileSize: number) {
  return adsPost<PresignResponse>(`/ads/${adId}/photos/presign`, {
    file_name: fileName,
    content_type: contentType,
    file_size: fileSize,
  });
}

export function confirmPhoto(adId: string, s3Key: string, position: number) {
  return adsPost<AdPhoto>(`/ads/${adId}/photos`, { s3_key: s3Key, position });
}

export function deletePhoto(adId: string, photoId: string) {
  return adsDelete(`/ads/${adId}/photos/${photoId}`);
}

export function banAd(adId: string, reason: string) {
  return adsPost<{ id: string }>(`/ads/${adId}/ban`, { reason });
}

export function unbanAd(adId: string, unbanReason: string) {
  return adsPost<{ status: string }>(`/ads/${adId}/unban`, { unban_reason: unbanReason });
}

export function getAttributes(attrs: string[]) {
  return adsGet<Record<string, boolean>>(`/attributes?attrs=${attrs.join(',')}`);
}

export function getCityContext(city: string) {
  const query = new URLSearchParams({ city });
  return adsGet<CityContext>(`/external/city-context?${query.toString()}`);
}
