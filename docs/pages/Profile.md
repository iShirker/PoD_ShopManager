# Profile

**File:** `Profile.tsx`  
**Route:** `/profile`  
**Auth:** Required

---

## Goals

1. **Profile form** — Name, avatar, email (read-only or change flow).
2. **Preferences** — Theme selection; save.
3. **Password change** — Optional; current + new + confirm.

**User goal:** Update profile and preferences.

---

## UI design

- **Header:** “Profile”.
- **Form:** Name, avatar URL or upload; theme dropdown; save.
- **Password section:** Current, new, confirm; “Change password”.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| PF1 | Profile page loads at `/profile` | “Profile” title; form visible. |
| PF2 | Saving profile updates user | Success feedback; data persisted. |
| PF3 | Theme change updates theme | UI theme changes; saved. |
| PF4 | Theme applied | Page uses theme variables. |
