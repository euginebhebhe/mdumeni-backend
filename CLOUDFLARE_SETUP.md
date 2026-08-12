# Cloudflare Workers Routing Setup

## Overview
This document explains the Cloudflare Workers routing configuration for MDUMENI Backend. The setup allows your FastAPI backend to be accessible via a Cloudflare Worker URL.

## Files Created

### 1. **wrangler.toml** ✅ CRITICAL
- Cloudflare Workers configuration file
- Defines the worker name, compatibility date, and environment settings
- **Required fields to update:**
  - `zone_id` in `[env.production]` - Get from Cloudflare dashboard
  - `zone_id` in `[env.staging]` - Optional staging environment

### 2. **package.json** ✅
- Node.js package configuration
- Defines scripts for development and deployment
- Key scripts:
  - `npm run dev` - Run worker locally
  - `npm run deploy` - Deploy to production
  - `npm run deploy:staging` - Deploy to staging

### 3. **worker.js** ✅
- Main Cloudflare Worker entry point
- Routes requests to your FastAPI backend
- Handles CORS, headers, and errors

### 4. **index.js** ✅
- Request handler logic
- Forwards requests to your Python FastAPI backend
- Adds security and CORS headers
- Timeout handling (30 seconds)

### 5. **api_main.py** ✅
- FastAPI application entry point
- Copy of main.py with all routes configured
- Run with: `uvicorn api_main:app --host 0.0.0.0 --port 8000`

## Setup Steps

### Step 1: Install Dependencies
```bash
npm install
```

### Step 2: Configure Cloudflare
1. Go to https://dash.cloudflare.com/
2. Create a new Worker or use existing account
3. Get your **Zone ID** from Account Overview
4. Update `wrangler.toml`:
   ```toml
   [env.production]
   zone_id = "your-zone-id-here"
   ```

### Step 3: Set Environment Variables
Create a `.env` file or set in Cloudflare:
```bash
BACKEND_URL=https://your-fastapi-domain.com
```

Or use wrangler secrets:
```bash
wrangler secret put BACKEND_URL
```

### Step 4: Test Locally
```bash
npm run dev
```
This runs the worker on `http://localhost:8787`

### Step 5: Deploy to Cloudflare
```bash
npm run deploy
```

Or for staging:
```bash
npm run deploy:staging
```

## How It Works

```
[Client Request]
        ↓
[Cloudflare Worker (worker.js)]
        ↓
[worker.js routes to index.js]
        ↓
[index.js forwards to FastAPI]
        ↓
[Python FastAPI Backend (api_main.py)]
        ↓
[Response sent back through worker]
```

## Environment Variables

### For Local Development
Set `BACKEND_URL` to your local FastAPI server:
```
BACKEND_URL=http://localhost:8000
```

### For Production
Update in Cloudflare Dashboard or via wrangler secrets:
```bash
wrangler secret put BACKEND_URL
# Then enter your production URL when prompted
# e.g., https://api.mdumeni.com
```

## Running FastAPI Backend

### Local Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run FastAPI
uvicorn api_main:app --host 0.0.0.0 --port 8000 --reload
```

### Production (via Gunicorn)
```bash
gunicorn api_main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Troubleshooting

### "Cannot reach backend" Error
1. Check `BACKEND_URL` environment variable is set correctly
2. Verify FastAPI is running on the specified URL
3. Check Cloudflare Worker logs: `wrangler tail`
4. Ensure CORS is enabled (should be by default in worker.js)

### Timeout Errors
1. Increase timeout in `index.js` (currently 30 seconds)
2. Check if FastAPI backend is slow to respond
3. Monitor with: `wrangler tail --status ok --status error`

### Deployment Fails
1. Ensure `wrangler.toml` has valid `zone_id`
2. Run `npm install` to update dependencies
3. Check Node.js version: `node --version` (need v16+)
4. Verify authentication: `wrangler login`

## Testing Endpoints

Once deployed, test with:
```bash
# Get recommendations
curl -X POST https://mdumeni-backend.eugineeuman.workers.dev/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "soil_ph": 6.5,
    "soil_moisture_pct": 60,
    "soil_temp_c": 24,
    "agro_region": 3,
    "has_irrigation": true,
    "budget_level": "medium",
    "planting_month": 10
  }'

# Health check
curl https://mdumeni-backend.eugineeuman.workers.dev/health

# Swagger docs
curl https://mdumeni-backend.eugineeuman.workers.dev/docs
```

## Next Steps

1. ✅ Files created
2. ⬜ Update `wrangler.toml` with your Cloudflare Zone ID
3. ⬜ Set `BACKEND_URL` environment variable
4. ⬜ Run `npm install`
5. ⬜ Test locally with `npm run dev`
6. ⬜ Deploy with `npm run deploy`

## Support

For issues with:
- **Cloudflare Workers**: https://developers.cloudflare.com/workers/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Wrangler CLI**: https://developers.cloudflare.com/workers/wrangler/
