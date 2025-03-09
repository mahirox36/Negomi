"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useUser } from "../contexts/UserContext";
import LoadingScreen from "../components/LoadingScreen";

export default function CallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setUser } = useUser();

  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) {
      router.push("/");
      return;
    }

    const processCallback = async () => {
      try {
        const response = await fetch("/api/auth/discord/callback", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ code }),
        });

        if (!response.ok) {
          throw new Error("Failed to authenticate");
        }

        const data = await response.json();
        setUser(data.user);
        router.push("/dashboard");
      } catch (error) {
        console.error("Authentication failed:", error);
        router.push("/");
      }
    };

    processCallback();
  }, [router, searchParams, setUser]);

  return <LoadingScreen message="Authenticating..." />;
}
