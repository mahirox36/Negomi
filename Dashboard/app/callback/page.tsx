"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { handleDiscordCallback } from "../utils/auth";
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
        const data = await handleDiscordCallback(code);
        setUser(data.user); // Use context instead of localStorage directly
        localStorage.setItem("accessToken", data.accessToken);
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
