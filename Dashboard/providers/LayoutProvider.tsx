'use client';

import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import { SidebarLayout, LayoutItem } from '../types/layout';
import toast from 'react-hot-toast';

interface LayoutState {
  sidebar: SidebarLayout | null;
  serverSidebar: SidebarLayout | null;
  pageLayout: LayoutItem[] | null;
  isLoading: boolean;
  hasChanges: boolean;
  currentPath: string | null;
  serverId: string | null;
}

interface LayoutContextType extends LayoutState {
  setHasChanges: (value: boolean) => void;
  setCurrentPath: (path: string) => void;
  setServerId: (id: string) => void;
  fetchSidebar: () => Promise<void>;
  fetchServerSidebar: () => Promise<void>;
  fetchPageLayout: (page: string) => Promise<void>;
  saveChanges: () => Promise<void>;
  revertChanges: () => void;
  resetToDefaults: () => Promise<void>;
}

const LayoutContext = createContext<LayoutContextType | null>(null);

interface FetchState {
  [key: string]: boolean;
}

export function LayoutProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<LayoutState>({
    sidebar: null,
    serverSidebar: null,
    pageLayout: null,
    isLoading: false,
    hasChanges: false,
    currentPath: null,
    serverId: null
  });

  // Use ref to track ongoing fetches to prevent duplicate requests
  const fetchingRef = useRef<FetchState>({});
  const layoutCacheRef = useRef<{[key: string]: LayoutItem[]}>({});

  const setHasChanges = useCallback((value: boolean) => {
    setState(prev => ({ ...prev, hasChanges: value }));
  }, []);

  const setCurrentPath = useCallback((path: string) => {
    setState(prev => ({ ...prev, currentPath: path }));
  }, []);

  const setServerId = useCallback((id: string) => {
    setState(prev => ({ ...prev, serverId: id }));
  }, []);

  const fetchSidebar = useCallback(async () => {
    if (state.sidebar || fetchingRef.current.sidebar) return;
    
    try {
      fetchingRef.current.sidebar = true;
      const response = await fetch('/api/v1/layout/settings/sidebar');
      if (!response.ok) throw new Error('Failed to fetch sidebar');
      const data = await response.json();
      setState(prev => ({ ...prev, sidebar: data }));
    } catch (error) {
      console.error('Error fetching sidebar:', error);
      toast.error('Failed to load sidebar');
    } finally {
      fetchingRef.current.sidebar = false;
    }
  }, [state.sidebar]);

  const fetchServerSidebar = useCallback(async () => {
    if (state.serverSidebar || fetchingRef.current.serverSidebar) return;
    
    try {
      fetchingRef.current.serverSidebar = true;
      const response = await fetch('/api/v1/layout/settings/server/sidebar');
      if (!response.ok) throw new Error('Failed to fetch server sidebar');
      const data = await response.json();
      setState(prev => ({ ...prev, serverSidebar: data }));
    } catch (error) {
      console.error('Error fetching server sidebar:', error);
      toast.error('Failed to load server sidebar');
    } finally {
      fetchingRef.current.serverSidebar = false;
    }
  }, [state.serverSidebar]);

  const fetchPageLayout = useCallback(async (page: string) => {
    const fetchKey = `page_${page}`;
    
    // Return cached layout if available
    if (layoutCacheRef.current[page]) {
      setState(prev => ({ ...prev, pageLayout: layoutCacheRef.current[page] }));
      return;
    }

    if (fetchingRef.current[fetchKey]) return;
    
    try {
      fetchingRef.current[fetchKey] = true;
      setState(prev => ({ ...prev, isLoading: true }));
      
      const response = await fetch(`/api/v1/layout/settings/server/${page}`);
      if (!response.ok) throw new Error('Failed to fetch page layout');
      const data = await response.json();
      
      // Cache the layout
      layoutCacheRef.current[page] = data;
      setState(prev => ({ 
        ...prev, 
        pageLayout: data,
        isLoading: false 
      }));
    } catch (error) {
      console.error('Error fetching page layout:', error);
      setState(prev => ({ ...prev, pageLayout: null, isLoading: false }));
      toast.error('Failed to load page layout');
    } finally {
      fetchingRef.current[fetchKey] = false;
    }
  }, []);

  const saveChanges = useCallback(async () => {
    if (!state.hasChanges || !state.serverId || !state.currentPath) return;

    try {
      setState(prev => ({ ...prev, isLoading: true }));
      
      // Get current settings from the correct location in app state
      // This will be from the React component that set hasChanges to true
      const settingsData = {};
      window.dispatchEvent(new CustomEvent('getUnsavedSettings', { 
        detail: { 
          callback: (settings: any) => {
            Object.assign(settingsData, settings);
          } 
        }
      }));
      
      const response = await fetch(`/api/v1/guilds/${state.serverId}/settings/${state.currentPath}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settingsData),
        credentials: 'include'
      });
      
      if (!response.ok) throw new Error('Failed to save changes');
      setHasChanges(false);
      toast.success('Changes saved successfully');
    } catch (error) {
      console.error('Error saving changes:', error);
      toast.error('Failed to save changes');
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [state.hasChanges, state.serverId, state.currentPath, setHasChanges]);

  const revertChanges = useCallback(() => {
    if (!state.hasChanges) return;
    // Dispatch event to notify components to revert their changes
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
      // Dispatch event to notify components that settings have been reset
      window.dispatchEvent(new CustomEvent('settingsReset'));
      toast.success('Settings reset to defaults');
    } catch (error) {
      console.error('Error resetting settings:', error);
      toast.error('Failed to reset settings');
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [state.serverId, state.currentPath]);

  return (
    <LayoutContext.Provider 
      value={{ 
        ...state,
        setHasChanges,
        setCurrentPath,
        setServerId,
        fetchSidebar,
        fetchServerSidebar,
        fetchPageLayout,
        saveChanges,
        revertChanges,
        resetToDefaults
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
