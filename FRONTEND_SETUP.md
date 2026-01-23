# Frontend Setup Guide

## Environment Variables

### Required for Production

The frontend **MUST** have the `VITE_API_URL` environment variable set in Railway for production deployments.

#### Setting VITE_API_URL in Railway

1. Go to Railway Dashboard
2. Select your **Frontend** service (not backend)
3. Go to **Variables** tab
4. Click **+ New Variable**
5. Add:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://podshopmanagerbackend-production.up.railway.app/api`
6. Click **Add**
7. **Redeploy** the frontend service (Railway should auto-redeploy, but you can trigger it manually)

#### Why This is Required

- **Development**: Vite proxy automatically forwards `/api` to `http://localhost:5000`
- **Production**: No proxy exists, so the frontend needs the full backend URL
- **Without it**: Frontend tries to use `/api` which doesn't work in production, causing "Network error"

### Verification

After setting `VITE_API_URL` and redeploying:

1. Open browser DevTools (F12)
2. Go to Console tab
3. You should see:
   ```
   API Base URL: https://podshopmanagerbackend-production.up.railway.app/api
   VITE_API_URL env var: https://podshopmanagerbackend-production.up.railway.app/api
   ```

If you see `API Base URL: /api` and `VITE_API_URL env var: (not set)`, then the environment variable is not configured correctly.

## Troubleshooting

### "Network error - cannot reach server"

**Possible causes:**
1. `VITE_API_URL` not set in Railway → Set it and redeploy
2. Frontend not redeployed after setting variable → Redeploy frontend service
3. Backend service is down → Check Railway backend service status
4. CORS issue → Check backend CORS configuration

**Check:**
1. Browser Console (F12) → Look for API Base URL logs
2. Network tab → Check if requests are going to the correct URL
3. Railway logs → Check if backend is receiving requests

### Testing Backend Connection

You can test if the backend is accessible:
```bash
# Test backend health
curl https://podshopmanagerbackend-production.up.railway.app/api/health

# Should return: {"status":"healthy","message":"POD Manager API is running"}
```

## Local Development

For local development, you don't need to set `VITE_API_URL`. The Vite proxy will handle it automatically.

If you want to test against production backend locally:
```bash
# Create frontend/.env.local (not committed to git)
VITE_API_URL=https://podshopmanagerbackend-production.up.railway.app/api
```
