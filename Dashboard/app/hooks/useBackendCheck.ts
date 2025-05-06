import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export function useBackendCheck(requireOwner = false) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const checkBackend = async () => {
      // Skip check for home page
      if (pathname === '/') {
        setLoading(false);
        return;
      }

      try {
        const healthCheck = await fetch('/api/v1/bot/health', {
              method: 'GET',
              headers: {
'Accept': 'application/json',
          }
        });

        if (!healthCheck.ok) {
          throw new Error('Backend is offline');
        }

        if (requireOwner) {
          const ownerCheck = await fetch('/api/v1/admin/is_owner', {
            credentials: 'include'
          });
          
          if (!ownerCheck.ok) {
            throw new Error('Unauthorized');
          }

          const data = await ownerCheck.json();
          if (!data.is_owner) {
            throw new Error('Unauthorized');
          }
        }

        setLoading(false);
        setError(null);
      } catch (error) {
        setError(error instanceof Error ? error.message : 'An error occurred');
        setLoading(false);
        if (pathname !== '/') {
          router.push('/error');
        }
      }
    };

    checkBackend();
  }, [router, requireOwner, pathname]);

  return { loading, error };
}
