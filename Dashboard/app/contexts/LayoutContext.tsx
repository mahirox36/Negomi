'use client';

import { createContext, useContext, ReactNode } from 'react';

export interface LayoutContextType {
  hasChanges: boolean;
  setHasChanges: (value: boolean) => void;
  onSave?: () => Promise<void>;
  onRevert?: () => void;
  onReset?: () => Promise<void>;
}

export const LayoutContext = createContext<LayoutContextType | undefined>(undefined);

export const useLayout = () => {
  const context = useContext(LayoutContext);
  if (!context) {
    throw new Error('useLayout must be used within a LayoutProvider');
  }
  return context;
};

export const LayoutProvider = LayoutContext.Provider;
