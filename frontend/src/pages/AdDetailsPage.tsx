import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navigation from '../components/Navigation';
import { ImageWithFallback } from '../components/figma/ImageWithFallback';
import { User, Mail, MapPin, X, RotateCcw, Trash2, ShieldBan, ShieldCheck } from 'lucide-react';
import { getAd, closeAd, reopenAd, deleteAd, banAd, unbanAd, getCityContext } from '@/entities/ad/api';
import { useAttributes } from '@/shared/hooks/useAttributes';
import { getPhotoUrl } from '@/shared/lib/s3';
import { useAuth } from '@/app/providers/AuthProvider';
import { Meta } from '@/shared/seo/Meta';
import { getCanonicalUrl } from '@/shared/seo/url';
import type { Ad } from '@/entities/ad/model';
import { getCategoryLabel } from '@/entities/ad/category';

const MODERATE_ATTRS = ['can_moderate'];

function mapCityUnavailableReason(reason?: string): { text: string; status: 'empty' | 'error' } {
  switch (reason) {
    case 'api_key_missing':
      return { text: 'Внешний сервис погоды не настроен (нет API-ключа)', status: 'empty' };
    case 'city_not_found':
      return { text: 'Для этого города внешний сервис не вернул данные', status: 'empty' };
    case 'rate_limited':
    case 'provider_rate_limited':
      return { text: 'Лимит запросов к внешнему сервису исчерпан, попробуйте позже', status: 'error' };
    case 'provider_unreachable':
      return { text: 'Внешний сервис временно недоступен', status: 'error' };
    default:
      return { text: 'Не удалось получить данные внешнего сервиса', status: 'error' };
  }
}

interface AdDetailsPageProps {
  onLogout: () => void;
}

