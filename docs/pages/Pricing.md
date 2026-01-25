# Pricing calculator

**File:** `Pricing.tsx`  
**Route:** `/pricing`  
**Auth:** Required

---

## Goals

1. **Fee calculator** — Platform (Etsy / Shopify); price, cost; output fees, net profit, margin %.
2. **Etsy options** — Offsite ads on/off.
3. **Clear output** — Total fees, gross profit, net, margin.

**User goal:** Know true profit before pricing; compare Etsy vs Shopify fees.

---

## UI design

- **Header:** “Profitability Calculator” or “Calculator”.
- **Form:** Platform selector; selling price; cost; Etsy offsite ads checkbox.
- **Output:** Total fees, gross profit, net profit, margin %.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| PR1 | Pricing page loads at `/pricing` | “Calculator” or “Pricing” title; form visible. |
| PR2 | Enter price and cost shows results | Fees, net, margin displayed. |
| PR3 | Switching platform updates calculation | Etsy vs Shopify different output. |
| PR4 | Etsy offsite ads toggle changes result | Margin/fees change when toggled. |
| PR5 | Theme applied | Page uses theme variables. |
