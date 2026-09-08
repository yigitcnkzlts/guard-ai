# GUARD AI dashboard

Local development:

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000

The dashboard talks to GUARD backend at `NEXT_PUBLIC_GUARD_API_URL` (default `http://localhost:8001`).
