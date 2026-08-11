# MDUMENI Backend API
**AI agronomist for Zimbabwe - deployed on Cloudflare Workers**

This is the backend server for the MDUMENI mobile app.  
It runs all 4 AI engines and exposes them via a REST API.

Live docs: `https://mdumeni-backend.eugineeuman.workers.dev/docs`

---

## Deploy to Cloudflare Workers

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

### Step 2 - Configure Cloudflare Workers

Create or select the Worker that serves this API, then configure its deployment from your Cloudflare dashboard or CI workflow.

---

### Step 3 - Deploy the API

1. Deploy the Worker using your configured Cloudflare workflow.
2. Add the required environment variables as Worker secrets or environment variables.
3. Deploy the service and confirm the Worker route is active.

The production Worker is available at the URL below.

---

### Step 4 — Get your live URL

Your API is live at:  
`https://mdumeni-backend.eugineeuman.workers.dev`

Test it by visiting:  
`https://mdumeni-backend.eugineeuman.workers.dev/health`

You should see:
```json
{"status": "ok", "engines": 4, "crops": 30}
```

Full interactive docs:  
`https://mdumeni-backend.eugineeuman.workers.dev/docs`

---

### Step 5 — Connect the mobile app

Open `mdumeni-app/src/services/api.ts` on your computer.  
Find this line:

```typescript
const BASE_URL = 'https://mdumeni-backend.eugineeuman.workers.dev';
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

Cloudflare Workers hosts this API at the production URL above. Review your Cloudflare plan limits before a public launch or pilot.

For the demo and pilot this is fine.  
When you get institutional customers, upgrade to the $7/month paid tier for always-on performance.

---

## Auto-deploy on every push

Deploy updates through your configured Cloudflare Workers workflow after pushing changes.
