import { useState } from 'react';
import Navigation from '../components/Navigation';
import AdCard from '../components/AdCard';
import { mockAds, currentUser } from '../data/mockData';
import { Edit2, User, Mail, Package } from 'lucide-react';

interface UserProfilePageProps {
  onLogout: () => void;
}

export default function UserProfilePage({ onLogout }: UserProfilePageProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [username, setUsername] = useState(currentUser.username);

  const userAds = mockAds.filter((ad) => ad.userId === currentUser.id);

  const handleSave = () => {
    setIsEditing(false);
    // In a real app, this would save to backend
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation onLogout={onLogout} />
      
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Card */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg overflow-hidden mb-8 shadow-lg">
          <div className="p-8 text-white">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                  <User className="w-10 h-10 text-white" />
                </div>
                <div>
                  <h1 className="text-white mb-1">My Profile</h1>
                  <p className="text-blue-100">Manage your account and ads</p>
                </div>
              </div>
              
              {!isEditing ? (
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors backdrop-blur-sm"
                >
                  <Edit2 className="w-5 h-5" />
                  Edit Profile
                </button>
              ) : (
                <div className="flex gap-2">
                  <button
                    onClick={() => setIsEditing(false)}
                    className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors backdrop-blur-sm"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    className="px-4 py-2 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                  >
                    Save
                  </button>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Username */}
              <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-2">
                  <User className="w-5 h-5 text-blue-100" />
                  <label className="text-blue-100">Username</label>
                </div>
                {isEditing ? (
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-4 py-2 bg-white/90 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-white"
                  />
                ) : (
                  <p className="text-white">{username}</p>
                )}
              </div>

              {/* Email - Read only */}
              <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-2">
                  <Mail className="w-5 h-5 text-blue-100" />
                  <label className="text-blue-100">Email</label>
                </div>
                <p className="text-white">{currentUser.email}</p>
              </div>
            </div>
          </div>
        </div>

        {/* User Ads Section */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 sm:p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
              <Package className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-gray-900">My Ads</h2>
              <p className="text-gray-600">{userAds.length} active listing{userAds.length !== 1 ? 's' : ''}</p>
            </div>
          </div>
          
          {userAds.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {userAds.map((ad) => (
                <AdCard
                  key={ad.id}
                  id={ad.id}
                  title={ad.title}
                  price={ad.price}
                  image={ad.image}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">You haven't posted any ads yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}