# Financial Planning Application - Design Style Guide
## Narrative Storytelling Approach

> **Design Philosophy**: This application uses a narrative storytelling approach to make financial planning accessible, educational, and empowering. Every page should tell a story, explain the "why" behind the numbers, and guide users toward better financial decisions.

---

## 1. Design Principles

### Core Values

1. **Storytelling Over Data Display**
   - Lead with plain-language narratives that explain financial situations
   - Numbers support the story, they don't replace it
   - Use conversational tone: "You're worth £325,000" instead of "Net Worth: £325,000"
   - Every metric includes context: "That's increased by £7,500 since last month"
   - Frame data in terms of user goals and outcomes

2. **Educational by Default**
   - Teach users about financial concepts through use
   - Explain technical terms in plain English (IHT = Inheritance Tax)
   - Use callout boxes for tips and explanations
   - Link to deeper learning resources for curious users
   - Never assume financial literacy—meet users where they are

3. **Empowerment Through Understanding**
   - Help users understand the "why" behind recommendations
   - Celebrate wins and progress ("Great progress!")
   - Frame challenges as opportunities ("Good news: You can reduce this by...")
   - Build confidence through clear, actionable guidance
   - Reduce anxiety by simplifying complex topics

4. **Conversational & Human Tone**
   - Write like a trusted advisor speaking to a friend
   - Use "you" and "your" (second person)
   - Avoid financial jargon; use everyday language
   - Be warm and encouraging, not cold and technical
   - Show empathy: acknowledge that finance can be overwhelming

5. **Generous White Space & Readability**
   - Text-focused design requires excellent readability
   - Ample line spacing (1.7 for body text in narrative sections)
   - Short paragraphs (2-3 sentences max)
   - Cards for each narrative "chapter"
   - Sections clearly separated (48-64px gaps)

6. **Progressive Disclosure Through Narrative**
   - Start with the high-level story
   - Use expandable sections for deeper details
   - "Tell me more" links for additional context
   - Keep primary narrative simple; complexity is optional
   - Guide users through their financial journey step-by-step

---

## 2. Visual Design System

### Color Palette

#### Primary Colors
```css
--primary: #2563EB          /* Professional blue - primary actions, links */
--primary-dark: #1E40AF     /* Hover states, emphasis */
--primary-light: #60A5FA    /* Backgrounds, subtle highlights */
```

**Usage:**
- Primary buttons, key CTAs
- Active navigation items
- Interactive elements (links, accordions)
- Key metric highlights

#### Semantic Colors
```css
--success: #10B981          /* Green - positive metrics, growth */
--warning: #F59E0B          /* Amber - caution, attention needed */
--error: #EF4444            /* Red - negative values, alerts */
--info: #3B82F6             /* Blue - informational callouts */
```

**Financial Context:**
- **Green**: Portfolio growth, surplus, under budget, tax savings
- **Red**: Liabilities, deficits, IHT liability, over budget
- **Amber**: Warnings, approaching limits (pension annual allowance)
- **Blue**: Neutral information, educational content

#### Neutral Colors
```css
--text-primary: #0F172A     /* Headlines, primary content */
--text-secondary: #475569   /* Body text, descriptions */
--text-tertiary: #94A3B8    /* Labels, metadata, less important */
--text-inverse: #FFFFFF     /* Text on dark backgrounds */

--background: #FFFFFF       /* Page background (light mode) */
--background-secondary: #F8FAFC  /* Alternate sections */
--surface: #FFFFFF          /* Card backgrounds */
--surface-hover: #F1F5F9    /* Interactive card hover */

--border: #E2E8F0           /* Standard borders */
--border-light: #F1F5F9     /* Subtle dividers */
```

