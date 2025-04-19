'use client';

import { createContext, useContext, useState, useCallback, ReactNode, useRef } from 'react';
import toast from 'react-hot-toast';

export interface LayoutState {
  pageLayout: any[] | null;
  sidebar: any | null;
  serverSidebar: any | null;
  hasChanges: boolean;
  isLoading: boolean;
  currentPath: string | null;
  serverId: string | null;
}

export interface LayoutActions {
  setHasChanges: (value: boolean) => void;
  setPageLayout: (layout: any[]) => void;
  setSidebar: (sidebar: any) => void;
  setServerSidebar: (sidebar: any) => void;
  setCurrentPath: (path: string) => void;
  setServerId: (id: string) => void;
  fetchPageLayout: (page: string) => Promise<void>;
  fetchSidebar: () => Promise<void>;
  fetchServerSidebar: () => Promise<void>;
  saveChanges: () => Promise<void>;
  revertChanges: () => void;
  resetToDefaults: () => Promise<void>;
}

export interface LayoutContextValue extends LayoutState, LayoutActions {}

const LayoutContext = createContext<LayoutContextValue | undefined>(undefined);

interface FetchStates {
  [key: string]: boolean;
}

export function LayoutProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<LayoutState>({
    pageLayout: null,
    sidebar: null,
    serverSidebar: null,
    hasChanges: false,
    isLoading: false,
    currentPath: null,
    serverId: null
  });

  // Use refs to track ongoing fetches
  const fetchingRef = useRef<FetchStates>({});

  const setHasChanges = useCallback((value: boolean) => {
    setState(prev => ({ ...prev, hasChanges: value }));
  }, []);

  const setPageLayout = useCallback((layout: any[]) => {
    setState(prev => ({ ...prev, pageLayout: layout }));
  }, []);

  const setSidebar = useCallback((sidebar: any) => {
    setState(prev => ({ ...prev, sidebar }));
  }, []);

  const setServerSidebar = useCallback((serverSidebar: any) => {
    setState(prev => ({ ...prev, serverSidebar }));
  }, []);

  const setCurrentPath = useCallback((path: string) => {
    setState(prev => ({ ...prev, currentPath: path }));
  }, []);

  const setServerId = useCallback((id: string) => {
    setState(prev => ({ ...prev, serverId: id }));
  }, []);

  const fetchPageLayout = useCallback(async (page: string) => {
    const fetchKey = `page_${page}`;
    if (fetchingRef.current[fetchKey]) return;
    
    try {
      fetchingRef.current[fetchKey] = true;
      setState(prev => ({ ...prev, isLoading: true }));
      
      const response = await fetch(`/api/v1/layout/settings/server/${page}`);
      if (!response.ok) throw new Error('Failed to fetch page layout');
      const data = await response.json();
      setPageLayout(data);
    } catch (error) {
      console.error('Error fetching page layout:', error);
      setPageLayout([]);
      toast.error('Failed to load page layout');
    } finally {
      fetchingRef.current[fetchKey] = false;
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [setPageLayout]);

  const fetchSidebar = useCallback(async () => {
    if (state.sidebar || fetchingRef.current.sidebar) return;
    
    try {
      fetchingRef.current.sidebar = true;
      const response = await fetch('/api/v1/layout/settings/sidebar');
      if (!response.ok) throw new Error('Failed to fetch sidebar');
      const data = await response.json();
      setSidebar(data);
    } catch (error) {
      console.error('Error fetching sidebar:', error);
      toast.error('Failed to load sidebar');
    } finally {
      fetchingRef.current.sidebar = false;
    }
  }, [state.sidebar, setSidebar]);

  const fetchServerSidebar = useCallback(async () => {
    if (state.serverSidebar || fetchingRef.current.serverSidebar) return;
    
    try {
      fetchingRef.current.serverSidebar = true;
      const response = await fetch('/api/v1/layout/settings/server/sidebar');
      if (!response.ok) throw new Error('Failed to fetch server sidebar');
      const data = await response.json();
      setServerSidebar(data);
    } catch (error) {
      console.error('Error fetching server sidebar:', error);
      toast.error('Failed to load server sidebar');
    } finally {
      fetchingRef.current.serverSidebar = false;
    }
  }, [state.serverSidebar, setServerSidebar]);

  const saveChanges = useCallback(async () => {
    if (!state.hasChanges || !state.serverId || !state.currentPath) return;

    try {
      setState(prev => ({ ...prev, isLoading: true }));
      const response = await fetch(`/api/v1/guilds/${state.serverId}/settings/${state.currentPath}`, {
        method: 'POST',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Failed to save changes');
      setHasChanges(false);
      toast.success('Changes saved successfully');
    } catch (error) {
      console.error('Error saving changes:', error);
      toast.error('Failed to save changes');
      throw error;
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [state.hasChanges, state.serverId, state.currentPath, setHasChanges]);

  const revertChanges = useCallback(() => {
    if (!state.hasChanges) return;
    window.dispatchEvent(new CustomEvent('revertChanges'));
    setHasChanges(false);
    toast.success('Changes reverted');
  }, [state.hasChanges, setHasChanges]);

  const resetToDefaults = useCallback(async () => {
    if (!state.serverId || !state.currentPath) return;

    try {
      setState(prev => ({ ...prev, isLoading: true }));
      const response = await fetch(`/api/v1/guilds/${state.serverId}/settings/${state.currentPath}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Failed to reset settings');
      window.dispatchEvent(new CustomEvent('settingsReset'));
      toast.success('Settings reset to defaults');
    } catch (error) {
      console.error('Error resetting settings:', error);
      toast.error('Failed to reset settings');
      throw error;
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [state.serverId, state.currentPath]);

  const value: LayoutContextValue = {
    ...state,
    setHasChanges,
    setPageLayout,
    setSidebar,
    setServerSidebar,
    setCurrentPath,
    setServerId,
    fetchPageLayout,
    fetchSidebar,
    fetchServerSidebar,
    saveChanges,
    revertChanges,
    resetToDefaults
  };

  return (
    <LayoutContext.Provider value={value}>
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