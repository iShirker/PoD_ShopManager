# Railway Environment Variables for Backend

This document lists all environment variables that should be configured in Railway for the backend service.

## Required Variables

### Core Application
- **SECRET_KEY** - Flask secret key for session management (generate a secure random string)
- **JWT_SECRET_KEY** - Secret key for JWT token signing (generate a secure random string)
- **DATABASE_URL** - Database connection string (Railway provides this automatically when you add a PostgreSQL database)
- **PORT** - Server port (Railway sets this automatically, but defaults to 5000 if not set)

### URLs
- **FRONTEND_URL** - Frontend application URL (e.g., `https://podshopmanagerfrontend-production.up.railway.app`)
- **BACKEND_URL** - Backend application URL (e.g., `https://podshopmanagerbackend-production.up.railway.app`)

### Google OAuth
- **GOOGLE_CLIENT_ID** - Google OAuth 2.0 Client ID
- **GOOGLE_CLIENT_SECRET** - Google OAuth 2.0 Client Secret

### Etsy API
- **ETSY_API_KEY** - Etsy API Keystring
- **ETSY_API_SECRET** - Etsy Shared Secret
- **ETSY_REDIRECT_URI** - Etsy OAuth redirect URI (e.g., `https://podshopmanagerbackend-production.up.railway.app/api/auth/etsy/callback`)

### Shopify API
- **SHOPIFY_API_KEY** - Shopify API Key
- **SHOPIFY_API_SECRET** - Shopify API Secret

### Gelato API (Optional - for OAuth)
- **GELATO_CLIENT_ID** - Gelato OAuth Client ID
- **GELATO_CLIENT_SECRET** - Gelato OAuth Client Secret
- **GELATO_REDIRECT_URI** - Gelato OAuth redirect URI (e.g., `https://podshopmanagerbackend-production.up.railway.app/api/auth/gelato/callback`)
- **GELATO_OAUTH_SCOPE** - Gelato OAuth scope (optional)
- **GELATO_OAUTH_AUTHORIZE_URL** - Gelato OAuth authorization URL (defaults to `https://api.gelato.com/oauth/authorize`)
- **GELATO_OAUTH_TOKEN_URL** - Gelato OAuth token URL (defaults to `https://api.gelato.com/oauth/token`)

### Printify API (Optional)
- **PRINTIFY_CLIENT_ID** - Printify OAuth Client ID
- **PRINTIFY_CLIENT_SECRET** - Printify OAuth Client Secret
- **PRINTIFY_TOKEN** - Printify Personal Access Token (alternative to OAuth)

### Printful API (Optional)
- **PRINTFUL_CLIENT_ID** - Printful OAuth Client ID
- **PRINTFUL_CLIENT_SECRET** - Printful OAuth Client Secret

### Flask Environment (Optional)
- **FLASK_ENV** - Flask environment mode (`development`, `production`, or `testing`). Defaults to `development` if not set.

## Notes

1. **Railway Auto-Provided Variables:**
   - `DATABASE_URL` - Automatically set when you add a PostgreSQL database service
   - `PORT` - Automatically set by Railway (usually 5000 or 8080)
   - `RAILWAY_ENVIRONMENT` - Railway environment name
   - `RAILWAY_SERVICE_NAME` - Service name

2. **OAuth Redirect URIs:**
   Make sure to register these redirect URIs in the respective OAuth provider dashboards:
   - Google: `{BACKEND_URL}/api/auth/google/callback`
   - Etsy: `{BACKEND_URL}/api/auth/etsy/callback`
   - Shopify: `{BACKEND_URL}/api/auth/shopify/callback`
   - Gelato: `{BACKEND_URL}/api/auth/gelato/callback`
   - Printify: `{BACKEND_URL}/api/auth/printify/callback`
   - Printful: `{BACKEND_URL}/api/auth/printful/callback`

3. **Security:**
   - Never commit `.env` files to git
   - Use strong, randomly generated values for `SECRET_KEY` and `JWT_SECRET_KEY`
   - Rotate secrets regularly in production

4. **Optional Variables:**
   Variables marked as "Optional" are only needed if you're using those specific integrations. You can omit them if not needed.
