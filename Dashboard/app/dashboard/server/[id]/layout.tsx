import { ReactNode, Suspense } from "react";
import ServerLayoutClient from "./layout-client";
import { Metadata } from "next";

interface Params {
  id: string;
}

interface LayoutProps {
  children: ReactNode;
  params: Params;
}

export const metadata: Metadata = {
  title: "Server Dashboard | Negomi",
  description: "Manage your Discord server settings and view analytics",
};

export default function ServerLayout({ children, params }: LayoutProps) {
  const serverId = params?.id ?? "";

  return (
    <div className="min-h-screen relative">
      <Suspense fallback={null}>
        <ServerLayoutClient serverId={serverId}>{children}</ServerLayoutClient>
      </Suspense>
    </div>
  );
}
