'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { registerParticipant } from '@/lib/api';
import { useLanguage } from '@/context/LanguageContext';

export default function Home() {
  const router = useRouter();
  const { language, setLanguage, t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const participant = await registerParticipant({
        age: formData.age ? parseInt(formData.age) : undefined,
        gender: formData.gender || undefined,
      });

      // Store participant info and language in localStorage
      localStorage.setItem('participantId', participant.id);
      localStorage.setItem('participantCode', participant.participant_code);
      localStorage.setItem('preferredLanguage', language);

      // Redirect to assessment hub
      router.push(`/assessment/${participant.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to register');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {/* Language Toggle */}
          <div className="flex justify-center gap-2 mb-6">
            <button
              onClick={() => setLanguage('en')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                language === 'en'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              English
            </button>
            <button
              onClick={() => setLanguage('kr')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                language === 'kr'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              한국어
            </button>
          </div>

          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {t.landing.title}
            </h1>
            <p className="text-gray-600">
              {t.landing.subtitle}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="age" className="block text-sm font-medium text-gray-700 mb-1">
                {t.landing.ageLabel}
              </label>
              <input
                type="number"
                id="age"
                min="18"
                max="120"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder={t.landing.agePlaceholder}
              />
            </div>

            <div>
              <label htmlFor="gender" className="block text-sm font-medium text-gray-700 mb-1">
                {t.landing.genderLabel}
              </label>
              <select
                id="gender"
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">{t.landing.genderOptions.preferNot}</option>
                <option value="male">{t.landing.genderOptions.male}</option>
                <option value="female">{t.landing.genderOptions.female}</option>
                <option value="non-binary">{t.landing.genderOptions.nonBinary}</option>
                <option value="other">{t.landing.genderOptions.other}</option>
              </select>
            </div>

            {error && (
              <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? t.landing.startingButton : t.landing.startButton}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            <p>{t.landing.assessmentInfo}</p>
            <ul className="mt-2 space-y-1">
              {t.landing.assessmentTypes.map((type, index) => (
                <li key={index}>{type}</li>
              ))}
            </ul>
            <p className="mt-2 text-xs text-gray-400">
              {t.landing.randomOrderNote}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
