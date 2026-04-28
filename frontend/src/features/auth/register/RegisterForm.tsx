import { useState } from 'react';
import { UserPlus } from 'lucide-react';
import { registerUser } from '@/entities/user/api';
import { ApiError } from '@/shared/api/client';
import type { AuthResponse } from '@/entities/user/model';

interface RegisterFormProps {
  onSuccess: (data: AuthResponse) => void;
}

export function RegisterForm({ onSuccess }: RegisterFormProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await registerUser({ email, name, password });
      onSuccess(data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError('Этот email уже занят');
      } else {
        setError('Ошибка регистрации. Попробуйте позже.');
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

      <div>
        <label htmlFor="register-name" className="block text-gray-700 mb-2">
          Имя
        </label>
        <input
          type="text"
          id="register-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Иван Иванов"
          required
        />
      </div>

      <div>
        <label htmlFor="register-email" className="block text-gray-700 mb-2">
          Email
        </label>
        <input
          type="email"
          id="register-email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="you@example.com"
          required
        />
      </div>

      <div>
        <label htmlFor="register-password" className="block text-gray-700 mb-2">
          Пароль
        </label>
        <input
          type="password"
          id="register-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="••••••••"
          minLength={6}
          required
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <UserPlus className="w-5 h-5" />
        {loading ? 'Регистрация...' : 'Зарегистрироваться'}
      </button>
    </form>
  );
}
