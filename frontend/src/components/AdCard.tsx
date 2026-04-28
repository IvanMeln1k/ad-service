import { Link } from 'react-router-dom';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { getPhotoUrl } from '@/shared/lib/s3';
import type { Ad } from '@/entities/ad/model';

interface AdCardProps {
  ad: Ad;
}

export default function AdCard({ ad }: AdCardProps) {
  const firstPhoto = ad.photos[0];
  const imageUrl = firstPhoto ? getPhotoUrl(firstPhoto.s3_key) : '';

  return (
    <Link to={`/ads/${ad.id}`} className="group">
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
        <div className="aspect-video w-full overflow-hidden bg-gray-100">
          <ImageWithFallback
            src={imageUrl}
            alt={ad.title}
            loading="lazy"
            decoding="async"
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        <div className="p-4">
          <h3 className="text-gray-900 mb-1 line-clamp-1">{ad.title}</h3>
          <p className="text-gray-500 text-sm line-clamp-1">{ad.description}</p>
          {(ad.price !== undefined || ad.city) && (
            <p className="text-sm text-gray-700 mt-2">
              {ad.price !== undefined ? `${ad.price} ₽` : 'Без цены'}{ad.city ? ` • ${ad.city}` : ''}
            </p>
          )}
          {ad.status !== 'ACTIVE' && (
            <span className="inline-block mt-2 text-xs px-2 py-1 rounded bg-gray-100 text-gray-600">
              {ad.status === 'CLOSED' ? 'Закрыто' : ad.status}
            </span>
          )}
          {ad.is_banned && (
            <span className="inline-block mt-2 text-xs px-2 py-1 rounded bg-red-100 text-red-600">
              Заблокировано
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
