import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider, useAuth } from '@/app/providers/AuthProvider';
import { useAttributes } from '@/shared/hooks/useAttributes';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import AllAdsPage from '@/pages/AllAdsPage';
import AdDetailsPage from '@/pages/AdDetailsPage';
import UserProfilePage from '@/pages/UserProfilePage';
import CreateAdPage from '@/pages/CreateAdPage';
import ConfirmEmailPage from '@/pages/ConfirmEmailPage';
import NotFoundPage from '@/pages/NotFoundPage';

function RoleRoute({
  attr,
  element,
}: {
  attr: 'can_create_ad' | 'can_moderate';
  element: JSX.Element;
}) {
  const values = useAttributes([attr]);
  const allowed = Boolean(values[attr]);
  if (values.loading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-500">Проверка прав...</div>;
  }
  if (!allowed) {
    return <Navigate to="/ads" replace />;
  }
  return element;
}

function AppRoutes() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <Routes>
      <Route path="/confirm-email" element={<ConfirmEmailPage />} />
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/ads" /> : <LoginPage />}
      />
      <Route
        path="/register"
        element={isAuthenticated ? <Navigate to="/ads" /> : <RegisterPage />}
      />
      <Route
        path="/ads"
        element={isAuthenticated ? <AllAdsPage onLogout={logout} /> : <Navigate to="/login" />}
      />
      <Route
        path="/ads/new"
        element={
          isAuthenticated ? (
            <RoleRoute attr="can_create_ad" element={<CreateAdPage onLogout={logout} />} />
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/ads/:id"
        element={isAuthenticated ? <AdDetailsPage onLogout={logout} /> : <Navigate to="/login" />}
      />
      <Route
        path="/profile"
        element={isAuthenticated ? <UserProfilePage onLogout={logout} /> : <Navigate to="/login" />}
      />
      <Route path="/" element={<Navigate to={isAuthenticated ? '/ads' : '/login'} />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

export default function App() {
  return (
    <HelmetProvider>
      <Router>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </Router>
    </HelmetProvider>
  );
}
