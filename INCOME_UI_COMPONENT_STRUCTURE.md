# Income UI Component Structure

## Component Hierarchy

```
IncomePage (Main Container)
│
├── Header Section
│   ├── Page Title
│   ├── Page Description
│   └── Alert Messages (Error/Success)
│
├── Controls Row
│   ├── IncomeTaxYearSwitcher
│   │   ├── Country Selector (UK/SA)
│   │   ├── Tax Year Dropdown
│   │   └── Date Range Display
│   │
│   └── Add Income Button
│
├── IncomeSummarySection
│   ├── Summary Heading
│   ├── Narrative Text
│   ├── Metric Grid
│   │   ├── Total GBP
│   │   ├── Total ZAR
│   │   ├── Tax Withheld (conditional)
│   │   └── Foreign Income (conditional)
│   ├── Income by Type Breakdown
│   ├── Income by Country Breakdown
│   └── Educational Callout
│
├── IncomeList
│   ├── Filters Row
│   │   ├── Type Filter
│   │   ├── Country Filter
│   │   └── Sort Selector
│   │
│   └── Income Cards (forEach)
│       ├── Header
│       │   ├── Icon + Title
│       │   ├── Amount + Currency
│       │   └── Foreign Badge (conditional)
│       ├── Details Row
│       │   ├── Country + Flag
│       │   ├── Date
│       │   ├── GBP Amount
│       │   ├── ZAR Amount
│       │   └── Tax Withheld (conditional)
│       └── Actions
│           ├── Edit Button
│           └── Delete Button
│
├── Educational Footer
│
└── Modals (conditional rendering)
    ├── IncomeFormModal (if showFormModal)
    │   ├── Modal Header
    │   ├── Form Fields Grid
    │   │   ├── Income Type
    │   │   ├── Source Country
    │   │   ├── Description
    │   │   ├── Related Entity
    │   │   ├── Amount + Currency
    │   │   ├── Frequency
    │   │   ├── Start/End Dates
    │   │   ├── Gross/Net Toggle
    │   │   └── Tax Withheld Section (expandable)
    │   └── Actions (Cancel / Save)
    │
    └── IncomeDetailsModal (if showDetailsModal)
        ├── Modal Header
        ├── Income Details Section
        ├── Currency Conversion Section
        ├── Tax Information Section (conditional)
        ├── Tax Year Allocation Section (conditional)
        ├── Tax Treatment Callout
        └── Actions (Close / Edit / Delete)
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        IncomePage                            │
│  (State: incomes, summary, modals, filters, loading, error) │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
           ┌────────▼────────┐  ┌──────▼──────┐
           │  Load Incomes   │  │Load Summary │
           │  (on mount)     │  │(on tax year)│
           └────────┬────────┘  └──────┬──────┘
                    │                   │
         ┌──────────▼───────────────────▼──────────┐
         │        API Endpoints (utils/api.js)      │
         │  getAll() / getSummary() / create() /    │
         │        update() / delete()               │
         └──────────────────┬───────────────────────┘
                            │
                ┌───────────▼───────────┐
                │  Backend API Server   │
                │  /api/v1/user/income  │
                └───────────────────────┘

User Actions:
  Add Income → Open IncomeFormModal → Submit → create() → Reload
  Edit Income → Open IncomeFormModal → Submit → update() → Reload
  Delete Income → Confirm → delete() → Reload
  View Details → Open IncomeDetailsModal
  Change Tax Year → getSummary() with new year
  Filter/Sort → Client-side filtering in IncomeList
```

---

## Component Props

### IncomePage (No props - Top level)

State managed internally:
- `incomes: Array` - All income entries
- `summary: Object` - Summary for selected tax year
- `selectedCountry: string` - 'UK' or 'SA'
- `selectedTaxYear: string` - e.g., '2024/25'
- `showFormModal: boolean`
- `showDetailsModal: boolean`
- `selectedIncome: Object | null`
- `loading: boolean`
- `saving: boolean`
- `error: string | null`
- `success: string | null`

### IncomeSummarySection

```javascript
{
  summary: {
    total_income_gbp: number,
    total_income_zar: number,
    total_tax_withheld_gbp: number,
    foreign_income_gbp: number,
    foreign_tax_credits_gbp: number,
    by_type: { [type]: amount },
    by_country: { [country]: amount }
  },
  taxYear: string,      // e.g., '2024/25'
  country: string,      // 'UK' or 'SA'
  loading: boolean
}
```

