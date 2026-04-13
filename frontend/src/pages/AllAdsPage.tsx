import Navigation from '../components/Navigation';
import AdCard from '../components/AdCard';
import { mockAds } from '../data/mockData';

interface AllAdsPageProps {
  onLogout: () => void;
}

export default function AllAdsPage({ onLogout }: AllAdsPageProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation onLogout={onLogout} />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-gray-900 mb-8">All Ads</h1>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {mockAds.map((ad) => (
            <AdCard
              key={ad.id}
              id={ad.id}
              title={ad.title}
              price={ad.price}
              image={ad.image}
            />
          ))}
        </div>
      </div>
    </div>
  );
}