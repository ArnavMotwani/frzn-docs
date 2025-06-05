import type { NextApiRequest, NextApiResponse } from 'next';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method === 'GET') {
        try {
            const { id } = req.query;

            if (!id || typeof id !== 'string') {
                res.status(400).json({ error: 'Invalid repository ID' });
                return;
            }

            const response = await fetch(`${BACKEND_URL}/api/repos/${id}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });

            if (!response.ok) {
                const text = await response.text();
                res.status(response.status).json({ error: text || 'Backend error' });
                return;
            }

            const data = await response.json();
            res.status(200).json(data);
            return;

        } catch (err: any) {
            console.error('Error fetching /repos/[id]:', err);
            res.status(502).json({ error: 'Unable to reach backend. Check if backend is running.' });
            return;
        }
    } else if (req.method === 'DELETE') {
        try {
            const { id } = req.query;

            if (!id || typeof id !== 'string') {
                res.status(400).json({ error: 'Invalid repository ID' });
                return;
            }

            const response = await fetch(`${BACKEND_URL}/api/repos/${id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
            });

            if (!response.ok) {
                const text = await response.text();
                res.status(response.status).json({ error: text || 'Backend error' });
                return;
            }

            res.status(204).end();
            return;
        } catch (err: any) {
            console.error('Error handling DELETE /repos/[id]:', err);
            res.status(500).json({ error: 'Internal server error' });
            return;
        }
    }
    res.setHeader('Allow', ['GET', 'DELETE']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
    return;
}