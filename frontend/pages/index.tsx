// frontend/pages/index.tsx
import React, { useState } from 'react';
import { NextPage } from 'next';

import RepoSlashInput from '@/components/RepoSlashInput';
import RepoSlashCard from '@/components/RepoSlashCard';

const Home: NextPage = () => {
    const [owner, setOwner] = useState('');
    const [name, setName] = useState('');

    const repos = [
        { owner: 'facebook', name: 'react' },
        { owner: 'vercel', name: 'next.js' },
        { owner: 'tailwindlabs', name: 'tailwindcss' },
        { owner: 'nodejs', name: 'node' },
        { owner: 'python', name: 'cpython' },
        { owner: 'microsoft', name: 'typescript' },
    ];

    const handleIndexRepo = () => {
        // TODO: replace with your actual indexing logic
        console.log('Indexing repo:', { owner, name });
    };

    return (
        <div className="flex flex-col items-center min-h-screen p-8">
            <h1 className="text-6xl font-bold">frzn-docs</h1>
            <p className="mt-4 text-lg text-gray-500">
                Create documentation AI agent for your codebase
            </p>

            <p className="mt-8 text-sm text-gray-500">
                Enter your repo below
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
                    className="mt-4 px-6 py-2 block mx-auto rounded-lg border-3 border-black font-bold text-gray-700 hover:bg-gray-100"
                >
                    Index repo
                </button>
            </div>

            <p className="mt-12 text-sm text-gray-500">
                or choose a previously indexed project
            </p>

            <div className="mt-4 w-full max-w-4xl grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {repos.map((repo, idx) => (
                    <RepoSlashCard
                        key={idx}
                        repoOwner={repo.owner}
                        repoName={repo.name}
                        gradientFrom="#3B82F6"
                        gradientTo="#9333EA"
                        backgroundColor="#FFFFFF"
                        showBackground={true}
                        className="cursor-pointer"
                    />
                ))}
            </div>
        </div>
    );
};

export default Home;