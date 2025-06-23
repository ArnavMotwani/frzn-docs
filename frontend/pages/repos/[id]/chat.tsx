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
import {
    Card,
    CardHeader,
    CardTitle,
    CardAction,
} from '@/components/ui/card';

const ChatPage: NextPage = () => {
    const router = useRouter();
    const { isReady } = router;
    const { id } = router.query;
    const hasFetched = useRef(false);
    const [repo, setRepo] = useState<Repo | null>(null);

    const runtime = useChatRuntime({
        api: `/api/chat?repoId=${id}`,
    });

    useEffect(() => {
        if (!isReady || hasFetched.current) return;
        hasFetched.current = true;

        if (Array.isArray(id) || isNaN(Number(id))) {
            toast.error('Invalid repo ID');
            router.replace('/');
            return;
        }

        (async () => {
            try {
                const res = await fetch(`/api/repos/${Number(id)}`);
                if (!res.ok) {
                    const text = await res.text();
                    throw new Error(text || 'Failed to fetch repo details');
                }

                const data: Repo = await res.json();
                switch (data.index_status) {
                    case 'complete':
                        setRepo(data);
                        break;
                    case 'error':
                        toast.error(
                            `Error indexing ${data.owner}/${data.name}, status: ${data.index_status}`,
                            { duration: 4000 }
                        );
                        router.replace('/');
                        break;
                    default:
                        toast(
                            `${data.owner}/${data.name} is ${data.index_status}, please try again shortly.`,
                            { duration: 4000 }
                        );
                        router.replace('/');
                }
            } catch (err) {
                console.error('Fetch repo error:', err);
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

            <div className="flex flex-col min-h-screen
                            bg-gradient-to-b from-gray-50 to-white
                            dark:from-gray-900 dark:to-gray-800">
                <div className="flex justify-center px-6 pt-6">
                    <div className="w-full max-w-screen-3xl">
                        <Card className="
                            gap-0 py-0
                            bg-gradient-to-r from-blue-500 to-purple-600
                            text-white shadow-xl
                            mb-6
                        ">
                            <CardHeader className="px-6 py-2 flex items-center justify-between">
                                <CardTitle className="text-2xl leading-tight">
                                    {repo ? `${repo.owner}/${repo.name}` : 'Loading...'}
                                </CardTitle>
                                <CardAction>
                                    <button
                                        aria-label="Close chat"
                                        onClick={() => router.push('/')}
                                        className="p-2 rounded-full hover:bg-white/20 transition"
                                    >
                                        <X className="w-6 h-6 text-white" />
                                    </button>
                                </CardAction>
                            </CardHeader>
                        </Card>
                    </div>
                </div>

                <main className="flex-1 flex justify-center px-6 pb-6">
                    <div className="
                        w-full max-w-screen-3xl flex flex-1
                        bg-white/90 dark:bg-gray-800/90
                        backdrop-blur-sm
                        rounded-2xl
                        shadow-2xl
                        ring-1 ring-gray-200 dark:ring-gray-700
                        overflow-hidden
                    ">
                        <AssistantRuntimeProvider runtime={runtime}>
                            <aside className="
                                hidden md:block w-64
                                bg-gray-100 dark:bg-gray-700
                                p-6
                                overflow-auto
                            ">
                                <ThreadList />
                            </aside>

                            <section className="flex-1 flex flex-col">
                                <div className="flex-1 overflow-auto p-6">
                                    <Thread />
                                </div>
                            </section>
                        </AssistantRuntimeProvider>
                    </div>
                </main>
            </div>
        </>
    );
};

export default ChatPage;