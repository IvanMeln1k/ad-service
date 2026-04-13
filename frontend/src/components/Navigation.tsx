import { Link, useLocation } from 'react-router-dom';
import { User, LogOut } from 'lucide-react';

interface NavigationProps {
  onLogout: () => void;
}

export default function Navigation({ onLogout }: NavigationProps) {
  const location = useLocation();

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/ads" className="text-blue-600">
            ClassifiedAds
          </Link>
          
          <div className="flex items-center gap-4">
            <Link 
              to="/profile"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                location.pathname === '/profile' 
                  ? 'bg-blue-50 text-blue-600' 
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <User className="w-5 h-5" />
              My Profile
            </Link>
            
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
