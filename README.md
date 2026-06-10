# MDUMENI Backend API
**AI agronomist for Zimbabwe - deployed on Railway**

This is the backend server for the MDUMENI mobile app.  
It runs all 4 AI engines and exposes them via a REST API.

Live docs once deployed: `https://mdumeni-api-production.up.railway.app/docs`

---

## Deploy to Railway - step by step

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

### Step 2 - Create a Railway account

Go to **railway.com** and sign up with your GitHub account.

---

### Step 3 - Deploy the API

1. In the Railway dashboard, click **New Project**
2. Click **Connect a repository** → select `mdumeni-backend`
3. Railway auto-detects Python with Nixpacks. Confirm these settings:
   - **Name:** `mdumeni-api`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
4. Add the required environment variables in Railway
5. Deploy the service

Railway builds and deploys from the connected GitHub repository.

---

### Step 4 — Get your live URL

Your API is live at:  
`https://mdumeni-api-production.up.railway.app`

Test it by visiting:  
`https://mdumeni-api-production.up.railway.app/health`

You should see:
```json
{"status": "ok", "engines": 4, "crops": 30}
```

Full interactive docs:  
`https://mdumeni-api-production.up.railway.app/docs`

---

### Step 5 — Connect the mobile app

Open `mdumeni-app/src/services/api.ts` on your computer.  
Find this line:

```typescript
const BASE_URL = 'https://mdumeni-api-production.up.railway.app';
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

Railway hosts this API at the production URL above. Review your Railway plan limits before a public launch or pilot.

For the demo and pilot this is fine.  
When you get institutional customers, upgrade to the $7/month paid tier for always-on performance.

---

## Auto-deploy on every push

Once connected to Railway, every time you run `git push` from your computer,  
Railway automatically rebuilds and redeploys.  
No manual steps needed.
