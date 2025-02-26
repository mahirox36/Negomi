'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { handleDiscordCallback } from '../utils/auth';

function CallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();

    useEffect(() => {
        const code = searchParams.get('code');
        if (!code) {
            router.push('/');
            return;
        }

        const processCallback = async () => {
            try {
                const data = await handleDiscordCallback(code);
                localStorage.setItem('user', JSON.stringify(data.user));
                localStorage.setItem('accessToken', data.accessToken);
                router.push('/');
            } catch (error) {
                console.error('Authentication failed:', error);
                router.push('/');
            }
        };

        processCallback();
    }, [router, searchParams]);

    return (
        <div className="text-white text-xl">Authenticating...</div>
    );
}

export default function CallbackPage() {
    return (
        <div className="min-h-screen flex items-center justify-center">
            <Suspense fallback={<div className="text-white text-xl">Loading...</div>}>
                <CallbackContent />
            </Suspense>
        </div>
    );
}
