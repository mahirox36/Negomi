import { ReactNode } from 'react';
import { UserProvider } from '@/contexts/UserContext';
import { LayoutProvider } from '../contexts/LayoutContext';
import { Toaster } from 'react-hot-toast';

interface RootProviderProps {
  children: ReactNode;
}

export function RootProvider({ children }: RootProviderProps) {
  return (
    <LayoutProvider>
      <UserProvider>
        <Toaster
          position="bottom-left"
          toastOptions={{
            style: {
              zIndex: 100,
              position: "relative",
              background: "rgba(23, 23, 23, 0.9)",
              color: "#fff",
              backdropFilter: "blur(8px)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
            },
          }}
        />
        {children}
      </UserProvider>
    </LayoutProvider>
  );
}