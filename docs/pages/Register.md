# Register

**File:** `Register.tsx`  
**Route:** `/register`  
**Auth:** Not required (public)

---

## Goals

1. **Account creation** — User can register with email, password (and optional name).
2. **Validation** — Email format, password strength, confirm password (if used).
3. **Navigation** — Link to “Log in” for existing users.
4. **Error handling** — Clear message on duplicate email, validation failure, or network error.

**User goal:** Create an account and start using the app.

---

## Feature research

- **Standard registration** — Email, password, confirm password; optional first/last name.
- **E-commerce tools** — Often minimal fields; OAuth reduces friction.

---

## UI design

### Layout

- **Centered form:**
  - Email input.
  - Password input.
  - Optional: Confirm password, first name, last name.
  - “Create account” / “Register” button.
  - “Log in” link → `/login`.
- **Error area** for validation or API errors.

### Key elements

- Email, password inputs; submit button; “Log in” link.

### Actions

- Submit → POST `/api/auth/register`; on success, redirect to `/login` or auto-login and redirect to `/`.
- “Log in” → navigate to `/login`.

### Accessibility

- Labels for all inputs; errors associated via `aria-describedby`.

---

## Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| R1 | Register page loads at `/register` | Form visible; email, password inputs present. |
| R2 | Submit with invalid email shows validation error | Error shown; no API call or no redirect. |
| R3 | Submit with valid data creates account | Success; redirect to `/login` or `/`. |
| R4 | “Log in” link navigates to `/login` | Click → URL is `/login`. |
| R5 | Theme applied | Form uses theme variables. |