### IncomeList

```javascript
{
  incomes: Array<Income>,
  loading: boolean,
  onEdit: (income) => void,
  onDelete: (incomeId) => void,
  onViewDetails: (income) => void,
  selectedTaxYear: string,
  selectedCountry: string
}
```

### IncomeFormModal

```javascript
{
  income: Object | null,    // null for add, object for edit
  onSave: (formData) => void,
  onCancel: () => void,
  loading: boolean
}
```

### IncomeDetailsModal

```javascript
{
  income: Object,           // Income to display
  onEdit: (income) => void,
  onDelete: (incomeId) => void,
  onClose: () => void
}
```

### IncomeTaxYearSwitcher

```javascript
{
  country: string,          // 'UK' or 'SA'
  taxYear: string,          // e.g., '2024/25'
  onCountryChange: (country) => void,
  onTaxYearChange: (taxYear) => void
}
```

---

## Income Data Model

```javascript
{
  // Database fields (snake_case from backend)
  id: string,
  user_id: string,
  income_type: 'employment' | 'self_employment' | 'rental' | 'dividend' |
               'interest' | 'investment' | 'pension' | 'capital_gains' | 'other',
  source_country: 'UK' | 'ZA' | 'US' | 'EU' | 'OTHER',
  description: string,
  amount: number,
  currency: 'GBP' | 'ZAR' | 'USD' | 'EUR',
  frequency: 'annual' | 'monthly' | 'weekly' | 'quarterly' | 'one_time',
  uk_tax_year: string,      // e.g., '2024/25'
  sa_tax_year: string,      // e.g., '2024/2025'
  is_gross: boolean,
  tax_withheld_at_source: number | null,
  paye_reference: string | null,
  start_date: string,       // ISO date
  end_date: string | null,  // ISO date or null
  related_entity: string | null,

  // Calculated fields
  gbp_amount: number,
  zar_amount: number,
  exchange_rate_used: number,
  exchange_rate_date: string,

  // Metadata
  deleted: boolean,
  created_at: string,
  updated_at: string
}
```

---

## User Workflows

### 1. View Income Summary

```
User → Navigate to /income
  ↓
Page loads → Fetch incomes + summary
  ↓
Display summary for current tax year
  ↓
User selects different tax year
  ↓
Fetch new summary → Update display
```

### 2. Add New Income

```
User → Click "Add Income"
  ↓
IncomeFormModal opens
  ↓
User fills form
  ↓
User clicks "Add Income"
  ↓
Validation passes → API call to create()
  ↓
Success → Close modal → Reload data → Show success message
```

### 3. Edit Existing Income

```
User → Click "Edit" on income card
  ↓
IncomeFormModal opens with pre-filled data
  ↓
User modifies fields
  ↓
User clicks "Update Income"
  ↓
Validation passes → API call to update()
  ↓
Success → Close modal → Reload data → Show success message
```

### 4. View Income Details

```
User → Click on income card
  ↓
IncomeDetailsModal opens
  ↓
Display full details + tax treatment
  ↓
User can:
  - Click "Edit" → Open IncomeFormModal
  - Click "Delete" → Confirm → Delete
  - Click "Close" → Close modal
```

### 5. Delete Income

```
User → Click "Delete" button
  ↓
Confirmation dialog appears
  ↓
User confirms
  ↓
API call to delete()
  ↓
Success → Reload data → Show success message
```

### 6. Filter and Sort

```
User → Select filter (type or country)
  ↓
Client-side filtering in IncomeList
  ↓
Display filtered results
  ↓
User → Select sort option
  ↓
Client-side sorting
  ↓
Display sorted results
```

---

## Styling Patterns

### Layout Containers

```css
narrativeSectionStyle = {
  padding: '32px',
  backgroundColor: '#FFFFFF',
  borderRadius: '12px',
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
  marginBottom: '24px',
  lineHeight: '1.7',
}
```

### Headings

```css
sectionHeadingStyle = {
  fontSize: '1.2rem',
  fontWeight: 600,
  color: '#0F172A',
  marginBottom: '16px',
}
```

### Metric Cards

```css
compactMetricStyle = {
  padding: '16px',
  backgroundColor: '#F8FAFC',
  borderRadius: '8px',
  border: '1px solid #E2E8F0',
}

metricValueStyle = {
  fontSize: '1.5rem',
  fontWeight: 'bold',
  color: '#0F172A',
  fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
}
```

