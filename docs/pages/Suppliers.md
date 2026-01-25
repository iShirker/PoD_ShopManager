# Suppliers

**File:** `Suppliers.tsx`  
**Route:** `/suppliers`  
**Auth:** Required

---

## Goals

1. **List PoD connections** — Gelato, Printify, Printful; show connection status per type.
2. **Connect** — Per-supplier connect (API key or OAuth).
3. **Actions** — Sync catalog, disconnect.

**User goal:** Manage PoD supplier connections; connect, sync, disconnect.

---

## UI design

- **Header:** “Suppliers”; connect buttons per supplier type.
- **List/cards** per supplier: name, status, “Sync”, “Disconnect”.
- **Empty state** when none connected.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| SU1 | Suppliers page loads at `/suppliers` | “Suppliers” and connect options visible. |
| SU2 | Connected suppliers shown | Name, status; Sync/Disconnect available. |
| SU3 | “Connect” opens supplier flow | No JS error. |
| SU4 | “Sync” triggers sync | Loading; UI updates. |
| SU5 | Theme applied | Page uses theme variables. |
