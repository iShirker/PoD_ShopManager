# Shop callback

**File:** `ShopCallback.tsx`  
**Route:** `/shops/callback`  
**Auth:** Required (or post-connect)

---

## Goals

1. **Handle shop OAuth redirect** — Etsy/Shopify returns `code`; exchange, store shop + tokens.
2. **Redirect** — Success → `/shops` or dashboard; error → `/shops` with message.

**User goal:** Complete shop connection; return to app.

---

## UI design

- **Loading** — “Connecting shop…”.
- **Error** — Message; link to `/shops`.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| SHC1 | Callback with valid `code` completes connection and redirects | Redirect to `/shops` or similar. |
| SHC2 | Error in callback shows message | No crash; user can retry. |
