import { useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { User, LogOut, Plus } from 'lucide-react';
import { useAttributes } from '@/shared/hooks/useAttributes';

interface NavigationProps {
  onLogout: () => void;
}

const ATTRS = ['can_create_ad'];

export default function Navigation({ onLogout }: NavigationProps) {
  const location = useLocation();
  const { can_create_ad } = useAttributes(ATTRS);

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/ads" className="text-blue-600">
            ClassifiedAds
          </Link>

          <div className="flex items-center gap-3">
            {can_create_ad && (
              <Link
                to="/ads/new"
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Подать объявление
              </Link>
            )}

            <Link
              to="/profile"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                location.pathname === '/profile'
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <User className="w-5 h-5" />
              Профиль
            </Link>

            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              Выйти
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
