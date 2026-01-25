# Version (deployment check)

**File:** `Version.tsx`  
**Route:** `/version`  
**Auth:** Not required

---

## Goals

1. **Deployment verification** — Confirm frontend and backend are running.
2. **Display** — Frontend build id, backend health status, backend version.

**User goal:** (Internal) Verify deployment; E2E uses this to assert both app and API are up.

---

## UI design

- **Body:** Card with “Deployment check”; frontend build, backend status, backend version.
- **Success:** “Frontend and backend are running.” when `health.status === 'healthy'`.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| V1 | `/version` loads | Page renders; “Deployment check” or build/backend info visible. |
| V2 | Backend health fetched | `data-testid="backend-status"` or `backend-version` present; status “healthy”. |
| V3 | `data-testid="deployment-ok"` when healthy | Element visible when backend returns healthy. |
