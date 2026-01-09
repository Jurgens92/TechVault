/**
 * ChoicesContext - Single Source of Truth for all dropdown choices/enums
 *
 * This context fetches choices from /api/meta/choices/ and provides them
 * to all form components. This ensures consistency between frontend and
 * backend without duplicating enum definitions.
 *
 * Usage:
 *   const { choices, getChoiceLabel } = useChoices();
 *   // In a select:
 *   {choices.documentation_category.map(c => (
 *     <option key={c.value} value={c.value}>{c.label}</option>
 *   ))}
 */

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import api from '../services/api';
import { Choices, Choice } from '../types/choices';

interface ChoicesContextType {
  choices: Choices | null;
  loading: boolean;
  error: string | null;
  getChoiceLabel: (category: keyof Choices, value: string) => string;
  getChoicesForField: (category: keyof Choices) => Choice[];
  refreshChoices: () => Promise<void>;
}

const defaultChoices: Choices = {
  documentation_category: [],
  password_category: [],
  configuration_type: [],
  network_device_type: [],
  endpoint_device_type: [],
  server_type: [],
  peripheral_type: [],
  software_type: [],
  license_type: [],
  backup_type: [],
  backup_status: [],
  voip_type: [],
};

const ChoicesContext = createContext<ChoicesContextType>({
  choices: null,
  loading: true,
  error: null,
  getChoiceLabel: () => '',
  getChoicesForField: () => [],
  refreshChoices: async () => {},
});

export const useChoices = () => {
  const context = useContext(ChoicesContext);
  if (!context) {
    throw new Error('useChoices must be used within a ChoicesProvider');
  }
  return context;
};

interface ChoicesProviderProps {
  children: ReactNode;
}

export const ChoicesProvider: React.FC<ChoicesProviderProps> = ({ children }) => {
  const [choices, setChoices] = useState<Choices | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchChoices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get<Choices>('/api/meta/choices/');
      setChoices(response.data);
    } catch (err: any) {
      console.error('Failed to fetch choices:', err);
      setError(err.response?.data?.detail || 'Failed to load choices');
      // Fall back to empty choices
      setChoices(defaultChoices);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChoices();
  }, [fetchChoices]);

  const getChoiceLabel = useCallback((category: keyof Choices, value: string): string => {
    if (!choices) return value;
    const categoryChoices = choices[category] || [];
    const choice = categoryChoices.find(c => c.value === value);
    return choice?.label || value;
  }, [choices]);

  const getChoicesForField = useCallback((category: keyof Choices): Choice[] => {
    if (!choices) return [];
    return choices[category] || [];
  }, [choices]);

  const refreshChoices = useCallback(async () => {
    await fetchChoices();
  }, [fetchChoices]);

  return (
    <ChoicesContext.Provider
      value={{
        choices,
        loading,
        error,
        getChoiceLabel,
        getChoicesForField,
        refreshChoices,
      }}
    >
      {children}
    </ChoicesContext.Provider>
  );
};

export default ChoicesContext;
