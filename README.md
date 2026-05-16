# MDUMENI Backend API
**AI agronomist for Zimbabwe — deployed on Render (free)**

This is the backend server for the MDUMENI mobile app.  
It runs all 4 AI engines and exposes them via a REST API.

Live docs once deployed: `https://mdumeni-api.onrender.com/docs`

---

## Deploy to Render — step by step

### Step 1 — Push this folder to GitHub

On your Windows machine, open PowerShell in this folder and run:

```
git init
git add .
git commit -m "Initial MDUMENI backend"
```

Then go to **github.com** → click **New repository** → name it `mdumeni-backend` → click **Create repository**.

Copy the commands GitHub shows you (they look like this):
```
git remote add origin https://github.com/euginebhebhe/mdumeni-backend.git
git branch -M main
git push -u origin main
```

Paste and run them in your PowerShell. Your code is now on GitHub.

---

### Step 2 — Create a Render account

Go to **render.com** → click **Get Started for Free** → sign up with your GitHub account.  
No credit card required.

---

### Step 3 — Deploy the API

1. In the Render dashboard, click **New** → **Web Service**
2. Click **Connect a repository** → select `mdumeni-backend`
3. Render auto-detects Python. Fill in these fields:
   - **Name:** `mdumeni-api`
   - **Region:** Oregon (closest to Zimbabwe)
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
   - **Instance Type:** Free
4. Click **Create Web Service**

Render builds and deploys in about 2 minutes.  
You will see a green **Live** badge when it is done.

---

### Step 4 — Get your live URL

Your API is live at:  
`https://mdumeni-api.onrender.com`  
(Render generates this URL automatically)

Test it by visiting:  
`https://mdumeni-api.onrender.com/health`

You should see:
```json
{"status": "ok", "engines": 4, "crops": 30}
```

Full interactive docs:  
`https://mdumeni-api.onrender.com/docs`

---

### Step 5 — Connect the mobile app

Open `mdumeni-app/src/services/api.ts` on your computer.  
Find this line:

```typescript
const BASE_URL = 'https://mdumeni-api.onrender.com';
```

Save the file. The app running in Expo Go will automatically reload and now call the real AI engines.

---

## API endpoints

| Endpoint | What it does |
|---|---|
| `GET /health` | Check if server is running |
| `POST /session` | **Main endpoint** — runs all 4 engines in one call |
| `POST /recommend` | Crop recommendations only |
| `POST /calendar` | Farming calendar for active crop |
| `POST /plan` | Financial planning |
| `POST /threats` | Active pest and disease threats |
| `POST /diagnose` | Symptom-based diagnosis |
| `GET /docs` | Interactive Swagger documentation |
| `POST /chat` | AI chat |


---

## Important note about the free tier

Render's free tier **spins down after 15 minutes of inactivity**.  
The first request after spin-down takes 30–60 seconds to respond.  
After that, all requests are fast.

For the demo and pilot this is fine.  
When you get institutional customers, upgrade to the $7/month paid tier for always-on performance.

---

## Auto-deploy on every push

Once connected to Render, every time you run `git push` from your computer,  
Render automatically rebuilds and redeploys in about 90 seconds.  
No manual steps needed.
