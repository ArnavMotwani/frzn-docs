import type { NextApiRequest, NextApiResponse } from 'next';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method === 'GET') {
        try {
            const response = await fetch(`${BACKEND_URL}/api/repos`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });

            if (!response.ok) {
                const text = await response.text();
                return res
                    .status(response.status)
                    .json({ error: text || 'Backend error' });
            }

            const data = await response.json();
            return res.status(200).json(data);

        } catch (err: any) {
            console.error('Error fetching /repos:', err);
            return res
                .status(502)
                .json({ error: 'Unable to reach backend. Check if backend is running.' });
        }
    } else if (req.method === 'POST') {
        try {
            const { owner, name } = req.body;

            if (!owner || !name) {
                return res.status(400).json({ error: 'Owner and name are required' });
            }

            const response = await fetch(`${BACKEND_URL}/api/repos`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ owner, name }),
            });

            if (!response.ok) {
                const text = await response.text();
                return res
                    .status(response.status)
                    .json({ error: text || 'Backend error' });
            }

            const data = await response.json();
            return res.status(201).json(data);
        } catch (err: any) {
            console.error('Error handling POST /repos:', err);
            return res.status(500).json({ error: 'Internal server error' });
        }
    }

    res.setHeader('Allow', ['GET']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
}