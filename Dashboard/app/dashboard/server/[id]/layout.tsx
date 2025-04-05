import { ReactNode, Suspense } from "react";
import ServerLayoutClient from "./layout-client";
interface Params {
  id: string;
}

interface LayoutProps {
  children: ReactNode;
  params: Params;
}

export default function ServerLayout({ children, params }: LayoutProps) {
  const serverId = params.id;
  
  return (
    <Suspense fallback={null}>
      <ServerLayoutClient serverId={serverId}>{children}</ServerLayoutClient>
    </Suspense>
  );
}