export default function AdDetailsPage({ onLogout }: AdDetailsPageProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { auth } = useAuth();
  const [ad, setAd] = useState<Ad | null>(null);
  const [loading, setLoading] = useState(true);
  const [cityContext, setCityContext] = useState<{
    text: string;
    status: 'loading' | 'ready' | 'empty' | 'error';
  }>({ text: '', status: 'empty' });
  const { can_moderate } = useAttributes(MODERATE_ATTRS);
  const isModerator = !!can_moderate;

  useEffect(() => {
    if (!id) return;
    getAd(id)
      .then(setAd)
      .catch(() => setAd(null))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (!ad?.city) {
      setCityContext({ text: '', status: 'empty' });
      return;
    }
    let cancelled = false;
    setCityContext({ text: '', status: 'loading' });
    getCityContext(ad.city)
      .then((context) => {
        if (cancelled) return;
        if (!context.available) {
          const mapped = mapCityUnavailableReason(context.unavailable_reason);
          setCityContext(mapped);
          return;
        }
        const temp = context.temperature_c !== undefined ? `${Math.round(context.temperature_c)}°C` : null;
        const weather = context.weather_description ?? null;
        const parts = [temp, weather].filter(Boolean).join(' • ');
        if (!parts) {
          setCityContext({ text: 'Внешние данные для этого города пока отсутствуют', status: 'empty' });
          return;
        }
        setCityContext({ text: parts, status: 'ready' });
      })
      .catch(() => {
        if (!cancelled) {
          setCityContext({ text: 'Не удалось загрузить данные внешнего API', status: 'error' });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [ad?.city]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation onLogout={onLogout} />
        <p className="text-gray-500 text-center py-12">Загрузка...</p>
      </div>
    );
  }

  if (!ad) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation onLogout={onLogout} />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <p className="text-gray-600">Объявление не найдено</p>
        </div>
      </div>
    );
  }

  const isOwner = auth?.user_id === ad.user_id;
  const author = ad.author;
  const firstPhoto = ad.photos[0];
  const canonicalUrl = getCanonicalUrl(`/ads/${ad.id}`);
  const adImage = firstPhoto ? getPhotoUrl(firstPhoto.s3_key) : undefined;
  const adJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: ad.title,
    description: ad.description,
    image: adImage ? [adImage] : undefined,
    offers: {
      '@type': 'Offer',
      price: ad.price ?? 0,
      priceCurrency: 'RUB',
      availability: ad.status === 'ACTIVE' ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
      url: canonicalUrl,
    },
  };

  const handleClose = async () => {
    await closeAd(ad.id);
    setAd({ ...ad, status: 'CLOSED' });
  };

  const handleReopen = async () => {
    await reopenAd(ad.id);
    setAd({ ...ad, status: 'ACTIVE' });
  };

  const handleDelete = async () => {
    if (!confirm('Удалить объявление?')) return;
    await deleteAd(ad.id);
    navigate('/ads');
  };

  const handleBan = async () => {
    const reason = prompt('Причина блокировки:');
    if (!reason) return;
    await banAd(ad.id, reason);
    setAd({ ...ad, is_banned: true, ban_reason: reason });
  };

  const handleUnban = async () => {
    const reason = prompt('Причина разблокировки:');
    if (!reason) return;
    await unbanAd(ad.id, reason);
    setAd({ ...ad, is_banned: false, ban_reason: undefined });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Meta
        title={ad.title}
        description={ad.description.slice(0, 160)}
        canonical={canonicalUrl}
        image={adImage}
        type="article"
        jsonLd={adJsonLd}
      />
      <Navigation onLogout={onLogout} />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="aspect-video w-full overflow-hidden bg-gray-100">
                <ImageWithFallback
                  src={firstPhoto ? getPhotoUrl(firstPhoto.s3_key) : ''}
                  alt={ad.title}
                  loading="eager"
                  className="w-full h-full object-cover"
                />
              </div>

              {ad.photos.length > 1 && (
                <div className="flex gap-2 p-4 overflow-x-auto">
                  {ad.photos.map((photo, index) => (
                    <div key={photo.id} className="w-16 h-16 flex-shrink-0 rounded overflow-hidden border border-gray-200">
                      <ImageWithFallback
                        src={getPhotoUrl(photo.s3_key)}
                        alt={`${ad.title} фото ${index + 1}`}
                        loading="lazy"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ))}
                </div>
              )}

              <div className="p-6 sm:p-8">
                <div className="flex justify-between items-start mb-4">
                  <h1 className="text-gray-900">{ad.title}</h1>
                  <div className="flex gap-2">
                    {ad.status !== 'ACTIVE' && (
                      <span className="text-sm px-3 py-1 rounded bg-gray-100 text-gray-600">
                        {ad.status === 'CLOSED' ? 'Закрыто' : ad.status}
                      </span>
                    )}
                    {ad.is_banned && (
                      <span className="text-sm px-3 py-1 rounded bg-red-100 text-red-600">Заблокировано</span>
                    )}
                  </div>
                </div>

                {ad.is_banned && ad.ban_reason && (
                  <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-700">
                      <span className="font-medium">Причина блокировки:</span> {ad.ban_reason}
                    </p>
                  </div>
                )}

                <p className="text-gray-700 leading-relaxed">{ad.description}</p>
                <div className="mt-4 text-gray-700 space-y-1">
                  {ad.price !== undefined && <p><span className="text-gray-500">Цена:</span> {ad.price} ₽</p>}
                  {ad.city && <p><span className="text-gray-500">Город:</span> {ad.city}</p>}
                  {ad.category && <p><span className="text-gray-500">Категория:</span> {getCategoryLabel(ad.category)}</p>}
                </div>

                {isOwner && !ad.is_banned && (
                  <div className="flex gap-3 mt-6 pt-6 border-t border-gray-200">
                    {ad.status === 'ACTIVE' && (
                      <button onClick={handleClose} className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-gray-700">
                        <X className="w-4 h-4" /> Закрыть
                      </button>
                    )}
                    {ad.status === 'CLOSED' && !ad.is_banned && (
                      <button onClick={handleReopen} className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-gray-700">
                        <RotateCcw className="w-4 h-4" /> Открыть снова
                      </button>
                    )}
                    <button onClick={handleDelete} className="flex items-center gap-2 px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                      <Trash2 className="w-4 h-4" /> Удалить
                    </button>
                  </div>
                )}

                {isModerator && !isOwner && (
                  <div className="flex gap-3 mt-6 pt-6 border-t border-gray-200">
                    {!ad.is_banned ? (
                      <button onClick={handleBan} className="flex items-center gap-2 px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                        <ShieldBan className="w-4 h-4" /> Заблокировать
                      </button>
                    ) : (
                      <button onClick={handleUnban} className="flex items-center gap-2 px-4 py-2 border border-green-300 text-green-600 rounded-lg hover:bg-green-50 transition-colors">
                        <ShieldCheck className="w-4 h-4" /> Разблокировать
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-8">
              <h3 className="text-gray-900 mb-4">Автор</h3>

              {author ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      {author.avatar_url ? (
                        <img src={author.avatar_url} alt="" className="w-12 h-12 rounded-full object-cover" />
                      ) : (
                        <User className="w-6 h-6 text-blue-600" />
                      )}
                    </div>
                    <div>
                      <p className="text-gray-900">{author.name}</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {author.email && (
                      <div className="flex items-start gap-3">
                        <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
                        <div>
                          <p className="text-gray-500 mb-1">Email</p>
                          <a href={`mailto:${author.email}`} className="text-blue-600 hover:text-blue-700">
                            {author.email}
                          </a>
                        </div>
                      </div>
                    )}

                    {author.city && (
                      <div className="flex items-start gap-3">
                        <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                        <div>
                          <p className="text-gray-500 mb-1">Город</p>
                          <p className="text-gray-900">{author.city}</p>
                        </div>
                      </div>
                    )}

                    {ad.city && (
                      <div className="flex items-start gap-3">
                        <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                        <div>
                          <p className="text-gray-500 mb-1">Данные по городу</p>
                          {cityContext.status === 'loading' && <p className="text-gray-500">Загрузка...</p>}
                          {cityContext.status === 'ready' && <p className="text-gray-900">{cityContext.text}</p>}
                          {cityContext.status === 'empty' && <p className="text-gray-500">Нет дополнительных данных</p>}
                          {cityContext.status === 'error' && <p className="text-amber-700">{cityContext.text}</p>}
                        </div>
                      </div>
                    )}
                  </div>

                  {author.email && (
                    <a
                      href={`mailto:${author.email}`}
                      className="block w-full text-center bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors mt-4"
                    >
                      Написать автору
                    </a>
                  )}
                </div>
              ) : (
                <p className="text-gray-600">Информация об авторе недоступна</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
