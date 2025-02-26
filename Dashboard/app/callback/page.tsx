"use client";

import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { handleDiscordCallback } from "../utils/auth";
import { useUser } from "../contexts/UserContext";
import LoadingScreen from "../components/LoadingScreen";

function CallbackContent() {
  return (
    <Suspense fallback={<LoadingScreen message="Loading..." />}>
      <CallbackHandler />
    </Suspense>
  );
}

function CallbackHandler() {
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
        setUser(data.user);
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

export default function CallbackPage() {
  return <CallbackContent />;
}
