# Fulfillment

**File:** `OrdersFulfillment.tsx`  
**Route:** `/orders/fulfillment`  
**Auth:** Required

---

## Goals

1. **Fulfillment queue** — Orders/items pending fulfillment; customer, items, destination.
2. **Actions** — “Fulfill” (send to PoD), “Skip”, “Cancel”; bulk actions if applicable.

**User goal:** Work through unfulfilled orders; send to PoD without leaving the app.

---

## UI design

- **Header:** “Fulfillment” or “Orders pending fulfillment”.
- **List** of pending orders: order ID, customer, items, “Fulfill” / “Skip”.
- **Empty state** when none pending.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| OF1 | Fulfillment page loads at `/orders/fulfillment` | “Fulfillment” title; list or empty state. |
| OF2 | Pending orders listed | Order ID, customer or items visible. |
| OF3 | “Fulfill” triggers fulfillment flow | Loading; order moves out of queue or status updates. |
| OF4 | Empty state when no pending | Message; no error. |
| OF5 | Theme applied | Page uses theme variables. |
