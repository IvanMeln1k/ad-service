export const CATEGORY_OPTIONS = [
  { value: 'AUTO', label: 'Авто' },
  { value: 'REALTY', label: 'Недвижимость' },
  { value: 'ELECTRONICS', label: 'Электроника' },
  { value: 'CLOTHING', label: 'Одежда' },
  { value: 'SERVICES', label: 'Услуги' },
  { value: 'OTHER', label: 'Другое' },
] as const;

const CATEGORY_LABEL_MAP: Record<string, string> = CATEGORY_OPTIONS.reduce(
  (acc, option) => {
    acc[option.value] = option.label;
    return acc;
  },
  {} as Record<string, string>
);

export function getCategoryLabel(category?: string): string {
  if (!category) {
    return 'Не указана';
  }
  return CATEGORY_LABEL_MAP[category] ?? category;
}
