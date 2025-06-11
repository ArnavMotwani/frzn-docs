// frontend/pages/repos/[id]/chat.tsx

import React, { useEffect, useRef, useState } from 'react';
import { NextPage } from 'next';
import { useRouter } from 'next/router';
import toast, { Toaster } from 'react-hot-toast';

import { Repo } from '@/pages/index';

const ChatPage: NextPage = () => {
    const router = useRouter();
    const { isReady } = router;
    const { id } = router.query;
    const hasFetched = useRef(false);
    const [repo, setRepo] = useState<Repo | null>(null);

    useEffect(() => {
        if (!isReady) return;
        if (hasFetched.current) return;
        hasFetched.current = true;

        if (Array.isArray(id) || isNaN(Number(id))) {
            toast.error('Invalid repo ID');
            router.replace('/');
            return;
        }

        const repoId = Number(id);
        (async () => {
            try {
                const res = await fetch(`/api/repos/${repoId}`);
                if (!res.ok) {
                    const text = await res.text();
                    throw new Error(text || 'Failed to fetch repo details');
                }
                const data: Repo = await res.json();

                if (data.index_status === 'complete') {
                    setRepo(data);
                } else if (data.index_status === 'error') {
                    toast.error(
                        `Error indexing repo ${data.owner}/${data.name}: ${data.index_status}`,
                        { duration: 4000 }
                    );
                    router.replace('/');
                } else if (data.index_status === 'pending' || data.index_status === 'indexing') {
                    toast(
                        `Repo ${data.owner}/${data.name} is still being indexed, status: ${data.index_status}`,
                        { duration: 4000 }
                    );
                    router.replace('/');
                }
            } catch (error) {
                console.error('Error fetching repo details:', error);
            }
        })();
    }, [isReady, id, router]);

    return (
        <>
            <Toaster
                position="top-right"
                toastOptions={{
                    className: 'font-bold',
                    style: {
                        background: '#333',
                        color: '#F9FAFB',
                        fontSize: '1rem',
                        padding: '16px',
                        borderRadius: '20px',
                    },
                }}
            />
            <div className="flex flex-col items-center justify-center h-screen">
                <h1 className="text-2xl font-bold mb-4">Chat Page</h1>
                {repo ? (
                    <div className="text-center">
                        <p className="mb-2">Repo: {repo.owner}/{repo.name}</p>
                        <p className="mb-2">Index Status: {repo.index_status}</p>
                        <p className="mb-4">Description: {repo.description || 'No description available'}</p>
                    </div>
                ) : (
                    <p className="text-gray-500">Loading repo details...</p>
                )}
                <p className="mt-4 text-sm text-gray-500">
                    This page is under construction. Please check back later.
                </p>
                <button
                    className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    onClick={() => router.push('/')}
                >
                    Go Back to Home
                </button>
            </div>
        </>
    );
};

export default ChatPage;