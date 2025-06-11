// frontend/pages/index.tsx
import React, { useEffect, useState } from 'react';
import { NextPage } from 'next';
import { useRouter } from 'next/router';
import toast, { Toaster } from 'react-hot-toast';

import RepoSlashInput from '@/components/RepoSlashInput';
import RepoSlashCard from '@/components/RepoSlashCard';

export interface Repo {
    id: number;
    owner: string;
    name: string;
    full_name: string;
    description: string | null;
    default_branch: string;
    html_url: string | null;
    clone_url: string | null;
    indexed_at: string;
    index_status: "pending" | "indexing" | "complete" | "error";
}

const Home: NextPage = () => {
    const router = useRouter();

    const [owner, setOwner] = useState('');
    const [name, setName] = useState('');
    const [repos, setRepos] = useState<Repo[]>([]);

    const handleIndexRepo = () => {
        const trimmedOwner = owner.trim();
        const trimmedName = name.trim();

        const createRepo = async () => {
            try {
                const response = await fetch('/api/repos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ owner: trimmedOwner, name: trimmedName }),
                });

                if (!response.ok) {
                    const text = await response.text();
                    throw new Error(text || 'Failed to index repo');
                }

                const data: Repo = await response.json();
                setRepos((prev) => [...prev, data]);
                setOwner('');
                setName('');
            } catch (error) {
                console.error('Error indexing repo:', error);
            }
        }
        if (trimmedOwner && trimmedName) {
            createRepo();
            toast(`Cloning and indexing ${trimmedOwner} / ${trimmedName}`, {
                duration: 4000,
            });
        } else {
            toast.error('Owner and repo cannot be empty');
        }
    };

    const handleDeleteRepo = async (repoId: number) => {
        try {
            const response = await fetch(`/api/repos/${repoId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
            });
            if (!response.ok) {
                const text = await response.text();
                throw new Error(text || 'Failed to delete repo');
            }
            setRepos((prev) => prev.filter(repo => repo.id !== repoId));
            toast.success('Repo deleted successfully');
        } catch (error) {
            console.error('Error deleting repo:', error);
        }
    }

    const handleRepoClick = async (repoId: number) => {
        router.push(`/repos/${repoId}/chat`);
    };

    useEffect(() => {
        const getRepos = async () => {
            try {
                const response = await fetch('/api/repos');
                if (!response.ok) {
                    throw new Error('Failed to fetch repos');
                }
                const data: Repo[] = await response.json();
                setRepos(data);
            } catch (error) {
                console.error('Error fetching repos:', error);
            }
        };
        getRepos();
    }, []);

    return (
        <>
            <Toaster
                position="top-right"
                reverseOrder={false}
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
            <div className="flex flex-col items-center min-h-screen p-8">
                <h1 className="text-6xl font-bold">frzn-docs</h1>
                <p className="mt-4 text-lg text-gray-500">
                    Create documentation AI agent for your codebase
                </p>

                <p className="mt-8 text-sm text-gray-500">
                    Enter your GitHub repo below
                </p>

                <div className="mt-4 w-full max-w-2xl">
                    <RepoSlashInput
                        repoOwner={owner}
                        repoName={name}
                        gradientFrom="#3B82F6"
                        gradientTo="#9333EA"
                        backgroundColor="#FFFFFF"
                        placeholderOwner="owner"
                        placeholderName="repo"
                        onOwnerChange={setOwner}
                        onNameChange={setName}
                        className="w-full"
                        height="72px"
                        fontSize="1.75rem"
                        fontWeight={700}
                    />

                    <button
                        onClick={handleIndexRepo}
                        className="mt-4 px-6 py-2 block mx-auto rounded-lg border-3 border-black font-bold text-gray-700 hover:bg-gray-100 cursor-pointer"
                    >
                        Index repo
                    </button>
                </div>

                <p className="mt-12 text-sm text-gray-500">
                    or choose a previously indexed project
                </p>

                <div className="mt-4 w-full max-w-4xl grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                    {repos.map((repo) => (
                        <RepoSlashCard
                            key={repo.id}
                            repoOwner={repo.owner}
                            repoName={repo.name}
                            gradientFrom={repo.index_status === "error" ? "#F87171" : "#3B82F6"}
                            gradientTo={repo.index_status === "error"   ? "#B91C1C" : "#9333EA"}
                            backgroundColor={repo.index_status === "error" ? "rgb(255, 236, 236)" : "rgb(219, 232, 251)"}
                            showBackground
                            className="cursor-pointer"
                            onClick={() => handleRepoClick(repo.id)}
                            onTrashClick={() => handleDeleteRepo(repo.id)}
                        />
                    ))}
                </div>
            </div>
        </>
    );
};

export default Home;