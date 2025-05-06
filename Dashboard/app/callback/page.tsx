"use client";

import { Suspense } from "react";
import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useUser } from "../contexts/UserContext";
import LoadingScreen from "../components/LoadingScreen";
import axios from "axios";
import { debounce } from "lodash";

function ClientCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setUser } = useUser();
  const [error, setError] = useState<string | null>(null);

  const processCallback = useCallback(
    debounce(async (code: string) => {
      try {
        const response = await axios.post("/api/v1/auth/discord/callback", 
          { code }, 
          {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
            validateStatus: (status) => status < 500,
            timeout: 10000,
            withCredentials: true
          }
        );

        if (response.status !== 200) {
          throw new Error(response.data.detail || 'Authentication failed');
        }

        const { user, accessToken } = response.data;
        
        // Store access token in cookie
        document.cookie = `accessToken=${accessToken}; path=/; max-age=604800; SameSite=Strict`;
        
        setUser(user);
        router.push("/dashboard");
      } catch (error) {
        console.error("Authentication error:", error);
        if (axios.isAxiosError(error)) {
          setError(error.response?.data?.detail || error.message);
        } else {
          setError('An unexpected error occurred');
        }
        setTimeout(() => router.push("/"), 3000);
      }
    }, 500), // Debounce for 500ms
    [router, setUser]
  );

  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) {
      router.push("/");
      return;
    }

    processCallback(code);

    return () => {
      processCallback.cancel();
    };
  }, [searchParams, processCallback]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-red-500 text-xl mb-4">{error}</div>
        <div className="text-gray-400">Redirecting to home...</div>
      </div>
    );
  }

  return <LoadingScreen message="Authenticating..." />;
}

export default function CallbackPage() {
  return (
    <Suspense fallback={<LoadingScreen message="Loading..." />}>
      <ClientCallback />
    </Suspense>
  );
}
