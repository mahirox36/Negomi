"use client";

import { useParams } from "next/navigation";
import { useEffect, useState, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";

// Define the Button type
type Button = {
  icon?: string;
  text: string;
  subtext?: string;
  buttonText?: string;
  link: string;
};

type LayoutItem = {
  type: "header" | "cards";
  text: string;
  subtext?: string;
  icon?: string;
  buttons?: Button[];
};

export default function Overview() {
  const params = useParams();
  const [pageLayout, setPageLayout] = useState<LayoutItem[]>([]);
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  const fetchPageLayout = useCallback(async () => {
    if (!isLoading) return;

    try {
      const response = await fetch(`/api/v1/layout/settings/server/overview`, {
        cache: 'no-store'
      });
      const data = await response.json();
      setPageLayout(Array.isArray(data) ? data : data.layout || []);
    } catch (error) {
      console.error("Failed to fetch layout:", error);
      setPageLayout([]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  useEffect(() => {
    fetchPageLayout();
  }, [fetchPageLayout]);

  const renderHeader = useMemo(() => (item: LayoutItem, index: number) => (
    <div
      key={index}
      className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-lg rounded-2xl p-8 shadow-xl border border-white/10"
    >
      <div className="flex items-center gap-4">
        {item.icon && (
          <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-white/20 to-white/10 rounded-xl shadow-inner">
            <i
              className={`${item.icon} text-2xl text-white/90`}
            ></i>
          </div>
        )}
        <div>
          <h1 className="text-3xl font-bold text-white bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
            {item.text}
          </h1>
          <p className="text-lg text-white/70 mt-1">
            {item.subtext}
          </p>
        </div>
      </div>
    </div>
  ), []);

  const renderCards = useMemo(() => (item: LayoutItem, index: number) => (
    <div
      key={index}
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8"
    >
      {item.buttons?.map((button: Button, buttonIndex: number) => (
        <div
          key={buttonIndex}
          onClick={() =>
            router.push(
              `/dashboard/server/${params.id}/${button.link}`
            )
          }
          className="group relative overflow-hidden p-6 bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 cursor-pointer"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div className="relative">
            <div className="flex items-center gap-3 mb-4">
              {button.icon && (
                <div className="w-10 h-10 flex items-center justify-center bg-white/10 rounded-lg group-hover:scale-110 transition-transform duration-300">
                  <i className={`${button.icon} text-white/90`}></i>
                </div>
              )}
              <h3 className="text-xl text-white font-semibold">
                {button.text}
              </h3>
            </div>
            <p className="text-white/70 text-sm mb-4">
              {button.subtext}
            </p>
            {button.buttonText && (
              <span className="inline-flex items-center px-4 py-2 bg-white/10 rounded-lg text-sm text-white group-hover:bg-white/20 transition-colors">
                {button.buttonText}
                <i className="fas fa-arrow-right ml-2 group-hover:translate-x-1 transition-transform"></i>
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  ), [params.id, router]);

  return (
    <div className="space-y-6">
      {pageLayout?.map((item: LayoutItem, index: number) => {
        switch (item.type) {
          case "header":
            return renderHeader(item, index);
          case "cards":
            return renderCards(item, index);
          default:
            return null;
        }
      })}
    </div>
  );
}
