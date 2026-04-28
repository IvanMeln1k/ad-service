import { useState, useEffect } from 'react';
import { getAttributes } from '@/entities/ad/api';

export function useAttributes(attrs: string[]) {
  const [values, setValues] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (attrs.length === 0) {
      setLoading(false);
      return;
    }
    getAttributes(attrs)
      .then(setValues)
      .catch(() => setValues({}))
      .finally(() => setLoading(false));
  }, [attrs.join(',')]);

  return { ...values, loading };
}
