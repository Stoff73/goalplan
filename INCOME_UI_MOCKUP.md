# Income Tracking UI - Visual Mockup

This document provides a visual representation of what the Income Tracking UI looks like.

---

## Page: `/income`

```
┌──────────────────────────────────────────────────────────────────────────┐
│  GoalPlan         Dashboard  Tax Status  Income  Profile    John Doe  [=] │
└──────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│  Your Income Tracking                                                      │
│                                                                            │
│  Track your income from all sources across the UK and South Africa.       │
│  We'll help you understand your total earnings, tax withholding, and      │
│  cross-border tax treatment.                                              │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  Tax Year Country: [UK Tax Year ▼]    Tax Year: [2024/25 ▼]  [+ Add Income]│
│  UK tax year runs from 6 April to 5 April                                 │
│  📅 6 April 2024 - 5 April 2025                                           │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  Your income summary for 2024/25                                           │
│                                                                            │
│  You earned a total of £52,500 (R1,215,000) in the UK tax year 2024/25.  │
│                                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ £52,500.00   │  │ R1,215,000.00│  │ £12,500.00   │  │ £7,500.00    │  │
│  │ Total Income │  │ Total Income │  │ Tax Already  │  │ Foreign      │  │
│  │ (GBP)        │  │ (ZAR)        │  │ Withheld     │  │ Income       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                            │
│  You've already paid £12,500 in tax through PAYE. This will be credited   │
│  against your final tax liability.                                         │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ ℹ️ Foreign income detected                                           │ │
│  │                                                                      │ │
│  │ You have £7,500 in foreign income. Under the UK-SA Double Tax       │ │
│  │ Agreement, you may be able to claim credit for foreign tax paid     │ │
│  │ (£1,200 in credits available).                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  Income by Type                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 💼 Employment                                           £45,000.00   │ │
│  ├──────────────────────────────────────────────────────────────────────┤ │
│  │ 🏠 Rental Income                                         £7,500.00   │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  Income by Source Country                                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 🇬🇧 United Kingdom                                      £45,000.00   │ │
│  ├──────────────────────────────────────────────────────────────────────┤ │
│  │ 🇺🇸 United States                                        £7,500.00   │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ ✅ Understanding your income                                         │ │
│  │                                                                      │ │
│  │ This is your gross income before tax. We track your income in the   │ │
│  │ currency you received it, then convert to GBP and ZAR for tax       │ │
│  │ calculations. Your actual tax liability will depend on your tax     │ │
│  │ residency status, domicile, and applicable allowances.              │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  Income Entries                                                            │
│                                                                            │
│  Filter by Type: [All Types ▼]  Filter by Country: [All Countries ▼]     │
│  Sort By: [Date (Newest First) ▼]                                         │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 💼 ABC Company Ltd                                      £45,000.00   │ │
│  │ Annually                                                             │ │
│  │                                                                      │ │
│  │ 🇬🇧 United Kingdom  •  📅 1 April 2024  •  💷 GBP: £45,000.00      │ │
│  │ 💵 ZAR: R1,035,000.00  •  🧾 Tax withheld: £10,000.00               │ │
│  │                                                                      │ │
│  │ ──────────────────────────────────────────────────────────────────  │ │
│  │ [Edit]  [Delete]                                                    │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 🏠 US Rental Property                                    $10,000.00  │ │
│  │ Monthly    🔵 Foreign income (DTA may apply)                        │ │
│  │                                                                      │ │
│  │ 🇺🇸 United States  •  📅 1 January 2024  •  💷 GBP: £7,500.00      │ │
│  │ 💵 ZAR: R172,500.00                                                 │ │
│  │                                                                      │ │
│  │ ──────────────────────────────────────────────────────────────────  │ │
│  │ [Edit]  [Delete]                                                    │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  ℹ️ Understanding your income tracking                                     │
│                                                                            │
│  We track your income in the currency you received it, then convert to    │
│  GBP and ZAR for tax calculations using official exchange rates. This     │
│  helps you understand your tax obligations in both jurisdictions.         │
│                                                                            │
│  Foreign income is income from outside the UK and SA. Under the UK-SA     │
│  Double Tax Agreement, you can claim credit for foreign tax paid,         │
│  preventing you from being taxed twice on the same income.                │
│                                                                            │
│  Tax withheld includes PAYE (UK), PASE (SA), and other withholding taxes. │
│  These amounts are credited against your final tax liability when you     │
│  file your tax return.                                                    │
│                                                                            │
│  Your actual tax liability depends on your tax residency status,          │
│  domicile, and available allowances like the UK Personal Savings          │
│  Allowance or SA interest exemption.                                      │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Modal: Add Income

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         [X]  Add income entry                            │
│                                                                          │
│  Record your income to track earnings and tax obligations across the UK │
│  and South Africa. We'll automatically convert amounts and calculate    │
│  tax treatment.                                                          │
│                                                                          │
│  ┌────────────────────────────┐  ┌────────────────────────────┐        │
│  │ Income Type *              │  │ Source Country *           │        │
│  │ [Select income type ▼]     │  │ [United Kingdom ▼]         │        │
│  └────────────────────────────┘  └────────────────────────────┘        │
│                                                                          │
│  ┌────────────────────────────┐  ┌────────────────────────────┐        │
│  │ Description                │  │ Employer Name              │        │
│  │ [e.g., Monthly salary]     │  │ [e.g., ABC Company Ltd]    │        │
│  └────────────────────────────┘  └────────────────────────────┘        │
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────────┐        │
│  │ Amount *   │  │ Currency * │  │ Frequency *                │        │
│  │ [0.00]     │  │ [GBP (£)▼] │  │ [Annually ▼]               │        │
│  └────────────┘  └────────────┘  └────────────────────────────┘        │
│  Enter the amount in the currency you received it                       │
│                                                                          │
│  ┌────────────────────────────┐  ┌────────────────────────────┐        │
│  │ Start Date *               │  │ End Date (Optional)        │        │
│  │ [2024-04-01]               │  │ [          ]               │        │
│  └────────────────────────────┘  └────────────────────────────┘        │
│                                  Leave blank if ongoing                 │
│                                                                          │
│  Income Type                                                             │
│  ○ Gross (before tax)    ○ Net (after tax)                             │
│  Gross = before tax, Net = after tax. Choose gross for accurate tax     │
│  calculations.                                                           │
│                                                                          │
│  ☐ Tax withheld at source (PAYE, PASE, etc.)                           │
│                                                                          │
│  ──────────────────────────────────────────────────────────────────────│
│                                               [Cancel]  [Add Income]    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Modal: Add Income (with Foreign Income)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         [X]  Add income entry                            │
│                                                                          │
│  Record your income to track earnings and tax obligations across the UK │
│  and South Africa. We'll automatically convert amounts and calculate    │
│  tax treatment.                                                          │
│                                                                          │
│  ┌────────────────────────────┐  ┌────────────────────────────┐        │
│  │ Income Type *              │  │ Source Country *           │        │
│  │ [Investment Income ▼]      │  │ [United States ▼]          │        │
│  └────────────────────────────┘  └────────────────────────────┘        │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ ℹ️ Foreign income detected                                       │  │
│  │                                                                  │  │
│  │ Income from outside the UK and SA. We'll calculate tax treatment│  │
│  │ under Double Tax Agreements to prevent you from being taxed     │  │
│  │ twice on the same income.                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────┐  ┌────────────────────────────┐        │
│  │ Description                │  │ Source/Entity              │        │
│  │ [US dividend income]       │  │ [Portfolio 1]              │        │
│  └────────────────────────────┘  └────────────────────────────┘        │
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────────┐        │
│  │ Amount *   │  │ Currency * │  │ Frequency *                │        │
│  │ [10000.00] │  │ [USD ($)▼] │  │ [Annually ▼]               │        │
│  └────────────┘  └────────────┘  └────────────────────────────┘        │
│                                                                          │
│  ☑ Tax withheld at source (PAYE, PASE, etc.)                           │
│                                                                          │
│  ┌────────────────────────────┐  ┌────────────────────────────┐        │
│  │ Tax Withheld Amount        │  │ PAYE Reference (Optional)  │        │
│  │ [1500.00]                  │  │ [                ]         │        │
│  └────────────────────────────┘  └────────────────────────────┘        │
│  Tax already deducted (PAYE in UK, PASE in SA)                         │
│                                                                          │
│  ──────────────────────────────────────────────────────────────────────│
│                                               [Cancel]  [Add Income]    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Modal: Income Details

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    [X]  💼 ABC Company Ltd                               │
│                                                                          │
│  🇬🇧 United Kingdom • Annually                                          │
│                                                                          │
│  Income Details                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Income Type                                      Employment       │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Amount                                           £45,000.00       │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Frequency                                        Annually         │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Employer                                         ABC Company Ltd  │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Income Type                                      Gross (before tax)│ │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Start Date                                       1 April 2024     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Currency Conversion                                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Original Amount                                  £45,000.00       │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Converted to GBP                                 £45,000.00       │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Converted to ZAR                                 R1,035,000.00    │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Exchange Rate                                    23.000000        │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Exchange Rate Date                               1 April 2024     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Tax Withheld                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Tax Withheld at Source                           £10,000.00       │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ PAYE Reference                                   123/AB12345      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Tax Year Allocation                                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ UK Tax Year                                      2024/25          │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ SA Tax Year                                      2024/2025        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ ✅ How this income is taxed                                      │  │
│  │                                                                  │  │
│  │ Your final tax liability depends on your tax residency status   │  │
│  │ and domicile. We convert all income to GBP and ZAR for tax      │  │
│  │ calculations. Tax already withheld will be credited against     │  │
│  │ your final liability.                                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ──────────────────────────────────────────────────────────────────────│
│                                      [Close]  [Edit]  [Delete]          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Empty State

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Your income summary for 2024/25                                           │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                                                                      │ │
│  │                     No income recorded yet.                          │ │
│  │                                                                      │ │
│  │     Add your first income entry to start tracking your earnings     │ │
│  │             and tax obligations.                                     │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  Income Entries                                                            │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                                                                      │ │
│  │                     No income recorded yet.                          │ │
│  │                                                                      │ │
│  │     Add your first income entry to start tracking earnings →        │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Mobile View

```
┌──────────────────────────────┐
│ ☰  GoalPlan         John [•] │
├──────────────────────────────┤
│                              │
│  Your Income Tracking        │
│                              │
│  Track your income from all  │
│  sources across the UK and   │
│  South Africa.               │
│                              │
├──────────────────────────────┤
│  Tax Year Country            │
│  [UK Tax Year ▼]            │
│                              │
│  Tax Year                    │
│  [2024/25 ▼]                │
│                              │
│  📅 6 April 2024 -           │
│     5 April 2025             │
│                              │
│  [+ Add Income] (full width) │
├──────────────────────────────┤
│  Your income summary         │
│  for 2024/25                 │
│                              │
│  You earned £52,500          │
│  (R1,215,000) this year.     │
│                              │
│  ┌────────────────────────┐ │
│  │ £52,500.00             │ │
│  │ Total Income (GBP)     │ │
│  └────────────────────────┘ │
│                              │
│  ┌────────────────────────┐ │
│  │ R1,215,000.00          │ │
│  │ Total Income (ZAR)     │ │
│  └────────────────────────┘ │
│                              │
│  ┌────────────────────────┐ │
│  │ £12,500.00             │ │
│  │ Tax Withheld           │ │
│  └────────────────────────┘ │
│                              │
├──────────────────────────────┤
│  Income Entries              │
│                              │
│  Filter: [All Types ▼]      │
│  Country: [All ▼]           │
│  Sort: [Date ▼]             │
│                              │
│  ┌────────────────────────┐ │
│  │ 💼 ABC Company         │ │
│  │ £45,000.00             │ │
│  │ Annually               │ │
│  │                        │ │
│  │ 🇬🇧 UK • 📅 Apr 2024  │ │
│  │ GBP: £45,000           │ │
│  │ ZAR: R1,035,000        │ │
│  │                        │ │
│  │ [Edit] [Delete]        │ │
│  └────────────────────────┘ │
│                              │
│  ┌────────────────────────┐ │
│  │ 🏠 US Property         │ │
│  │ $10,000 🔵 Foreign    │ │
│  │ Monthly                │ │
│  │                        │ │
│  │ 🇺🇸 US • 📅 Jan 2024  │ │
│  │ GBP: £7,500            │ │
│  │                        │ │
│  │ [Edit] [Delete]        │ │
│  └────────────────────────┘ │
└──────────────────────────────┘
```

---

## Color Scheme Reference

### Text Colors
- **Primary Heading:** #0F172A (near-black)
- **Body Text:** #475569 (medium gray)
- **Secondary Text:** #64748B (light gray)
- **Tertiary Text:** #94A3B8 (lighter gray)

### Background Colors
- **Page Background:** #FFFFFF (white)
- **Card Background:** #FFFFFF (white)
- **Metric Background:** #F8FAFC (very light gray)
- **Hover Background:** #F1F5F9 (light gray hover)

### Accent Colors
- **Primary Blue:** #2563EB (links, buttons)
- **Info Blue:** #3B82F6 (callouts, badges)
- **Success Green:** #10B981 (educational callouts)
- **Warning Amber:** #F59E0B (warnings)
- **Danger Red:** #EF4444 (delete actions)

### Callout Backgrounds
- **Info:** #EFF6FF (light blue)
- **Success:** #F0FDF4 (light green)
- **Warning:** #FEF3C7 (light amber)

### Borders
- **Default:** #E2E8F0 (light gray)
- **Light:** #F1F5F9 (very light gray)
- **Callout:** 4px solid accent color on left

---

**Visual Reference Version:** 1.0
**Last Updated:** 2025-10-02
**Status:** Complete

