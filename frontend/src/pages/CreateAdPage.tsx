import { useNavigate } from 'react-router-dom';
import Navigation from '../components/Navigation';
import { CreateAdForm } from '@/features/ad/create/CreateAdForm';
import { Meta } from '@/shared/seo/Meta';
import { getCanonicalUrl } from '@/shared/seo/url';

interface CreateAdPageProps {
  onLogout: () => void;
}

export default function CreateAdPage({ onLogout }: CreateAdPageProps) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      <Meta
        title="Новое объявление"
        description="Создать объявление на ClassifiedAds"
        canonical={getCanonicalUrl('/ads/new')}
        noIndex
      />
      <Navigation onLogout={onLogout} />

      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-gray-900 mb-6">Новое объявление</h1>

        <div className="bg-white rounded-lg border border-gray-200 p-8">
          <CreateAdForm onSuccess={(ad) => navigate(`/ads/${ad.id}`)} />
        </div>
      </div>
    </div>
  );
}
