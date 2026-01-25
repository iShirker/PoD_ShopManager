# Auth callback

**File:** `AuthCallback.tsx`  
**Route:** `/auth/callback`, `/auth/error`  
**Auth:** Not required

---

## Goals

1. **Handle OAuth redirect** — Process `code` (or `error`) from provider; exchange for tokens.
2. **Redirect** — On success → `/`; on error → `/login` with message or `/auth/error`.

**User goal:** Complete sign-in via Google/OAuth; land in app or see error.

---

## UI design

- **Loading state** — Spinner or “Signing you in…” while exchanging code.
- **Error state** — Message; “Back to login” link.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| AC1 | Callback with valid `code` processes and redirects to `/` | Redirect; user authenticated. |
| AC2 | Callback with `error` shows error or redirects to `/login` | No crash; user can retry. |
| AC3 | `/auth/error` shows error UI | Message and link to login. |
