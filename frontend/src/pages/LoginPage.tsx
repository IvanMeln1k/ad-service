import { Link, useNavigate } from 'react-router-dom';
import { LoginForm } from '@/features/auth/login/LoginForm';
import { useAuth } from '@/app/providers/AuthProvider';
import { Meta } from '@/shared/seo/Meta';
import { getCanonicalUrl } from '@/shared/seo/url';

export default function LoginPage() {
  const navigate = useNavigate();
  const { handleAuthSuccess } = useAuth();

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <Meta
        title="Вход"
        description="Войдите в аккаунт ClassifiedAds"
        canonical={getCanonicalUrl('/login')}
        noIndex
      />
      <div className="w-full max-w-md">
        <header className="text-center mb-8">
          <h1 className="text-blue-600 mb-2">ClassifiedAds</h1>
          <p className="text-gray-600">Войдите в аккаунт</p>
        </header>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <LoginForm
            onSuccess={(data) => {
              handleAuthSuccess(data);
              navigate('/ads');
            }}
          />

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Нет аккаунта?{' '}
              <Link to="/register" className="text-blue-600 hover:text-blue-700">
                Зарегистрироваться
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
