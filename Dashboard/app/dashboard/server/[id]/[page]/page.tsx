"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import LoadingScreen from "@/app/components/LoadingScreen";
import ServerLayout from "@/app/components/ServerLayout";
import { useLayout } from "@/providers/LayoutProvider";
import { LayoutItem } from "@/types/layout";
import Link from "next/link";
import axios from "axios";
import AccessDenied from "@/app/components/forbidden";

export default function ServerPage() {
  const params = useParams();
  const { pageLayout, fetchPageLayout } = useLayout();
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const checkAdminStatus = async () => {
      try {
        const response = await fetch(`/api/guilds/${params.id}/is_admin`, {
          method: 'POST',
          credentials: 'include',
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.detail || 'Failed to check admin status');
        }
        
        setIsAdmin(data.isAdmin);
      } catch (error) {
        console.error("Admin check error:", error);
        setIsAdmin(false);
        setError(error instanceof Error ? error.message : 'Failed to check permissions');
      }
    };

    checkAdminStatus();
    fetchPageLayout(params.page as string);
  }, [fetchPageLayout, params.id, params.page]);

  if (isAdmin === null) {
    return <LoadingScreen message="Checking Permissions" />;
  }

  if (!isAdmin) {
    return (
      <AccessDenied 
        error={new Error(error || "You do not have permission to view this page.")} 
        reset={() => window.location.reload()} 
      />
    );
  }

  if (!pageLayout) {
    return <LoadingScreen message="Loading Page" />;
  }

  const renderLayoutItem = (item: LayoutItem, index: number) => {
    switch (item.type) {
      case "header":
        return (
          <div key={index} className="bg-white/10 backdrop-blur-lg rounded-lg p-6">
            <h1 className="text-2xl font-bold text-white mb-2">{item.text}</h1>
            <p className="text-white/70 mb-8">{item.subtext}</p>
          </div>
        );
      case "cards":
        return (
          <div key={index} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {item.buttons?.map((button, buttonIndex) => (
              <Link
                key={buttonIndex}
                href={`/dashboard/server/${params.id}${button.link}`}
                className="block p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
              >
                <h3 className="text-white font-semibold mb-1">{button.text}</h3>
                <p className="text-white/60 text-sm">{button.subtext}</p>
              </Link>
            ))}
          </div>
        );
      case "panel":
        return (
          <div key={index} className="bg-white/5 rounded-lg p-6 mb-8">
            <div className="flex items-center gap-3 mb-4">
              {item.icon && <i className={`${item.icon} text-xl text-white/70`}></i>}
              <div>
                <h2 className="text-lg font-semibold text-white">{item.text}</h2>
                <p className="text-sm text-white/70">{item.subtext}</p>
              </div>
            </div>
            <div className="space-y-4">
              {item.settings?.map((setting: any, settingIndex: number) => (
                <div key={settingIndex} className="flex items-center justify-between">
                  <span className="text-white">{setting.name}</span>
                  {setting.type === "colour" && (
                    <div className="flex items-center gap-2">
                      <div
                        className="w-6 h-6 rounded border border-white/20"
                        style={{ backgroundColor: setting.value }}
                      />
                      <input
                        type="text"
                        value={setting.value}
                        className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white w-24"
                        onChange={() => {}} // Add your color change handler here
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <ServerLayout serverId={params.id as string}>
      <div className="space-y-6">
        {pageLayout.map((item, index) => renderLayoutItem(item, index))}
      </div>
    </ServerLayout>
  );
}
