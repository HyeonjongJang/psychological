'use client';

import { useState } from 'react';
import { useLanguage } from '@/context/LanguageContext';

interface LikertScaleProps {
  onSelect: (value: number) => void;
  disabled?: boolean;
  selected?: number | null;
}

export default function LikertScale({ onSelect, disabled = false, selected = null }: LikertScaleProps) {
  const { t } = useLanguage();
  const [hoveredValue, setHoveredValue] = useState<number | null>(null);

  const labels = t.likert.labels.map((label, index) => ({
    value: index + 1,
    label,
  }));

  return (
    <div className="w-full">
      <div className="flex justify-between mb-2 text-xs text-gray-500">
        <span>{t.likert.labels[0]}</span>
        <span>{t.likert.labels[6]}</span>
      </div>
      <div className="flex gap-2 justify-center">
        {labels.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => !disabled && onSelect(value)}
            onMouseEnter={() => !disabled && setHoveredValue(value)}
            onMouseLeave={() => setHoveredValue(null)}
            disabled={disabled}
            className={`
              w-10 h-10 rounded-full font-semibold transition-all duration-200
              ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
              ${selected === value
                ? 'bg-primary-600 text-white scale-110'
                : hoveredValue === value
                  ? 'bg-primary-100 text-primary-700 scale-105'
                  : 'bg-gray-100 text-gray-700 hover:bg-primary-50'
              }
            `}
            title={label}
          >
            {value}
          </button>
        ))}
      </div>
      {hoveredValue && (
        <div className="text-center mt-2 text-sm text-gray-600">
          {labels.find(l => l.value === hoveredValue)?.label}
        </div>
      )}
    </div>
  );
}
