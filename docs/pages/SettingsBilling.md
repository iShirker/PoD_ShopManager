# Billing

**File:** `SettingsBilling.tsx`  
**Route:** `/settings/billing`  
**Auth:** Required

---

## Goals

1. **Plan comparison** — Free Trial, Starter, Pro, Master; monthly/yearly toggle; limits, features.
2. **Current plan** — Name, start/expiry, auto-renew or cancelled; usage vs limits.
3. **Select plan** — Radio select; total, proration; “Pay” or “Start free trial”.
4. **Cancel** — Disable auto-renew; confirm dialog.

**User goal:** Choose plan, see usage, pay, cancel without confusion.

---

## UI design

- **Header:** “Billing” or “Subscription”.
- **Plan table** — Columns = plans; rows = price, limits, features; current usage column; “Select” per plan.
- **Monthly/yearly** toggle centered above table.
- **Current plan** — Left: plan, dates, auto-renew/cancelled; right: “Cancel” button.
- **Bottom right** — Total, “Pay” or “Start free trial”; Free Trial shows Total 0.
- **Payment modal** — When Pay clicked; payment options (USA, Europe, Other) — TBD processor.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| B1 | Billing page loads at `/settings/billing` | “Billing” or plan table visible. |
| B2 | All plans shown (Trial, Starter, Pro, Master) | Four columns or rows. |
| B3 | Monthly/yearly toggle switches pricing and limits | Values update. |
| B4 | Current plan highlighted | “Your plan” or similar; dates shown. |
| B5 | Selecting plan updates Total | Total reflects selection; Free Trial = 0. |
| B6 | “Start free trial” when Trial selected | Button visible; disabled if already used. |
| B7 | “Cancel” shows confirmation | Dialog; confirm disables auto-renew. |
| B8 | Theme applied | Page uses theme variables. |
