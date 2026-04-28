import { useState, useEffect } from 'react';
import Navigation from '../components/Navigation';
import AdCard from '../components/AdCard';
import { User, Mail, Package } from 'lucide-react';
import { listMyAds } from '@/entities/ad/api';
import { useAuth } from '@/app/providers/AuthProvider';
import { Meta } from '@/shared/seo/Meta';
import { getCanonicalUrl } from '@/shared/seo/url';
import type { Ad } from '@/entities/ad/model';

interface UserProfilePageProps {
  onLogout: () => void;
}

export default function UserProfilePage({ onLogout }: UserProfilePageProps) {
  const { auth } = useAuth();
  const [myAds, setMyAds] = useState<Ad[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listMyAds()
      .then(setMyAds)
      .catch(() => setMyAds([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Meta
        title="Профиль"
        description="Мой профиль на ClassifiedAds"
        canonical={getCanonicalUrl('/profile')}
        noIndex
      />
      <Navigation onLogout={onLogout} />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg overflow-hidden mb-8 shadow-lg">
          <div className="p-8 text-white">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                <User className="w-10 h-10 text-white" />
              </div>
              <div>
                <h1 className="text-white mb-1">Мой профиль</h1>
                <p className="text-blue-100">Управление аккаунтом и объявлениями</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-2">
                  <User className="w-5 h-5 text-blue-100" />
                  <label className="text-blue-100">ID пользователя</label>
                </div>
                <p className="text-white text-sm">{auth?.user_id || '—'}</p>
              </div>

              <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-2">
                  <Mail className="w-5 h-5 text-blue-100" />
                  <label className="text-blue-100">Авторизация</label>
                </div>
                <p className="text-white text-sm">{auth?.access_token ? 'Активна' : '—'}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6 sm:p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
              <Package className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-gray-900">Мои объявления</h2>
              <p className="text-gray-600">
                {loading ? 'Загрузка...' : `${myAds.length} объявлени${myAds.length === 1 ? 'е' : 'й'}`}
              </p>
            </div>
          </div>

          {loading ? (
            <p className="text-gray-500 text-center py-12">Загрузка...</p>
          ) : myAds.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {myAds.map((ad) => (
                <AdCard key={ad.id} ad={ad} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">У вас пока нет объявлений.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
