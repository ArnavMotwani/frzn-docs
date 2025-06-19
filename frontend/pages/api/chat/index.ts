
// frontend/pages/api/chat/index.ts

import type { NextApiRequest, NextApiResponse } from "next";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export const config = {
    api: {
        bodyParser: false,
        responseLimit: false,
    },
};

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== "POST") {
        res.setHeader("Allow", ["POST"]);
        return res.status(405).end(`Method ${req.method} Not Allowed`);
    }

    const { repoId } = req.query;
    const rawBody: string = await new Promise((resolve, reject) => {
        let data = "";
        req.on("data", (chunk) => (data += chunk));
        req.on("end", () => resolve(data));
        req.on("error", reject);
    });

    let backendRes: Response;
    try {
        backendRes = await fetch(`${BACKEND_URL}/api/chat?repoId=${repoId}`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    rawBody,
        });
    } catch (err) {
        console.error("Proxy error:", err);
        return res.status(502).json({ error: "Backend unreachable" });
    }

    res.status(backendRes.status)
    res.setHeader("Content-Type", "text/plain; charset=utf-8")
    res.setHeader("x-vercel-ai-data-stream", "v1")

    const reader = backendRes.body!.getReader()
    try {
        while (true) {
            const { done, value } = await reader.read()
            if (done) break
            res.write(new TextDecoder().decode(value))
        }
    } finally {
        res.end()
    }
}