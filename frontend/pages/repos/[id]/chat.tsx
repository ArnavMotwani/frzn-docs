// frontend/pages/repos/[id]/chat.tsx

import React, { useEffect, useRef, useState } from 'react';
import { NextPage } from 'next';
import { useRouter } from 'next/router';
import toast, { Toaster } from 'react-hot-toast';
import { X } from 'lucide-react';
import { AssistantRuntimeProvider } from '@assistant-ui/react';
import { useChatRuntime } from '@assistant-ui/react-ai-sdk';
import { Thread } from '@/components/assistant-ui/thread';
import { ThreadList } from '@/components/assistant-ui/thread-list';
import { Repo } from '@/pages/index';

const ChatPage: NextPage = () => {
    const router = useRouter();
    const { isReady } = router;
    const { id } = router.query;
    const hasFetched = useRef(false);
    const [repo, setRepo] = useState<Repo | null>(null);

    const runtime = useChatRuntime({
        api: "/api/chat",
    });

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

            <div className="relative flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
                <button
                    aria-label="Close chat"
                    onClick={() => router.push('/')}
                    className="absolute top-6 right-6 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
                >
                    <X className="w-6 h-6 text-gray-600 dark:text-gray-300" />
                </button>

                {repo && (
                    <h1 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-100">
                        {repo.owner}/{repo.name}
                    </h1>
                )}

                <div className="w-full max-w-7xl bg-white dark:bg-gray-800 rounded-2xl shadow-md overflow-hidden flex h-[80vh]">
                    <AssistantRuntimeProvider runtime={runtime}>
                        <div className="grid grid-cols-[250px_1fr] gap-4 p-6 flex-1 h-full">
                            <ThreadList />
                            <Thread />
                        </div>
                    </AssistantRuntimeProvider>
                </div>
            </div>
        </>
    );
};

export default ChatPage;