# Step-by-Step Vercel Deployment Guide

Deploying a full-stack application (Next.js Frontend + Python FastAPI Backend) requires understanding how modern cloud hosting works. **Vercel** is the absolute best place to host your Next.js frontend, as they literally created the framework!

However, because your backend is a heavy Python AI agent (using Docker, Pandas, and LangGraph), deploying the backend to Vercel is generally not recommended due to Vercel's strict 250MB serverless function limits.

Here is the absolute simplest, step-by-step guide to deploying your **Frontend to Vercel**, and how to handle the backend.

---

## Phase 1: Prepare Your Repository
Before deploying, make sure your code is pushed to a Git repository.
1. Go to [GitHub.com](https://github.com) and ensure your `python-equitie` repository is fully pushed and up to date on your main branch.
2. Ensure you have no uncommitted changes locally.

## Phase 2: Deploying the Frontend to Vercel

Vercel makes deploying Next.js effortless.

1. **Sign in to Vercel:**
   - Go to [vercel.com](https://vercel.com) and sign up using your **GitHub account**. This links your repositories automatically.

2. **Import Your Project:**
   - Click the **"Add New..."** button in the top right corner and select **"Project"**.
   - You will see a list of your GitHub repositories. Find your `python-equitie` repository and click **"Import"**.

3. **Configure the Build Settings (CRITICAL STEP):**
   Since your Next.js code is not in the root folder, you must tell Vercel where to look!
   - **Project Name:** You can leave it as default or name it `equitie-frontend`.
   - **Framework Preset:** Vercel will auto-detect **Next.js**.
   - **Root Directory:** Click "Edit" and select the **`frontend`** folder.
   - **Build Command:** Leave as default (`next build`).
   - **Output Directory:** Leave as default (`.next`).

4. **Deploy:**
   - Click the big blue **"Deploy"** button.
   - Vercel will now clone your repo, install NPM packages, and build your Next.js app.
   - In about 1-2 minutes, you will get a beautiful success screen with a live URL (e.g., `https://equitie-frontend.vercel.app`).

---

## Phase 3: Connecting the Python Backend

Right now, your deployed Vercel frontend is trying to talk to `/api/v1/investors`. In your local Docker setup, NGINX routes this to your FastAPI backend. On Vercel, you don't have NGINX, so you need a place to host your Python backend.

### Where to host the Python Backend?
For beginner developers, I highly recommend **Render.com** or **Railway.app**. They natively support Docker and are as easy to use as Vercel.

**Steps for Render (Example):**
1. Go to [render.com](https://render.com) and sign in with GitHub.
2. Click **New +** -> **Web Service**.
3. Select your `python-equitie` repository.
4. Render will automatically detect your `Dockerfile`.
5. Under Environment Variables, add your AI keys:
   - `OPENROUTER_API_KEY=your_key_here`
   - `LLM_OPENROUTER_MODELS=...`
6. Click **Create Web Service**. Render will build and deploy your Docker container and give you a URL (e.g., `https://equitie-backend.onrender.com`).

### Hooking them together:
Once your backend is live on Render, you just need to tell your Vercel frontend to talk to it!

1. In your Next.js frontend code, edit the `fetch` calls or create an environment variable (`NEXT_PUBLIC_API_URL`).
2. Example: Change `fetch("/api/v1/investors")` to `fetch("https://equitie-backend.onrender.com/api/v1/investors")`.
3. Push those changes to GitHub. Vercel will **automatically** rebuild and redeploy your frontend, and your full-stack app will be live globally!

---

## Summary Checklist
- [x] Push code to GitHub
- [ ] Import `python-equitie` to Vercel
- [ ] Set Vercel Root Directory to `frontend`
- [ ] Click Deploy on Vercel
- [ ] Deploy backend `Dockerfile` to Render or Railway
- [ ] Update frontend fetch URLs to point to the new backend URL
