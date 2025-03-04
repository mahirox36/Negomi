"use client";

import { ReactNode } from 'react';
import { useUser } from '../contexts/UserContext';
import LoadingScreen from './LoadingScreen';
import Navbar from './Navbar';
import Footer from './Footer';

interface PageWrapperProps {
  children: ReactNode;
  requireAuth?: boolean;
  loading?: boolean;
  loadingMessage?: string;
}

export default function PageWrapper({ 
  children, 
  requireAuth = false,
  loading = false,
  loadingMessage
}: PageWrapperProps) {
  const { user, isLoading } = useUser();

  if (isLoading || loading) {
    return <LoadingScreen message={loadingMessage} />;
  }

  if (requireAuth && !user) {
    window.location.href = '/';
    return <LoadingScreen message="Redirecting..." />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900">
      <Navbar />
      <main className="pt-16">
        {children}
      </main>
      <Footer />
    </div>
  );
}
