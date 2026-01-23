# Test Scripts

This folder contains all test scripts for the PoD Shop Manager project.

## Purpose

Test scripts are located here (not in `backend/`) to prevent Railway from redeploying the backend service when test scripts are modified.

## Important Notes

- **All new test scripts MUST be created in this folder only** - never in the `backend/` folder
- **Default backend URL**: When testing the backend, use the production URL: `https://podshopmanagerbackend-production.up.railway.app`
- Scripts can be modified for local testing by changing the `BACKEND_URL` variable

## Scripts

- `test_api_keys.py` - Test API keys for various POD suppliers (Etsy, Shopify, Gelato, Printify, Printful)
- `test_gelato.py` - Test Gelato API connection
- `test_gelato2.py` - Additional Gelato API tests
- `test_printify_token.py` - Test Printify token validation
- `check_printify_token.py` - Quick check for Printify token status
- `test_backend_printify.py` - Test Printify connection through local backend API
- `test_production_backend.py` - Test production backend health and endpoints
- `test_production_printify.py` - Test Printify connection through production backend API

## Usage

All scripts can be run from the root directory:

```bash
# From project root
python TestScripts/test_api_keys.py
python TestScripts/test_printify_token.py
python TestScripts/test_production_backend.py
```

Or from the TestScripts directory:

```bash
cd TestScripts
python test_api_keys.py
python test_printify_token.py
```

## Environment Variables

Scripts that need environment variables will automatically load them from `backend/.env`. Make sure your `.env` file is configured in the backend folder.

## Notes

- These scripts are for development/testing only
- They are not part of the deployed application
- Modifying these scripts will NOT trigger Railway redeployments
