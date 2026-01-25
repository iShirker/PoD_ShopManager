# Supplier callback

**File:** `SupplierCallback.tsx`  
**Route:** `/suppliers/callback`  
**Auth:** Required

---

## Goals

1. **Handle supplier OAuth redirect** — e.g. Printify/Printful return `code`; exchange, store connection.
2. **Redirect** — Success → `/suppliers`; error → `/suppliers` with message.

**User goal:** Complete supplier connection; return to app.

---

## UI design

- **Loading** — “Connecting supplier…”.
- **Error** — Message; link to `/suppliers`.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| SUC1 | Callback with valid `code` completes and redirects | Redirect to `/suppliers`. |
| SUC2 | Error shows message | No crash; retry possible. |
