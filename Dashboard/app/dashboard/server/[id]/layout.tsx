import { ReactNode, Suspense } from "react";
import ServerLayoutClient from "./layout-client";
import { Metadata } from "next";
import { LayoutProvider } from "@/providers/LayoutProvider";

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

export default async function ServerLayout({ children, params }: LayoutProps) {
  const resolvedParams = await params;
  const serverId = resolvedParams?.id ?? "";

  return (
    <div className="min-h-screen relative">
      <Suspense>
        <LayoutProvider>
          <ServerLayoutClient serverId={serverId}>{children}</ServerLayoutClient>
        </LayoutProvider>
      </Suspense>
    </div>
  );
}
