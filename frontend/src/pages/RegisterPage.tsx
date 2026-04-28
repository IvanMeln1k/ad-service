import { Link, useNavigate } from 'react-router-dom';
import { RegisterForm } from '@/features/auth/register/RegisterForm';
import { useAuth } from '@/app/providers/AuthProvider';
import { Meta } from '@/shared/seo/Meta';
import { getCanonicalUrl } from '@/shared/seo/url';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { handleAuthSuccess } = useAuth();

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <Meta
        title="Регистрация"
        description="Создайте аккаунт на ClassifiedAds для размещения и поиска объявлений"
        canonical={getCanonicalUrl('/register')}
        noIndex
      />
      <div className="w-full max-w-md">
        <header className="text-center mb-8">
          <h1 className="text-blue-600 mb-2">ClassifiedAds</h1>
          <p className="text-gray-600">Создайте аккаунт</p>
        </header>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <RegisterForm
            onSuccess={(data) => {
              handleAuthSuccess(data);
              navigate('/ads');
            }}
          />

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Уже есть аккаунт?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700">
                Войти
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
