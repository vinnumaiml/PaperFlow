# PaperFlow Deployment Guide

PaperFlow is a full-stack document utility platform consisting of:
1. **Frontend**: Next.js 16 (App Router), React 19, Tailwind CSS v4, Lucide Icons.
2. **Backend**: Python FastAPI document-processing engine with PyMuPDF, pikepdf, pypdf, ReportLab, and OCR utilities.

Because PaperFlow includes a real server-side Python engine, publishing it requires hosting both the frontend UI and the processing backend.

---

## Option 1 — Deploying to Vercel (Frontend) + Render (Backend) [Recommended]

### Step 1: Deploy Backend to Render (Free)
1. Go to [Render.com](https://render.com) and sign in with your GitHub account (`vinnumaiml`).
2. Click **New +** > **Web Service**.
3. Select your repository: `PaperFlow`.
4. Configure:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**. Once deployed, copy your backend URL (e.g., `https://paperflow-backend.onrender.com`).

### Step 2: Deploy Frontend to Vercel (Free)
1. Go to [Vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **Add New...** > **Project** and select `vinnumaiml/PaperFlow`.
3. In the project setup:
   - The included `vercel.json` and root `package.json` will automatically configure Next.js.
   - Under **Environment Variables**, add:
     - `NEXT_PUBLIC_API_URL` = `https://your-backend-url.onrender.com`
4. Click **Deploy**. Your site will be live on a `*.vercel.app` domain with SSL!

---

## Option 2 — 1-Click Full-Stack Deploy on Render via Blueprint

PaperFlow includes a ready-to-use [`render.yaml`](./render.yaml) specification:

1. Go to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** > **Blueprint**.
3. Select `vinnumaiml/PaperFlow`.
4. Render will automatically detect the backend and frontend services and wire their URLs together.
5. Click **Apply**. Both services will spin up automatically!

---

## Option 3 — Deploying to Netlify (Frontend)

PaperFlow includes pre-configured [`netlify.toml`](./netlify.toml) and [`frontend/public/_redirects`](./frontend/public/_redirects) files to ensure seamless deployment without "Page Not Found" errors:

### How to Deploy on Netlify:
1. Go to [Netlify.com](https://app.netlify.com/) and click **Add new site** > **Import an existing project**.
2. Connect your GitHub account and select **`vinnumaiml/PaperFlow`**.
3. Netlify will automatically detect the settings from `netlify.toml`:
   - **Base directory**: `.` (or `frontend`)
   - **Build command**: `cd frontend && npm install && npm run build` (or `npm run build`)
   - **Publish directory**: `frontend/out` (or `out`)
4. Under **Environment variables**, add:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend-url.onrender.com` (your live FastAPI backend URL)
5. Click **Deploy PaperFlow**.
6. If you already have an existing site on Netlify showing "Page Not Found":
   - Go to **Deploys** in your Netlify site dashboard.
   - Click **Trigger deploy** > **Clear cache and deploy site**.

---

## Option 4 — GitHub Pages (Frontend Static UI)

To publish the frontend directly on GitHub Pages using the included GitHub Actions workflow:

1. Open your repository on GitHub: [https://github.com/vinnumaiml/PaperFlow](https://github.com/vinnumaiml/PaperFlow)
2. Go to **Settings** > **Pages** (in the left sidebar).
3. Under **Build and deployment** > **Source**, change from *"Deploy from a branch"* to **GitHub Actions**.
4. That's it! The workflow [`.github/workflows/deploy-pages.yml`](./.github/workflows/deploy-pages.yml) will build Next.js and publish the website to:
   ```
   https://vinnumaiml.github.io/PaperFlow/
   ```
5. To connect live backend processing to your GitHub Pages site, set the GitHub secret/variable `NEXT_PUBLIC_API_URL` to your live hosted backend URL.

---

## Option 5 — Self-Hosted via Docker

To run both services together on any VPS, cloud server, or local machine:

```bash
# Clone the repository
git clone https://github.com/vinnumaiml/PaperFlow.git
cd PaperFlow

# Copy environment template
cp .env.example .env

# Build and start all services
docker compose up -d --build
```

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Interactive API Docs**: `http://localhost:8000/docs`
