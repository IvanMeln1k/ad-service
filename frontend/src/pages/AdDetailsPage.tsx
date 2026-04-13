import { useParams } from 'react-router-dom';
import Navigation from '../components/Navigation';
import AdCard from '../components/AdCard';
import { mockAds, mockUsers } from '../data/mockData';
import { ImageWithFallback } from '../components/figma/ImageWithFallback';
import { User, Mail, Phone, MapPin } from 'lucide-react';

interface AdDetailsPageProps {
  onLogout: () => void;
}

export default function AdDetailsPage({ onLogout }: AdDetailsPageProps) {
  const { id } = useParams<{ id: string }>();
  const ad = mockAds.find((a) => a.id === id);

  if (!ad) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation onLogout={onLogout} />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-gray-600">Ad not found</p>
        </div>
      </div>
    );
  }

  const seller = mockUsers.find((u) => u.id === ad.userId);
  const similarAds = mockAds.filter(
    (a) => a.category === ad.category && a.id !== ad.id
  ).slice(0, 5);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation onLogout={onLogout} />
      
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Main Ad Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="aspect-video w-full overflow-hidden bg-gray-100">
                <ImageWithFallback
                  src={ad.image}
                  alt={ad.title}
                  className="w-full h-full object-cover"
                />
              </div>
              
              <div className="p-6 sm:p-8">
                <div className="flex justify-between items-start mb-4">
                  <h1 className="text-gray-900">{ad.title}</h1>
                  <p className="text-blue-600">{ad.price}</p>
                </div>
                
                <p className="text-gray-700 leading-relaxed">{ad.description}</p>
              </div>
            </div>
          </div>

          {/* Seller Information */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-8">
              <h3 className="text-gray-900 mb-4">Seller Information</h3>
              
              {seller ? (
                <div className="space-y-4">
                  {/* Seller Name */}
                  <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <User className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-gray-900">{seller.username}</p>
                      <p className="text-gray-500">Member</p>
                    </div>
                  </div>

                  {/* Contact Information */}
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <p className="text-gray-500 mb-1">Email</p>
                        <a href={`mailto:${seller.email}`} className="text-blue-600 hover:text-blue-700">
                          {seller.email}
                        </a>
                      </div>
                    </div>

                    {seller.phone && (
                      <div className="flex items-start gap-3">
                        <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
                        <div>
                          <p className="text-gray-500 mb-1">Phone</p>
                          <a href={`tel:${seller.phone}`} className="text-blue-600 hover:text-blue-700">
                            {seller.phone}
                          </a>
                        </div>
                      </div>
                    )}

                    {seller.location && (
                      <div className="flex items-start gap-3">
                        <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                        <div>
                          <p className="text-gray-500 mb-1">Location</p>
                          <p className="text-gray-900">{seller.location}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Contact Button */}
                  <button className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors mt-4">
                    Contact Seller
                  </button>
                </div>
              ) : (
                <p className="text-gray-600">Seller information not available</p>
              )}
            </div>
          </div>
        </div>

        {similarAds.length > 0 && (
          <div>
            <h2 className="text-gray-900 mb-4">Similar Ads</h2>
            
            <div className="overflow-x-auto -mx-4 px-4 pb-4">
              <div className="flex gap-4 min-w-min">
                {similarAds.map((similarAd) => (
                  <div key={similarAd.id} className="w-64 flex-shrink-0">
                    <AdCard
                      id={similarAd.id}
                      title={similarAd.title}
                      price={similarAd.price}
                      image={similarAd.image}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}