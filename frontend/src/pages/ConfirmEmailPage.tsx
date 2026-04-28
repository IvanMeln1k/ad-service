import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { apiPost, ApiError } from '@/shared/api/client';
import { Meta } from '@/shared/seo/Meta';
import { getCanonicalUrl } from '@/shared/seo/url';

export default function ConfirmEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setErrorMessage('Токен не найден в ссылке');
      return;
    }

    apiPost('/confirm-email', { token })
      .then(() => setStatus('success'))
      .catch((err) => {
        setStatus('error');
        if (err instanceof ApiError) {
          setErrorMessage(err.message);
        } else {
          setErrorMessage('Не удалось подтвердить email');
        }
      });
  }, [token]);

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <Meta
        title="Подтверждение email"
        description="Подтверждение email адреса"
        canonical={getCanonicalUrl('/confirm-email')}
        noIndex
      />
      <div className="w-full max-w-md text-center">
        <h1 className="text-blue-600 mb-6">ClassifiedAds</h1>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          {status === 'loading' && (
            <p className="text-gray-600">Подтверждаем ваш email...</p>
          )}

          {status === 'success' && (
            <>
              <div className="text-green-600 text-4xl mb-4">&#10003;</div>
              <h2 className="text-gray-900 mb-2">Email подтверждён</h2>
              <p className="text-gray-600 mb-6">Теперь вы можете пользоваться всеми функциями сервиса.</p>
              <Link
                to="/login"
                className="inline-block bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Войти
              </Link>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="text-red-500 text-4xl mb-4">&#10007;</div>
              <h2 className="text-gray-900 mb-2">Ошибка</h2>
              <p className="text-gray-600 mb-6">{errorMessage}</p>
              <Link
                to="/login"
                className="inline-block bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors"
              >
                На страницу входа
              </Link>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
