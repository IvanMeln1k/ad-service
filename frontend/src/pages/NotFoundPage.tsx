import { Link } from 'react-router-dom';
import { Meta } from '@/shared/seo/Meta';
import { getCanonicalUrl } from '@/shared/seo/url';

export default function NotFoundPage() {
  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <Meta
        title="Страница не найдена"
        description="Запрошенная страница не найдена"
        canonical={getCanonicalUrl('/404')}
        noIndex
      />
      <section className="w-full max-w-md text-center bg-white rounded-lg border border-gray-200 p-8">
        <h1 className="text-gray-900 mb-3">404 — страница не найдена</h1>
        <p className="text-gray-600 mb-6">Проверьте адрес страницы или вернитесь к объявлениям.</p>
        <Link to="/ads" className="inline-block bg-blue-600 text-white py-2 px-5 rounded-lg hover:bg-blue-700 transition-colors">
          К объявлениям
        </Link>
      </section>
    </main>
  );
}
