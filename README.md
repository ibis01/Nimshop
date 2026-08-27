## 🚀 Deployment Guide

NimShop is designed for secure, production-grade deployment. Follow these steps to deploy the frontend, backend, and database.

### 1. PostgreSQL Setup

Production requires PostgreSQL. Create a database and note the connection string.
_Do not use SQLite in production._

### 2. Backend Deployment (e.g., Railway, Render, VPS)

1. Set the following environment variables:
   - `DATABASE_URL`: Your PostgreSQL connection string.
   - `FRONTEND_URL`: The exact HTTPS URL of your deployed frontend (e.g., `https://nimshop.vercel.app`).
   - `NIMIQ_NETWORK`: `testnet` (or `mainnet` for production).
   - `NIMIQ_RPC_URL`: `https://rpc.testnet.nimiqwatch.com/`
2. Initialize the database schema (handled automatically by FastAPI lifespan, or run `python seed.py` once to seed initial products).
3. Verify the `/health` endpoint returns `{"status": "healthy"}`.

### 3. Frontend Deployment (e.g., Vercel, Netlify)

1. Set the following environment variable:
   - `VITE_API_URL`: The exact HTTPS URL of your deployed backend (e.g., `https://nimshop-api.railway.app`).
2. Run `npm run build` and deploy the `dist` folder.
3. Ensure the deployment serves over HTTPS (required for Nimiq Pay WebView).

### 4. Connecting Frontend and Backend

Ensure the `FRONTEND_URL` in the backend exactly matches the deployed frontend domain to satisfy strict CORS policies.

---

## ✅ Deployment Readiness Checklist

### Backend Deployment

- [ ] Configure `DATABASE_URL` (PostgreSQL)
- [ ] Configure `FRONTEND_URL` (Exact HTTPS frontend URL)
- [ ] Configure `NIMIQ_NETWORK`
- [ ] Configure `NIMIQ_RPC_URL`
- [ ] Initialize database and run `python seed.py`
- [ ] Confirm `GET /health` returns 200 OK

### Frontend Deployment

- [ ] Configure `VITE_API_URL` (Exact HTTPS backend URL)
- [ ] Build successfully (`npm run build`)
- [ ] Deploy HTTPS version
- [ ] Confirm API connectivity from deployed frontend

### Nimiq Validation (Manual)

- [ ] Open NimShop in supported Nimiq Pay / Mini App environment
- [ ] Connect wallet
- [ ] Create order via AI search
- [ ] Execute real test transaction
- [ ] Capture real `txHash`
- [ ] Verify backend transaction validation (`/api/orders/verify`)
- [ ] Confirm order status transitions `PENDING` → `PAID`