#### Dark Mode Considerations
- All components must support dark mode
- Dark mode uses: `background: #0F172A`, `surface: #1E293B`
- Reduce contrast slightly (softer whites: #E2E8F0)
- Semantic colors remain consistent (adjust opacity if needed)

### Typography

#### Font Families
```css
--font-primary: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif;
--font-mono: ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace;
```

**Usage:**
- Primary: All UI text, headings, body
- Monospace: Currency values, dates, account numbers, code

#### Font Scale
```css
--text-xs: 12px      /* Metadata, timestamps, footnotes */
--text-sm: 14px      /* Labels, secondary information */
--text-base: 16px    /* Body text, default */
--text-lg: 18px      /* Subheadings, emphasized text */
--text-xl: 20px      /* Card titles, section headers */
--text-2xl: 24px     /* Page titles (mobile) */
--text-3xl: 30px     /* Page titles (desktop) */
--text-4xl: 36px     /* Hero sections, marketing */
```

#### Font Weights
```css
--weight-normal: 400    /* Body text */
--weight-medium: 500    /* Emphasis, labels */
--weight-semibold: 600  /* Subheadings, buttons */
--weight-bold: 700      /* Headings, key metrics */
```

#### Typography Rules (Narrative Approach)
1. **Page Headlines**: Bold, 1.8-2rem, conversational (e.g., "Your Financial Health: Strong with room to optimize")
2. **Section Headings**: Semibold, 1.2-1.5rem, clear and descriptive (e.g., "Your Financial Position", "Your Inheritance Tax Situation")
3. **Body Text**: Normal weight, 1rem, generous line-height (1.7) for easy reading
4. **Narrative Paragraphs**: Color text-secondary (#475569), relaxed tone
5. **Emphasis**: Bold for key numbers within sentences, not standalone
6. **Metric Values**: When standalone, 1.8-2rem bold, but prefer in-sentence: "You're worth **£325,000**"
7. **Currency**: Monospace font, embedded in natural sentences
8. **Callout Boxes**: Slightly smaller (0.95rem), colored backgrounds for tips
9. **Line Height**: 1.7 for narrative text (more readable), 1.5 for standard UI text
10. **Letter Spacing**: Normal for readability; avoid tight spacing

### Spacing System

```css
--space-xs: 4px      /* Tight groupings, icon margins */
--space-sm: 8px      /* Related items, compact layouts */
--space-md: 16px     /* Standard padding, element gaps */
--space-lg: 24px     /* Card padding, section spacing */
--space-xl: 32px     /* Large card padding, major sections */
--space-xxl: 48px    /* Section dividers */
--space-xxxl: 64px   /* Major page sections */
```

#### Spacing Guidelines
- **Card padding**: 24px (medium cards), 32px (large cards)
- **Grid gaps**: 16px (mobile), 24px (desktop)
- **Section spacing**: 48-64px between major sections
- **Element margins**: 8px between related items, 16px between unrelated

### Border Radius

```css
--radius-sm: 4px     /* Small elements, tags */
--radius-md: 8px     /* Inputs, buttons */
--radius-lg: 12px    /* Cards, modals */
--radius-xl: 16px    /* Large cards, hero sections */
--radius-full: 9999px /* Pills, avatars */
```

### Shadows

```css
--shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05)     /* Subtle depth */
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06)     /* Cards */
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07)     /* Hover states */
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1)    /* Modals */
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1)    /* Dropdowns */
--shadow-inner: inset 0 2px 4px rgba(0, 0, 0, 0.06) /* Pressed states */
```

**Usage:**
- Default cards: shadow-sm
- Hoverable cards: shadow-sm → shadow-md on hover
- Modals/overlays: shadow-lg or shadow-xl
- Avoid heavy shadows (trust = stability, not floating)

### Animations & Transitions

```css
--transition-fast: 150ms ease-in-out    /* Micro-interactions */
--transition-normal: 250ms ease-in-out  /* Standard transitions */
--transition-slow: 350ms ease-in-out    /* Page transitions */
```

**Animation Principles:**
1. **Subtle, not showy**: Animations reinforce hierarchy, not distract
2. **Fast micro-interactions**: Button hover, input focus (150ms)
3. **Standard transitions**: Card expand, tab switch (250ms)
4. **Page transitions**: Route changes, modal open (350ms)
5. **Loading states**: Skeleton loaders, not spinners (when possible)

---

## 3. Component Patterns (Narrative Storytelling)

### Narrative Section Cards

**Purpose**: Primary container for story sections (each "chapter" of the financial story)

**Variants:**
```typescript
<NarrativeSection>           // Default: 24px padding, generous spacing
<NarrativeSection highlight> // With colored left border for emphasis
<NarrativeSection expandable> // Collapsible for optional details
```

**Anatomy:**
- **Heading**: Clear, conversational title (h3, 1.2rem) - e.g., "Your Financial Position"
- **Narrative Paragraphs**: 2-3 sentences, line-height 1.7
- **Embedded Metrics** (optional): Small metric cards or inline bold numbers
- **Callout Boxes** (optional): Tips, explanations, or warnings
- **CTA Buttons** (optional): "Explore IHT Planning →" or "Learn More"
- **Expandable Content** (optional): "Tell me more" sections

**Guidelines:**
- Use border-radius-lg (12px)
- White background with subtle shadow
- Generous padding (32px) for comfortable reading
- Each section tells one story/concept
- Clear, descriptive headings without decorative elements
- Keep paragraphs short (2-3 sentences max)

### Buttons

**Variants:**
```typescript
<Button variant="primary">   // Primary actions (blue background)
<Button variant="secondary"> // Secondary actions (outlined)
<Button variant="ghost">     // Tertiary actions (no background)
<Button variant="danger">    // Destructive actions (red)
```

**Sizes:**
```typescript
<Button size="small">   // 8px/16px padding, 14px text
<Button size="medium">  // 16px/24px padding, 16px text (default)
<Button size="large">   // 24px/32px padding, 18px text
```

**Guidelines:**
- Primary buttons: 1 per section maximum
- Always provide hover/active states
- Loading state: button becomes disabled, shows spinner
- Full-width on mobile for primary CTAs

### Inline Metrics (Narrative Style)

**Purpose**: Display metrics within narrative context, not standalone

**Preferred Approach - Embedded in Narrative:**
```html
<p>
  You're worth <strong>£325,000</strong> after debts. That's increased by
  <strong style="color: #10B981;">£7,500</strong> since last month - great progress!
</p>
```

**Secondary Approach - Compact Metric Grid:**
When showing multiple related metrics, use small cards within narrative sections:
```html
<MetricGrid>
  <CompactMetric>
    <MetricValue>£325k</MetricValue>
    <MetricLabel>Net Worth</MetricLabel>
  </CompactMetric>
  <CompactMetric>
    <MetricValue>£125k</MetricValue>
    <MetricLabel>Pensions</MetricLabel>
  </CompactMetric>
</MetricGrid>
```

**Typography:**
- In-sentence bold: 1rem, bold weight, inline with text
- Standalone compact metrics: 1.5-1.8rem (smaller than traditional dashboards)
- Labels: 0.75rem, normal case (not uppercase), text-secondary
- No "change" indicators - describe changes in narrative text instead

**Guidelines:**
- PREFER: Metrics embedded in sentences with context
- Use standalone metrics sparingly (only for supporting data grids)
- Always explain what the number means in plain language
- Celebrate positive changes with encouraging language

### Data Tables

**Purpose**: Display tabular financial data

**Features:**
- Sortable columns (click header to sort)
- Pagination for >20 rows
- Row hover state (background: surface-hover)
- Sticky header on scroll

**Typography:**
- Header: Semibold, text-sm, text-secondary
- Body: Normal, text-sm, text-primary
- Numeric columns: Right-aligned, monospace

**Guidelines:**
- Zebra striping optional (use sparingly)
- Minimum row height: 48px (touch-friendly)
- Borders: subtle (border-light) or none
- Mobile: Convert to card-based list

### Forms & Inputs

**Input Variants:**
```typescript
<Input type="text" />       // Standard text input
<Input type="currency" />   // Currency with £ prefix
<Input type="date" />       // Date picker
<Select>                    // Dropdown
<Textarea>                  // Multi-line text
```

**Guidelines:**
- Label above input (never inside placeholder)
- Help text below input (text-secondary, text-sm)
- Error state: Red border, error message below
- Focus state: Primary color border, subtle glow
- Minimum height: 44px (touch-friendly)

### Charts & Data Visualization (Supporting Role)

**Philosophy**: Charts support the narrative, they don't replace it. Always pair visualizations with explanatory text.

**Chart Usage:**
1. **Bar Chart**: Use sparingly for simple comparisons (max 5-6 bars)
2. **Donut Chart**: For proportions, with narrative explaining the breakdown
3. **Line Chart**: For trends, with story about what the trend means
4. **Avoid**: Complex multi-line charts, stacked charts, or data-dense visualizations

**Chart Integration Pattern:**
```html
<NarrativeSection>
  <h3>Your Financial Position</h3>
  <p>
    You're worth <strong>£325,000</strong> after debts. Your main wealth
    comes from your property (£170k) and pensions (£125k).
  </p>

  <!-- Supporting visual -->
  <CompactMetricGrid>
    <Metric value="£325k" label="Net Worth" />
    <Metric value="£125k" label="Pensions" />
    <Metric value="£170k" label="Property" />
  </CompactMetricGrid>
</NarrativeSection>
```

**Guidelines:**
- Text first, charts second
- Keep charts simple and uncluttered
- Always explain what the chart shows before displaying it
- Use semantic colors with narrative meaning (green=good, red=attention needed)
- Avoid chartjunk: no 3D effects, minimal gridlines, clean legends

---

## 4. Layout Patterns

### Grid System

**Desktop (>1024px):**
```css
display: grid;
grid-template-columns: repeat(12, 1fr);  /* 12-column grid */
gap: 24px;
```

**Tablet (768-1024px):**
```css
grid-template-columns: repeat(6, 1fr);   /* 6-column grid */
gap: 16px;
```

**Mobile (<768px):**
```css
grid-template-columns: 1fr;              /* Single column */
gap: 16px;
```

### Page Structure

```
┌─────────────────────────────────────┐
│ Header (80px fixed)                 │
├─────────────────────────────────────┤
│ Page Content (max-width: 1280px)    │
│ ┌─────────────────────────────────┐ │
│ │ Page Title (2rem, 32px margin)  │ │
│ ├─────────────────────────────────┤ │
│ │ Metrics Grid (4 columns)        │ │
│ ├─────────────────────────────────┤ │
│ │ Section 1 (48px margin-top)     │ │
│ │ [Cards in responsive grid]      │ │
│ ├─────────────────────────────────┤ │
│ │ Section 2 (48px margin-top)     │ │
│ │ [Content]                       │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Container Widths

```css
--container-sm: 640px   /* Narrow forms, auth pages */
--container-md: 768px   /* Standard content */
--container-lg: 1024px  /* Wide layouts */
--container-xl: 1280px  /* Dashboard, full-width */
```

### White Space Usage

**Generous white space = Trust and clarity**

- **Page margins**: 32px (desktop), 16px (mobile)
- **Section spacing**: 48-64px between major sections
- **Card spacing**: 24px gap in grid layouts
- **Element spacing**: 16px between unrelated elements

---

## 5. Progressive Disclosure Patterns (Narrative Approach)

### Pattern 1: Story Chapters

**Philosophy**: Break complex financial topics into digestible "chapters" of the story

**Implementation:**
- Each major topic (wealth, IHT, retirement) is a separate narrative section card
- Start with high-level narrative, then provide supporting details
- Use "Tell me more" or "Learn how →" links for optional deep dives

**Example:**
```html
<NarrativeSection>
  <h3>Your Inheritance Tax Situation</h3>
  <p>
    Based on your £425k estate, you'd owe <strong>£45,000 in IHT</strong>
    if you passed away today. That's because your estate exceeds the £325k threshold.
  </p>

  <!-- Optional expandable detail -->
  <ExpandableDetail trigger="Tell me more about IHT">
    <p>Inheritance Tax (IHT) is charged at 40% on estates above £325,000...</p>
  </ExpandableDetail>

  <Button>Explore IHT Planning Strategies →</Button>
</NarrativeSection>
```

### Pattern 2: Callout Boxes for Tips

**Use for:**
- Educational tips ("Good news: You can reduce this by...")
- Warnings ("Important: Complete this before tax year end")
- Celebrations ("Great work! You're on track")

**UI:**
```html
<Callout type="tip">
  <strong>Good news: You can reduce this by:</strong>
  <ul>
    <li>Making gifts now (7-year rule)</li>
    <li>Using your £175k residence allowance</li>
    <li>Charitable giving (reduces tax to 36%)</li>
  </ul>
</Callout>
```

**Guidelines:**
- Use colored backgrounds (blue=tip, amber=warning, green=success)
- 4px left border for visual emphasis
- Keep text concise (3-5 bullet points max)
- Link to deeper resources when appropriate

### Pattern 3: Expandable "Tell Me More" Sections

**Use for:**
- Technical explanations
- Historical context
- Advanced options
- Calculation methodologies

**UI:**
```html
<ExpandableSection>
  <Trigger>Tell me more about pension annual allowance →</Trigger>
  <Content>
    <p>The annual allowance is the maximum you can contribute...</p>
  </Content>
</ExpandableSection>
```

**Guidelines:**
- Default to collapsed
- Use conversational trigger text ("Tell me more", "How does this work?")
- Smooth 250ms transition
- Chevron icon (▶ → ▼) to show state

### Pattern 4: "What Should I Do Next" Sections

**Use for:**
- Actionable recommendations
- Next steps
- Prioritized task lists

**UI:**
```html
<ActionSection>
  <h3>What You Should Do Next</h3>
  <ol>
    <li>Review your IHT situation (potential £45k savings)</li>
    <li>Max out pension contributions (£25k allowance remaining)</li>
    <li>Consider ISA investment (£8k cash could work harder)</li>
  </ol>
</ActionSection>
```

**Guidelines:**
- Always provide 2-4 specific, actionable items
- Explain the "why" (benefit) alongside the "what" (action)
- Use numbered lists for priority order
- Include links to relevant pages

### Pattern 5: Inline Term Explanations

**Use for:**
- Technical jargon
- Acronyms (IHT, RNRB, ISA)
- Financial concepts

**UI:**
```html
<p>
  Your estate exceeds the <Term definition="The tax-free threshold for inheritance tax, currently £325,000 per person">nil-rate band</Term> by £100k.
</p>
```

**Guidelines:**
- Underline or subtle dotted underline for defined terms
- Tooltip appears on hover (desktop) or tap (mobile)
- 1-2 sentence definition, plain language
- Optional "Learn more →" link to full article

---

## 6. Navigation & User Flow

### Primary Navigation

**Desktop Header:**
```
┌─────────────────────────────────────────────────┐
│ Logo    Dashboard  IHT  Pensions  Reports  •••  │
└─────────────────────────────────────────────────┘
```

**Mobile:**
- Hamburger menu (top-left)
- Logo (center)
- User avatar (top-right)

### Navigation Hierarchy

1. **Primary Nav** (Header): Main sections (Dashboard, IHT, Pensions, etc.)
2. **Secondary Nav** (Sidebar or tabs): Sub-sections within main area
3. **Tertiary Nav** (In-page): Tabs, accordions, anchors

### Breadcrumbs

**Use for:**
- Deep navigation (3+ levels)
- Complex wizards

**Format:**
```
Home > IHT Planning > 7-Year Gift Timeline > Edit Gift
```

**Guidelines:**
- Text-sm, text-secondary
- Separator: "/" or ">"
- Current page: text-primary, not clickable
- Max 4 levels before collapsing

### User Flow Principles

1. **Clear entry points**: Dashboard has clear "Quick Actions" for all features
2. **No dead ends**: Every page has next action or back button
3. **Persistent context**: Breadcrumbs, page titles always visible
4. **Confirmation for destructive actions**: Modal dialog for delete/archive
5. **Auto-save**: Forms save drafts automatically (with indicator)

---

## 7. Interaction Patterns

### Hover States

**Cards:**
- Transform: translateY(-2px)
- Shadow: shadow-sm → shadow-md
- Transition: 250ms ease-in-out

**Buttons:**
- Background: primary → primary-dark
- Transform: subtle scale(1.02) for large buttons
- Transition: 150ms ease-in-out

**Links:**
- Color: primary → primary-dark
- Text-decoration: underline on hover
- Transition: 150ms

### Active/Pressed States

**Buttons:**
- Shadow: shadow-inner (pressed appearance)
- Transform: scale(0.98)
- Transition: 100ms (fast)

### Focus States (Accessibility)

**All interactive elements:**
- Outline: 2px solid primary color
- Outline-offset: 2px
- Remove default browser outline
- Never remove focus indicator without replacement

**Input fields:**
- Border: 2px solid primary
- Subtle box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1)

### Loading States

**Page Load:**
- Skeleton loaders (match content layout)
- Avoid full-screen spinners
- Show structure immediately

**Button Actions:**
- Button text → spinner
- Button disabled during load
- Re-enable after success/error

**Data Updates:**
- Show "Last updated: 2 mins ago" timestamp
- Subtle refresh icon (spin on click)
- Toast notification for background updates

### Error States

**Form Validation:**
- Red border on input
- Error message below (red, text-sm)
- Icon: ⚠️ or ✕

**Page Errors:**
- Error boundary with friendly message
- "Go to Dashboard" button
- Contact support link

**Empty States:**
- Illustration or icon
- Helpful message: "No data yet. Add your first pension →"
- Primary CTA to add content

---

## 8. Content Writing Guidelines (Narrative Storytelling)

### Voice & Tone

**Voice** (consistent across all content):
- **Human & Conversational**: Write like a trusted advisor, not a robot
- **Educational**: Teach, don't lecture
- **Empowering**: Build confidence, reduce anxiety
- **Clear & Direct**: No jargon, no fluff

**Tone** (adjusts by context):
- **Dashboard**: Warm, encouraging ("Great progress!", "You're on track")
- **Warnings**: Helpful, not scary ("Here's how to reduce this")
- **Education**: Patient, supportive ("Let me explain...")
- **Celebrations**: Enthusiastic ("Excellent work!")

### Writing Patterns

**DO:**
- ✅ "You're worth £325,000 after debts"
- ✅ "That's increased by £7,500 since last month - great progress!"
- ✅ "Good news: You can reduce this by..."
- ✅ "You're on track for a comfortable retirement!"
- ✅ "Based on your £425k estate, you'd owe £45,000 in IHT"

**DON'T:**
- ❌ "Net Worth: £325,000"
- ❌ "Estate value has increased 2.3%"
- ❌ "IHT liability exists"
- ❌ "Retirement projection: £40,000 annually"
- ❌ "Current IHT exposure: £45,000"

### Financial Data Formatting

**Currency in Sentences:**
```html
<p>You're worth <strong>£325,000</strong> after debts.</p>
<p>Your estate would owe <strong>£45,000 in IHT</strong>.</p>
```
- Use monospace font for numbers
- Bold for emphasis
- Always provide context (what the number represents)

**Large Numbers:**
- In narrative: "£325,000" (full amount for clarity)
- In compact metrics: "£325k" (shortened is okay)

**Percentages:**
- Describe changes narratively: "increased by 2.3%" not "+2.3%"
- Use semantic colors: green for positive, red for concerning

**Dates:**
- Conversational: "since last month", "this tax year"
- When specific: "15 March 2024" (readable format)

### Content Structure

**Page Headlines:**
- Conversational and status-oriented
- Examples: "Your Financial Health: Strong with room to optimize"
- "You're on track for retirement, with a few optimizations available"

**Section Headings:**
- Clear, descriptive titles: "Your Financial Position"
- "Your Inheritance Tax Situation"
- "Your Retirement Outlook"

**Paragraphs:**
- 2-3 sentences maximum
- One idea per paragraph
- Use bold for key numbers/terms
- End with context or implication

**Lists:**
- Use bullets for options/tips
- Use numbers for sequential steps/priorities
- Keep items parallel in structure
- 3-5 items maximum per list

### Chart Best Practices

**Bar Charts:**
- Horizontal bars for long category names
- Vertical bars for time series
- Start Y-axis at 0 (never truncate)
- Max 10-12 bars (use pagination if more)

**Donut Charts:**
- Center KPI: Large metric value
- Max 8 segments (combine small values into "Other")
- Legend: To right or below
- Show percentages in legend

**Line Charts:**
- Max 4 lines per chart (reduce clutter)
- Different line styles (solid, dashed) for accessibility
- Show data points on hover
- Grid lines: subtle (border-light color)

**Area Charts:**
- Stacked for cumulative values
- Semi-transparent fill (opacity: 0.6)
- Solid line at top edge
- Tooltip shows all stack values on hover

### Accessibility in Charts

1. **Color is not the only indicator**: Use patterns, icons, labels
2. **High contrast**: All colors meet WCAG AA (4.5:1)
3. **Keyboard navigation**: Arrow keys to navigate data points
4. **Screen reader support**: Provide data table alternative
5. **Responsive**: Touch targets 44x44px minimum on mobile

---

## 9. Mobile-First Considerations

### Responsive Breakpoints

```css
--mobile: 480px      /* Small phones */
--tablet: 768px      /* Tablets, large phones */
--desktop: 1024px    /* Desktop, laptops */
--wide: 1280px       /* Large desktops */
```

### Mobile Design Rules

1. **Single column**: Stack cards vertically
2. **Larger touch targets**: Min 44x44px
3. **Simplified navigation**: Hamburger menu
4. **Reduce data density**: Show fewer metrics, prioritize key info
5. **Bottom navigation**: Quick actions at thumb-reach
6. **Full-width buttons**: Primary CTAs span full width

### Progressive Enhancement

**Mobile First:**
- Design for mobile constraints
- Add features as screen size increases
- Never hide essential features on mobile

**Desktop Enhancements:**
- Multi-column layouts
- Hover states
- Keyboard shortcuts
- Sidebars, contextual panels

---

## 10. Accessibility Standards

### WCAG 2.1 Level AA Compliance

**Color Contrast:**
- Text: 4.5:1 minimum (normal text)
- Large text: 3:1 minimum (18px+ or 14px+ bold)
- UI components: 3:1 minimum (borders, icons)

**Keyboard Navigation:**
- All interactive elements focusable
- Logical tab order (top-to-bottom, left-to-right)
- Skip navigation link (first focusable element)
- No keyboard traps

**Screen Reader Support:**
- Semantic HTML (header, nav, main, article, etc.)
- Alt text for images
- ARIA labels for icons/interactive elements
- Form labels properly associated

**Focus Indicators:**
- Visible focus state for all interactive elements
- High contrast (primary color outline)
- Never remove without alternative

**Motion:**
- Respect prefers-reduced-motion
- Disable animations for users with motion sensitivity

---

## 11. Implementation Checklist

### Before Launching a New Feature

- [ ] Follows design system (colors, typography, spacing)
- [ ] Responsive (tested on mobile, tablet, desktop)
- [ ] Dark mode support
- [ ] Keyboard navigation works
- [ ] Screen reader tested (at least NVDA or VoiceOver)
- [ ] Loading states implemented
- [ ] Error states handled
- [ ] Empty states designed
- [ ] Success feedback (toast or message)
- [ ] Progressive disclosure applied (advanced features collapsed)
- [ ] Consistent with navigation patterns
- [ ] No console errors/warnings
- [ ] Performance tested (Lighthouse score >90)

---

## 12. Resources & Tools

### Design Tools
- **Figma**: For mockups and prototypes
- **Adobe Color**: For color palette testing (contrast ratios)
- **WebAIM Contrast Checker**: WCAG compliance verification

### Development Tools
- **Styled-components**: Component styling (already in use)
- **React Icons**: Icon library (consistent icons)
- **Recharts or Chart.js**: Data visualization
- **React Hook Form**: Form management
- **React Query**: Data fetching and caching

### Testing Tools
- **Lighthouse**: Performance, accessibility audits
- **NVDA/JAWS**: Screen reader testing (Windows)
- **VoiceOver**: Screen reader testing (macOS/iOS)
- **axe DevTools**: Accessibility testing browser extension

---

## 13. Maintenance & Evolution

### Quarterly Design Review
- Review new patterns that have emerged
- Update this guide with new components
- Remove deprecated patterns
- User feedback integration

### Version Control
- All design changes logged
- Breaking changes flagged
- Migration guides for major updates

### Communication
- Announce design system updates to team
- Maintain component library (Storybook recommended)
- Documentation always kept current

---

---

## 14. Narrative Storytelling Examples

### Example 1: Dashboard Opening

**Traditional Approach (❌):**
```
Dashboard
Net Worth: £325,000
Monthly Income: £7,500
Monthly Expenses: £4,200
```

**Narrative Approach (✅):**
```
Your Financial Health: Strong with room to optimize

Based on your latest data, your net worth grew by £7,500 this month.
That's great progress! Here's what that means for your long-term goals...
```

### Example 2: IHT Warning

**Traditional Approach (❌):**
```
IHT Liability: £45,000
Estate Value: £425,000
NRB Used: 100%
```

**Narrative Approach (✅):**
```
Your Inheritance Tax Situation

Based on your £425k estate, you'd owe £45,000 in IHT if you passed away today.
That's because your estate exceeds the £325k threshold.

Good news: You can reduce this by:
• Making gifts now (7-year rule)
• Using your £175k residence allowance
• Charitable giving (reduces tax to 36%)

[Explore IHT Planning Strategies →]
```

### Example 3: Retirement Status

**Traditional Approach (❌):**
```
Pension Value: £450,000
Projected Income: £28,500/year
State Pension: £11,500/year
Total Income: £40,000/year
Target: £35,000/year
Status: On Track ✓
```

**Narrative Approach (✅):**
```
Your Retirement Outlook

You're on track for a comfortable retirement! Your £450k in pensions should
provide £25-30k annual income from age 65 (assuming 4% withdrawal rate).

Your current retirement age: 65
Projected annual income: £28,500/year
State pension: +£11,500/year (from age 67)
Total: £40,000/year — Meets your £35k goal

[See Full Retirement Projection →]
```

### Example 4: Action Items

**Traditional Approach (❌):**
```
Recommended Actions:
- Review IHT
- Pension contribution
- ISA investment
```

**Narrative Approach (✅):**
```
What You Should Do Next

1. Review your IHT situation (potential £45k savings)
2. Max out pension contributions (£25k allowance remaining)
3. Consider ISA investment (£8k cash could work harder)

Each of these actions could significantly improve your financial position.
Let's start with the first one.
```

---

## 15. Implementation Checklist (Narrative Storytelling)

### Content Review
- [ ] Uses conversational, second-person language ("you", "your")
- [ ] Explains the "why" behind every number
- [ ] Celebrates wins and frames challenges positively
- [ ] Clear, descriptive headings without decorative elements
- [ ] Paragraphs are 2-3 sentences maximum
- [ ] Technical terms defined in plain language
- [ ] Callout boxes for tips and explanations
- [ ] Clear "What to do next" guidance

### Visual Design
- [ ] Narrative section cards with generous padding (32px)
- [ ] Line height 1.7 for body text (readability)
- [ ] Metrics embedded in sentences, not standalone
- [ ] Colored callout boxes for tips/warnings
- [ ] White space between sections (48-64px)
- [ ] Supporting visuals (compact metric grids) follow narrative
- [ ] Expandable sections for optional details

### Interaction
- [ ] "Tell me more" links for educational content
- [ ] "Learn how →" buttons for deeper dives
- [ ] Inline term definitions (tooltips)
- [ ] Progressive disclosure (complexity is optional)
- [ ] Clear next-action CTAs

### Standard Checklist (All Pages)
- [ ] Responsive (mobile, tablet, desktop)
- [ ] Dark mode support
- [ ] Keyboard navigation
- [ ] Screen reader friendly
- [ ] Loading states
- [ ] Error states with helpful guidance
- [ ] No console errors
- [ ] Performance (Lighthouse >90)

---

**Version:** 1.0 (Narrative Storytelling)
**Last Updated:** January 2025
**Dashboard Approach:** Option 5 - Narrative Storytelling
**Maintained By:** Design & Engineering Team