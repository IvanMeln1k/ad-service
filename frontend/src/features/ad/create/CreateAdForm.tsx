import { useState } from 'react';
import { ChevronDown, Plus, Upload, X } from 'lucide-react';
import { createAd, presignPhoto, confirmPhoto } from '@/entities/ad/api';
import { CATEGORY_OPTIONS } from '@/entities/ad/category';
import { ApiError } from '@/shared/api/client';
import type { Ad } from '@/entities/ad/model';

interface CreateAdFormProps {
  onSuccess: (ad: Ad) => void;
}

export function CreateAdForm({ onSuccess }: CreateAdFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [city, setCity] = useState('');
  const [category, setCategory] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [uploadStatus, setUploadStatus] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const MAX_FILE_SIZE = 10 * 1024 * 1024;
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

  const handleFiles = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files);
      const valid: File[] = [];
      for (const file of selected) {
        if (!ALLOWED_TYPES.includes(file.type)) {
          setError('Разрешены только файлы JPG/PNG/WEBP');
          continue;
        }
        if (file.size > MAX_FILE_SIZE) {
          setError('Размер файла не должен превышать 10MB');
          continue;
        }
        valid.push(file);
      }
      setFiles((prev) => [...prev, ...valid]);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setUploadStatus('');
    setLoading(true);

    try {
      if (title.trim().length < 3 || description.trim().length < 10) {
        setError('Заполните название (от 3) и описание (от 10 символов)');
        return;
      }

      const ad = await createAd({
        title: title.trim(),
        description: description.trim(),
        price: price ? Number(price) : undefined,
        city: city.trim() || undefined,
        category: category || undefined,
      });

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setUploadStatus(`Загрузка файла ${i + 1}/${files.length}`);
        const { upload_url, s3_key } = await presignPhoto(ad.id, file.name, file.type, file.size);
        await fetch(upload_url, {
          method: 'PUT',
          body: file,
          headers: { 'Content-Type': file.type },
        });
        await confirmPhoto(ad.id, s3_key, i);
      }

      setUploadStatus('');
      onSuccess(ad);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError('Подтвердите email для создания объявлений');
      } else if (err instanceof ApiError && err.status === 400) {
        setError('Файл не прошел серверную валидацию (тип/размер)');
      } else {
        setError('Ошибка создания объявления');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div role="alert" className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}
      {uploadStatus && (
        <div className="bg-blue-50 text-blue-700 px-4 py-3 rounded-lg text-sm">
          {uploadStatus}
        </div>
      )}

      <div>
        <label htmlFor="ad-title" className="block text-gray-700 mb-2">Название</label>
        <input
          type="text"
          id="ad-title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Что продаёте?"
          required
        />
      </div>

      <div>
        <label htmlFor="ad-description" className="block text-gray-700 mb-2">Описание</label>
        <textarea
          id="ad-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={5}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
          placeholder="Опишите подробнее"
          required
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label htmlFor="ad-price" className="block text-gray-700 mb-2">Цена</label>
          <input
            type="number"
            id="ad-price"
            value={price}
            min={0}
            onChange={(e) => setPrice(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            placeholder="10000"
          />
        </div>
        <div>
          <label htmlFor="ad-city" className="block text-gray-700 mb-2">Город</label>
          <input
            type="text"
            id="ad-city"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            placeholder="Москва"
          />
        </div>
        <div>
          <label htmlFor="ad-category" className="block text-gray-700 mb-2">Категория</label>
          <div className="relative">
            <select
              id="ad-category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full appearance-none px-4 py-2 pr-10 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            >
              <option value="">Выберите категорию</option>
              {CATEGORY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          </div>
        </div>
      </div>

      <div>
        <label className="block text-gray-700 mb-2">Фотографии</label>
        <div className="flex flex-wrap gap-3">
          {files.map((file, i) => (
            <div key={i} className="relative w-20 h-20 rounded-lg overflow-hidden border border-gray-200">
              <img src={URL.createObjectURL(file)} alt="" className="w-full h-full object-cover" />
              <button
                type="button"
                onClick={() => removeFile(i)}
                className="absolute top-0 right-0 bg-red-500 text-white rounded-bl-lg p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
          <label className="w-20 h-20 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center cursor-pointer hover:border-blue-500 transition-colors">
            <Upload className="w-5 h-5 text-gray-400" />
            <input type="file" accept="image/*" multiple onChange={handleFiles} className="hidden" />
          </label>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <Plus className="w-5 h-5" />
        {loading ? 'Создание...' : 'Опубликовать'}
      </button>
    </form>
  );
}
