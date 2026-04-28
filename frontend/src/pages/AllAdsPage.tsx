import { useEffect, useMemo, useState } from 'react';
import { RotateCcw, Search, SlidersHorizontal, X } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import Navigation from '../components/Navigation';
import AdCard from '../components/AdCard';
import { listAds } from '@/entities/ad/api';
import { CATEGORY_OPTIONS, getCategoryLabel } from '@/entities/ad/category';
import { Meta } from '@/shared/seo/Meta';
import { getCanonicalUrl } from '@/shared/seo/url';
import type { Ad } from '@/entities/ad/model';

interface AllAdsPageProps {
  onLogout: () => void;
}

export default function AllAdsPage({ onLogout }: AllAdsPageProps) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [ads, setAds] = useState<Ad[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchInput, setSearchInput] = useState('');

  const filters = useMemo(() => {
    const limit = Number(searchParams.get('limit') || 12);
    const offset = Number(searchParams.get('offset') || 0);
    return {
      search: searchParams.get('search') || '',
      category: searchParams.get('category') || '',
      city: searchParams.get('city') || '',
      priceMin: searchParams.get('price_min') || '',
      priceMax: searchParams.get('price_max') || '',
      sortBy: (searchParams.get('sort_by') || 'created_at') as 'created_at' | 'price' | 'title',
      sortOrder: (searchParams.get('sort_order') || 'desc') as 'asc' | 'desc',
      limit: Number.isFinite(limit) && limit > 0 ? limit : 12,
      offset: Number.isFinite(offset) && offset >= 0 ? offset : 0,
    };
  }, [searchParams]);

  useEffect(() => {
    setSearchInput(filters.search);
  }, [filters.search]);

  const fetchAds = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await listAds({
        search: filters.search || undefined,
        category: filters.category || undefined,
        city: filters.city || undefined,
        price_min: filters.priceMin ? Number(filters.priceMin) : undefined,
        price_max: filters.priceMax ? Number(filters.priceMax) : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
        limit: filters.limit,
        offset: filters.offset,
      });
      setAds(data.items);
      setTotal(data.total);
    } catch {
      setAds([]);
      setTotal(0);
      setError('Не удалось загрузить объявления');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAds();
  }, [searchParams]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    updateFilter('search', searchInput.trim());
  };

  const updateFilter = (name: string, value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(name, value);
    } else {
      next.delete(name);
    }
    next.set('offset', '0');
    setSearchParams(next);
  };

  const handlePageChange = (offset: number) => {
    const next = new URLSearchParams(searchParams);
    next.set('offset', String(Math.max(0, offset)));
    setSearchParams(next);
  };

  const hasPrev = filters.offset > 0;
  const hasNext = filters.offset + filters.limit < total;

  const resetFilters = () => {
    setSearchParams(new URLSearchParams({ limit: String(filters.limit), offset: '0' }));
  };

  const activeFilters = [
    filters.search ? `Поиск: ${filters.search}` : null,
    filters.city ? `Город: ${filters.city}` : null,
    filters.category ? `Категория: ${getCategoryLabel(filters.category)}` : null,
    filters.priceMin ? `Цена от: ${filters.priceMin}` : null,
    filters.priceMax ? `Цена до: ${filters.priceMax}` : null,
  ].filter(Boolean) as string[];

  return (
    <div className="min-h-screen bg-gray-50">
      <Meta
        title="Объявления"
        description="Все объявления на ClassifiedAds"
        canonical={getCanonicalUrl('/ads')}
      />
      <Navigation onLogout={onLogout} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <h1 className="text-gray-900">Объявления</h1>

          <form onSubmit={handleSearch} className="flex w-full md:w-auto gap-2">
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Поиск..."
              className="w-full md:w-80 px-4 py-2.5 border border-gray-300 rounded-xl bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
            <button
              type="submit"
              className="px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors shadow-sm"
            >
              <Search className="w-5 h-5" />
            </button>
          </form>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-6 shadow-sm">
          <div className="flex items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="w-4 h-4 text-gray-500" />
              <p className="text-sm font-medium text-gray-800">Фильтры и сортировка</p>
            </div>
            <button
              type="button"
              onClick={resetFilters}
              className="inline-flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Сбросить
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            <label className="block">
              <span className="text-sm text-gray-600 mb-1.5 block">Город</span>
              <input
                value={filters.city}
                onChange={(e) => updateFilter('city', e.target.value)}
                placeholder="Например, Саратов"
                className="w-full px-3 py-2.5 text-sm border border-gray-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </label>

            <label className="block">
              <span className="text-sm text-gray-600 mb-1.5 block">Категория</span>
              <div className="relative">
                <select
                  value={filters.category}
                  onChange={(e) => updateFilter('category', e.target.value)}
                  className="w-full appearance-none px-3 py-2.5 pr-10 text-sm border border-gray-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                >
                  <option value="">Все категории</option>
                  {CATEGORY_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <svg
                  className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            </label>

            <label className="block">
              <span className="text-sm text-gray-600 mb-1.5 block">Цена от</span>
              <input
                value={filters.priceMin}
                onChange={(e) => updateFilter('price_min', e.target.value)}
                type="number"
                min={0}
                placeholder="0"
                className="w-full px-3 py-2.5 text-sm border border-gray-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </label>

            <label className="block">
              <span className="text-sm text-gray-600 mb-1.5 block">Цена до</span>
              <input
                value={filters.priceMax}
                onChange={(e) => updateFilter('price_max', e.target.value)}
                type="number"
                min={0}
                placeholder="100000"
                className="w-full px-3 py-2.5 text-sm border border-gray-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </label>

            <label className="block">
              <span className="text-sm text-gray-600 mb-1.5 block">Сортировать по</span>
              <div className="relative">
                <select
                  value={filters.sortBy}
                  onChange={(e) => updateFilter('sort_by', e.target.value)}
                  className="w-full appearance-none px-3 py-2.5 pr-10 text-sm border border-gray-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                >
                  <option value="created_at">Дате</option>
                  <option value="price">Цене</option>
                  <option value="title">Названию</option>
                </select>
                <svg
                  className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            </label>

            <label className="block">
              <span className="text-sm text-gray-600 mb-1.5 block">Порядок</span>
              <div className="relative">
                <select
                  value={filters.sortOrder}
                  onChange={(e) => updateFilter('sort_order', e.target.value)}
                  className="w-full appearance-none px-3 py-2.5 pr-10 text-sm border border-gray-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                >
                  <option value="desc">По убыванию</option>
                  <option value="asc">По возрастанию</option>
                </select>
                <svg
                  className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            </label>
          </div>

          {activeFilters.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {activeFilters.map((item) => (
                <span
                  key={item}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs bg-blue-50 text-blue-700 border border-blue-200"
                >
                  {item}
                </span>
              ))}
              <button
                type="button"
                onClick={resetFilters}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200 transition-colors"
              >
                <X className="w-3 h-3" />
                Очистить все
              </button>
            </div>
          )}
        </div>

        {loading ? (
          <p className="text-gray-500 text-center py-12">Загрузка...</p>
        ) : error ? (
          <p className="text-red-600 text-center py-12">{error}</p>
        ) : ads.length === 0 ? (
          <p className="text-gray-500 text-center py-12">Объявлений не найдено</p>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {ads.map((ad) => (
                <AdCard key={ad.id} ad={ad} />
              ))}
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-6">
              <p className="text-sm text-gray-600 bg-white border border-gray-200 rounded-xl px-3 py-2 w-fit">
                Показано {filters.offset + 1}-{Math.min(filters.offset + ads.length, total)} из {total}
              </p>
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={!hasPrev}
                  onClick={() => handlePageChange(filters.offset - filters.limit)}
                  className="px-4 py-2 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Назад
                </button>
                <button
                  type="button"
                  disabled={!hasNext}
                  onClick={() => handlePageChange(filters.offset + filters.limit)}
                  className="px-4 py-2 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Вперёд
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
