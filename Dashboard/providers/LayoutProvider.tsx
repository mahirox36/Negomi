'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { SidebarLayout, LayoutItem } from '../types/layout';

interface LayoutContextType {
  sidebar: SidebarLayout | null;
  serverSidebar: SidebarLayout | null;
  pageLayout: LayoutItem[] | null;
  fetchSidebar: () => Promise<void>;
  fetchServerSidebar: () => Promise<void>;
  fetchPageLayout: (page: string) => Promise<void>;
}

const LayoutContext = createContext<LayoutContextType | null>(null);

export function LayoutProvider({ children }: { children: React.ReactNode }) {
  const [sidebar, setSidebar] = useState<SidebarLayout | null>(null);
  const [serverSidebar, setServerSidebar] = useState<SidebarLayout | null>(null);
  const [pageLayout, setPageLayout] = useState<LayoutItem[] | null>(null);

  const fetchSidebar = useCallback(async () => {
    if (sidebar) return;
    const response = await fetch('/api/layout/settings/sidebar');
    const data = await response.json();
    setSidebar(data);
  }, [sidebar]);

  const fetchServerSidebar = useCallback(async () => {
    if (serverSidebar) return;
    const response = await fetch('/api/layout/settings/server/sidebar');
    const data = await response.json();
    setServerSidebar(data);
  }, [serverSidebar]);

  const fetchPageLayout = useCallback(async (page: string) => {
    try {
      const response = await fetch(`/api/layout/settings/server/${page}`);
      if (!response.ok) {
        throw new Error('Failed to fetch page layout');
      }
      const data = await response.json();
      setPageLayout(data);
    } catch (error) {
      console.error('Error fetching page layout:', error);
      setPageLayout(null);
    }
  }, []);

  return (
    <LayoutContext.Provider 
      value={{ 
        sidebar, 
        serverSidebar, 
        pageLayout, 
        fetchSidebar, 
        fetchServerSidebar, 
        fetchPageLayout 
      }}
    >
      {children}
    </LayoutContext.Provider>
  );
}

export function useLayout() {
  const context = useContext(LayoutContext);
  if (!context) {
    throw new Error('useLayout must be used within a LayoutProvider');
  }
  return context;
}
