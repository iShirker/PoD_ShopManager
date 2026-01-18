# POD Manager - Print on Demand Management Platform

A comprehensive Flask + React application for managing Print on Demand products across multiple suppliers (Gelato, Printify, Printful) and marketplaces (Etsy, Shopify).

## Features

### 1. Authentication
- Local email/password registration and login
- OAuth integration with Google, Etsy, Shopify
- OAuth-ready endpoints for Gelato, Printify, Printful (API key auth)
- JWT-based authentication with refresh tokens
- User profile management

### 2. Supplier Connections
- Connect multiple POD suppliers (Gelato, Printify, Printful)
- API key management and validation
- Product catalog synchronization
- View supplier products with pricing

### 3. Shop Management
- Connect multiple Etsy and Shopify shops
- OAuth-based shop authentication
- Automatic listing synchronization
- SKU-based POD product detection

### 4. Supplier Comparison
- Compare product prices across connected suppliers
- View base price + shipping costs
- Identify potential savings
- One-click supplier switching
- Bulk product migration

### 5. Listing Templates
- Create reusable listing templates
- Add products from different suppliers
- Select sizes and colors per product
- Generate listings across platforms

## Project Structure

```
ETSY_PoD_Products/
├── backend/                    # Flask API
│   ├── app/
│   │   ├── blueprints/        # API routes
│   │   │   ├── auth/          # Authentication
│   │   │   ├── users/         # User profiles
│   │   │   ├── suppliers/     # POD supplier management
│   │   │   ├── shops/         # Etsy/Shopify shops
│   │   │   ├── products/      # Product comparison & switching
│   │   │   └── templates/     # Listing templates
│   │   ├── models/            # SQLAlchemy models
│   │   └── services/          # Business logic
│   │       ├── suppliers/     # Gelato, Printify, Printful APIs
│   │       ├── shops/         # Etsy, Shopify APIs
│   │       ├── comparison.py  # Price comparison
│   │       ├── switching.py   # Supplier switching
│   │       └── templates.py   # Template listing creation
│   ├── config.py              # Configuration
│   ├── run.py                 # Entry point
│   └── requirements.txt
├── frontend/                   # React + Tailwind
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── store/             # Zustand state management
│   │   └── lib/               # API client, utilities
│   ├── package.json
│   └── vite.config.ts
└── .env.example               # Environment template
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp ../.env.example .env
# Edit .env with your API keys
```

4. Initialize database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run development server:
```bash
python run.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Run development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/google/authorize` - Start Google OAuth
- `GET /api/auth/etsy/authorize` - Start Etsy OAuth
- `GET /api/auth/shopify/authorize` - Start Shopify OAuth

### Users
- `GET /api/users/me` - Get current user profile
- `PATCH /api/users/me` - Update profile
- `PUT /api/users/me/password` - Change password
- `GET /api/users/me/summary` - Get user summary with stats

### Suppliers
- `GET /api/suppliers` - List all supplier connections
- `POST /api/suppliers/{type}/connect` - Connect a supplier
- `POST /api/suppliers/{type}/disconnect` - Disconnect a supplier
- `POST /api/suppliers/{type}/sync` - Sync supplier products
- `GET /api/suppliers/{type}/products` - Get supplier products

### Shops
- `GET /api/shops` - List connected shops
- `POST /api/shops/etsy/connect` - Connect Etsy shop
- `POST /api/shops/shopify/connect` - Connect Shopify shop
- `POST /api/shops/{id}/sync` - Sync shop listings
- `GET /api/shops/{id}/products` - Get shop products

### Products
- `GET /api/products/compare` - Compare product prices
- `GET /api/products/compare/summary` - Get comparison summary
- `POST /api/products/switch` - Switch product supplier
- `POST /api/products/switch/bulk` - Bulk switch suppliers
- `GET /api/products/types` - Get product types

### Templates
- `GET /api/templates` - List templates
- `POST /api/templates` - Create template
- `GET /api/templates/{id}` - Get template details
- `PATCH /api/templates/{id}` - Update template
- `POST /api/templates/{id}/products` - Add product to template
- `POST /api/templates/{id}/products/{pid}/colors` - Add color
- `POST /api/templates/{id}/create-listing` - Create listing from template

## Environment Variables

### Required
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key

### OAuth (for OAuth login)
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `ETSY_API_KEY`, `ETSY_API_SECRET`
- `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET`

### POD Suppliers
- `GELATO_API_KEY`
- `PRINTIFY_API_KEY`
- `PRINTFUL_API_KEY`

## SKU Patterns

The system detects POD suppliers based on SKU patterns:

| Supplier | Patterns |
|----------|----------|
| Gelato | `GEL_`, `GELATO_`, `GLT_` |
| Printify | `PFY_`, `PRINTIFY_`, `PRF_` |
| Printful | `PFL_`, `PRINTFUL_`, `PF_` |

When switching suppliers, SKUs are automatically updated to match the new supplier's pattern.

## Development Notes

### Adding a New Supplier

1. Create service file in `backend/app/services/suppliers/`
2. Add to supplier type enum in `backend/app/models/supplier.py`
3. Add validation function and export in `__init__.py`
4. Update SKU patterns in comparison and switching services
5. Add UI elements in frontend supplier components

### Adding a New Marketplace

1. Create service file in `backend/app/services/shops/`
2. Add to shop type enum in `backend/app/models/shop.py`
3. Create OAuth handlers in auth blueprint
4. Add sync function for listings
5. Update frontend shop components

## License

MIT