### Callouts

```css
// Info (blue)
calloutStyle = {
  backgroundColor: '#EFF6FF',
  border: '1px solid #BFDBFE',
  borderLeft: '4px solid #3B82F6',
  padding: '16px',
  borderRadius: '8px',
}

// Success (green)
successCalloutStyle = {
  backgroundColor: '#F0FDF4',
  borderLeft: '4px solid #10B981',
  // ... rest same as calloutStyle
}
```

### Badges

```css
foreignBadgeStyle = {
  display: 'inline-flex',
  alignItems: 'center',
  padding: '4px 8px',
  borderRadius: '4px',
  fontSize: '0.75rem',
  fontWeight: 500,
  backgroundColor: '#DBEAFE',
  color: '#1E40AF',
}
```

### Forms

```css
formGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
  gap: '20px',
  marginBottom: '24px',
}
```

---

## Utility Functions Reference

### Currency Formatting

```javascript
formatCurrency(45000, 'GBP')  // → '£45,000.00'
formatCurrencyCompact(45000, 'GBP')  // → '£45.0k'
```

### Income Type Utilities

```javascript
getIncomeTypeIcon('employment')  // → '💼'
getIncomeTypeLabel('employment')  // → 'Employment'
getIncomeTypeColor('employment')  // → '#2563EB'
```

### Country Utilities

```javascript
getCountryFlag('UK')  // → '🇬🇧'
getCountryLabel('UK')  // → 'United Kingdom'
```

### Tax Year Utilities

```javascript
getCurrentUKTaxYear()  // → '2024/25'
getCurrentSATaxYear()  // → '2024/2025'
getRecentUKTaxYears(6)  // → ['2024/25', '2023/24', ...]
getUKTaxYearDates('2024/25')  // → { start: '6 April 2024', end: '5 April 2025' }
```

### Date and Amount Utilities

```javascript
formatDate('2024-04-01')  // → '1 April 2024'
formatFrequency('monthly')  // → 'Monthly'
calculateAnnualAmount(1000, 'monthly')  // → 12000
```

### Data Processing

```javascript
groupIncomeByType(incomes)  // → { employment: [...], rental: [...] }
groupIncomeByCountry(incomes)  // → { UK: [...], ZA: [...] }
calculateTotalIncome(incomes, 'GBP')  // → 52500
```

---

## File Organization

```
frontend/
├── src/
│   ├── components/
│   │   ├── income/
│   │   │   ├── IncomeTaxYearSwitcher.jsx
│   │   │   ├── IncomeSummarySection.jsx
│   │   │   ├── IncomeList.jsx
│   │   │   ├── IncomeFormModal.jsx
│   │   │   └── IncomeDetailsModal.jsx
│   │   └── Layout.jsx (updated)
│   ├── pages/
│   │   └── IncomePage.jsx
│   ├── utils/
│   │   ├── income.js (new)
│   │   └── api.js (updated)
│   └── App.jsx (updated)
│
└── tests/
    └── components/
        ├── IncomeSummarySection.test.jsx
        ├── IncomeList.test.jsx
        ├── IncomeFormModal.test.jsx
        ├── IncomeDetailsModal.test.jsx
        └── IncomePage.test.jsx
```

---

## Quick Reference: Key Features

### Multi-Currency Support
- ✅ Display in GBP, ZAR, USD, EUR
- ✅ Auto-conversion using exchange rates
- ✅ Show original + converted amounts
- ✅ Exchange rate date tracking

### Tax Year Handling
- ✅ UK tax year (6 Apr - 5 Apr)
- ✅ SA tax year (1 Mar - 28 Feb)
- ✅ Auto-allocation to tax years
- ✅ Historical tax years (6 years)

### Foreign Income
- ✅ Auto-detection
- ✅ Visual badges
- ✅ DTA explanations
- ✅ Tax credit tracking

### Educational Content
- ✅ Narrative explanations
- ✅ Contextual help text
- ✅ Tax treatment guidance
- ✅ Inline term definitions

### Responsive Design
- ✅ Mobile-first approach
- ✅ Touch-friendly (44px min)
- ✅ Adaptive layouts
- ✅ Hover states (desktop only)

### Accessibility
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ WCAG AA contrast
- ✅ Semantic HTML

---

**Last Updated:** 2025-10-02
**Version:** 1.0
**Status:** Production Ready

