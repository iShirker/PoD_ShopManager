# Login

**File:** `Login.tsx`  
**Route:** `/login`  
**Auth:** Not required (public)

---

## Goals

1. **Email/password sign-in** — Users can log in with email + password.
2. **OAuth options** — “Sign in with Google”, “Sign in with Etsy”, “Sign in with Shopify” where configured.
3. **Navigation** — Link to “Register” for new users; optional “Forgot password” when implemented.
4. **Error handling** — Clear message on invalid credentials or network error.

**User goal:** Sign in quickly and reach the app; choose between email/password and OAuth.

---

## Feature research

- **E-commerce seller tools** — Login typically combines email/password plus Google; Etsy/Shopify OAuth for marketplace-linked apps.
- **Best practice** — Single form, visible OAuth buttons, “Remember me” optional, clear error messages.

---

## UI design

### Layout

- **Centered card** (or full-width form on small screens):
  - App logo / “POD Manager” title.
  - Email input (type email).
  - Password input (type password).
  - “Log in” button.
  - “Register” link → `/register`.
- **OAuth section:** Buttons for Google, Etsy, Shopify (if enabled). Each triggers OAuth flow.
- **Error area:** Inline or toast for “Invalid email or password”, “Network error”, etc.

### Key elements

- `input` email, `input` password, `button` “Log in”.
- Links: “Register”, OAuth buttons.
- Error message element (conditional).

### Actions

- Submit form → POST `/api/auth/login`; on success, store tokens, redirect to `/`.
- Click “Register” → navigate to `/register`.
- Click “Sign in with Google” → redirect to Google OAuth.
- Click “Sign in with Etsy” → redirect to Etsy OAuth.
- Click “Sign in with Shopify” → redirect to Shopify OAuth (may require shop domain first).

### Accessibility

- Labels for email and password.
- Form has `aria-describedby` for errors when present.

---

## Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| L1 | Login page loads at `/login` | Form visible; email and password inputs present. |
| L2 | Submit with invalid credentials shows error | Error message displayed; no redirect to `/`. |
| L3 | Submit with valid credentials redirects to `/` | Redirect to `/`; user is authenticated. |
| L4 | “Register” link navigates to `/register` | Click → URL is `/register`. |
| L5 | OAuth buttons present when configured | At least one of Google/Etsy/Shopify visible if configured. |
| L6 | Authenticated user visiting `/login` redirects to `/` | Redirect to `/`. |
| L7 | Theme applied | Login form uses theme variables. |
