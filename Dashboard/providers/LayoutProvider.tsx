"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
} from "react";
import { SidebarLayout, LayoutItem } from "../types/layout";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";

interface LayoutState {
  sidebar: SidebarLayout | null;
  serverSidebar: SidebarLayout | null;
  pageLayout: LayoutItem[] | null;
  isLoading: boolean;
  hasChanges: boolean;
  currentPath: string | null;
  serverId: string | null;
  isAdmin: boolean;
  disableProviderSave?: boolean;
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
  setDisableProviderSave: (value: boolean) => void;
  setLoading: (value: boolean) => void;
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
    serverId: null,
    isAdmin: false,
  });

  const router = useRouter();
  const fetchingRef = useRef<FetchState>({});
  const layoutCacheRef = useRef<{ [key: string]: LayoutItem[] }>({});

  const setHasChanges = useCallback((value: boolean) => {
    setState((prev) => ({ ...prev, hasChanges: value }));
  }, []);

  const setCurrentPath = useCallback((path: string) => {
    setState((prev) => ({ ...prev, currentPath: path }));
  }, []);

  const checkAdminPermission = useCallback(
    async (serverId: string) => {
      try {
        const userResponse = await fetch("/api/v1/auth/user", {
          credentials: "include",
        });

        if (!userResponse.ok) {
          router.push("/api/v1/auth/discord/login");
          return false;
        }

        const response = await fetch(`/api/v1/guilds/${serverId}/is_admin`, {
          method: "POST",
          credentials: "include",
        });

        if (!response.ok) {
          router.push("/dashboard");
          setState((prev) => ({ ...prev, isAdmin: false }));
          toast.error("You need admin permissions to access this");
          return false;
        }

        setState((prev) => ({ ...prev, isAdmin: true }));
        return true;
      } catch (error) {
        setState((prev) => ({ ...prev, isAdmin: false }));
        toast.error("Failed to verify permissions");
        return false;
      }
    },
    [router]
  );

  const setServerId = useCallback(
    async (id: string) => {
      if (await checkAdminPermission(id)) {
        setState((prev) => ({ ...prev, serverId: id }));
      }
    },
    [checkAdminPermission]
  );

  const fetchSidebar = useCallback(async () => {
    if (state.sidebar || fetchingRef.current.sidebar) return;

    try {
      fetchingRef.current.sidebar = true;
      const response = await fetch("/api/v1/layout/settings/sidebar");
      if (!response.ok) throw new Error("Failed to fetch sidebar");
      const data = await response.json();
      setState((prev) => ({ ...prev, sidebar: data }));
    } catch (error) {
      console.error("Error fetching sidebar:", error);
      toast.error("Failed to load sidebar");
    } finally {
      fetchingRef.current.sidebar = false;
    }
  }, [state.sidebar]);

  const fetchServerSidebar = useCallback(async () => {
    if (
      !state.serverId ||
      !state.isAdmin ||
      state.serverSidebar ||
      fetchingRef.current.serverSidebar
    )
      return;

    try {
      fetchingRef.current.serverSidebar = true;
      const response = await fetch("/api/v1/layout/settings/server/sidebar");
      if (!response.ok) throw new Error("Failed to fetch server sidebar");
      const data = await response.json();
      setState((prev) => ({ ...prev, serverSidebar: data }));
    } catch (error) {
      console.error("Error fetching server sidebar:", error);
      toast.error("Failed to load server sidebar");
    } finally {
      fetchingRef.current.serverSidebar = false;
    }
  }, [state.serverSidebar, state.serverId, state.isAdmin]);

  const fetchPageLayout = useCallback(
    async (page: string) => {
      if (!state.serverId || !state.isAdmin) return;
      const fetchKey = `page_${page}`;

      if (layoutCacheRef.current[page]) {
        setState((prev) => ({
          ...prev,
          pageLayout: layoutCacheRef.current[page],
        }));
        return;
      }

      if (fetchingRef.current[fetchKey]) return;

      try {
        fetchingRef.current[fetchKey] = true;
        setState((prev) => ({ ...prev, isLoading: true }));

        const response = await fetch(`/api/v1/layout/settings/server/${page}`);
        if (!response.ok) throw new Error("Failed to fetch page layout");
        const data = await response.json();

        layoutCacheRef.current[page] = data;
        setState((prev) => ({
          ...prev,
          pageLayout: data,
          isLoading: false,
        }));
      } catch (error) {
        console.error("Error fetching page layout:", error);
        setState((prev) => ({ ...prev, pageLayout: null, isLoading: false }));
        toast.error("Failed to load page layout");
      } finally {
        fetchingRef.current[fetchKey] = false;
      }
    },
    [state.serverId, state.isAdmin]
  );

  const saveChanges = useCallback(async () => {
    if (
      !state.hasChanges ||
      !state.serverId ||
      !state.currentPath ||
      !state.isAdmin
    )
      return;

    if (state.disableProviderSave) {
      window.dispatchEvent(new CustomEvent("getUnsavedSettings"));
      return;
    }

    setState((prev) => ({ ...prev, isLoading: true }));
    toast.loading("Saving changes...");

    try {
      const settingsData: any = await new Promise((resolve) => {
        const temp: any = {};
        window.dispatchEvent(
          new CustomEvent("getUnsavedSettings", {
            detail: {
              callback: (settings: any) => {
                Object.assign(temp, settings);
                resolve(temp);
              },
            },
          })
        );
      });

      const response = await fetch(
        `/api/v1/guilds/${state.serverId}/settings/${state.currentPath}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(settingsData),
        }
      );

      if (!response.ok) throw new Error("Failed to save changes");

      setHasChanges(false);
      toast.dismiss();
    } catch (error) {
      console.error("Error saving changes:", error);
      toast.error("Failed to save changes");
    } finally {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  }, [
    state.hasChanges,
    state.serverId,
    state.currentPath,
    state.isAdmin,
    state.disableProviderSave,
    setHasChanges,
  ]);

  const revertChanges = useCallback(() => {
    if (!state.hasChanges) return;
    window.dispatchEvent(new CustomEvent("revertChanges"));
    setHasChanges(false);
    toast.success("Changes reverted");
  }, [state.hasChanges, setHasChanges]);

  const resetToDefaults = useCallback(async () => {
    if (!state.serverId || !state.currentPath || !state.isAdmin) return;

    try {
      setState((prev) => ({ ...prev, isLoading: true }));
      const response = await fetch(
        `/api/v1/guilds/${state.serverId}/settings/${state.currentPath}`,
        {
          method: "DELETE",
          credentials: "include",
        }
      );
      if (!response.ok) throw new Error("Failed to reset settings");

      window.dispatchEvent(new CustomEvent("settingsReset"));
      toast.success("Settings reset to defaults");
    } catch (error) {
      console.error("Error resetting settings:", error);
      toast.error("Failed to reset settings");
    } finally {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  }, [state.serverId, state.currentPath, state.isAdmin]);

  const setDisableProviderSave = useCallback((value: boolean) => {
    setState((prev) => ({ ...prev, disableProviderSave: value }));
  }, []);

  const setLoading = useCallback((value: boolean) => {
    setState((prev) => ({ ...prev, isLoading: value }));
  }, []);

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
        resetToDefaults,
        setDisableProviderSave,
        setLoading,
      }}
    >
      {children}
    </LayoutContext.Provider>
  );
}

export function useLayout() {
  const context = useContext(LayoutContext);
  if (!context)
    throw new Error("useLayout must be used within a LayoutProvider");
  return context;
}
