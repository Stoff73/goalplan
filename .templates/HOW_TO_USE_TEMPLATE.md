# How to Use the Phase Template

**Template File:** `phase_template.md`

---

## Step 1: Copy and Rename Template

```bash
cp .templates/phase_template.md phase2_tasks.md
```

---

## Step 2: Replace All Placeholders

### Find and Replace:

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `[NUMBER]` | Phase number | `2` |
| `[PHASE NAME]` | Descriptive name | `Core Modules` |
| `[DATE]` | Current date | `October 1, 2025` |
| `[X-Y months]` | Timeline estimate | `4-5 months` |
| `[N-1]` | Previous phase number | `1` (for Phase 2) |
| `[N.1]`, `[N.2]`, etc. | Section numbers | `2.1`, `2.2`, etc. |
| `[Module/Section Name]` | Actual module name | `Protection Module` |
| `[Key deliverable X]` | Specific output | `Life assurance tracking` |

### Content Placeholders:

- `[One-sentence description...]` - Write clear goal
- `[Brief description...]` - Describe prerequisites
- `[Specific section to read]` - Reference exact section in context file
- `[Specific subtask X]` - Write detailed, actionable subtasks
- `[Clear acceptance criteria]` - Define when task is complete

---

## Step 3: Structure Your Phase

### Determine Sections

Based on your phase requirements, create sections for:

1. **Backend Data Models** - Database tables, migrations
2. **Business Logic Services** - Calculations, validations
3. **API Endpoints** - REST endpoints
4. **Frontend UI Components** - React components
5. **Integration** - Cross-module functionality

### Example Phase Structure:

```markdown
# PHASE 2: CORE MODULES

## 2.1 Protection Module - Data Models
### Task 2.1.1: Policy Data Models
### Task 2.1.2: Beneficiary Management

## 2.2 Protection Module - Business Logic
### Task 2.2.1: Coverage Calculation Service
### Task 2.2.2: Coverage Gap Analysis

## 2.3 Protection Module - API Endpoints
### Task 2.3.1: Policy CRUD Endpoints
### Task 2.3.2: Coverage Summary Endpoint

## 2.4 Protection Module - Frontend UI
### Task 2.4.1: Policy List Component
### Task 2.4.2: Add/Edit Policy Form
### Task 2.4.3: Coverage Gap Display

## 2.5 Investment Module - Data Models
[... continue pattern ...]
```

---

## Step 4: Write Tasks Following Pattern

### Backend Task Pattern:

```markdown
### Task X.Y.Z: [Descriptive Task Name]

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `ModuleName.md`, `Architecture.md`, `DataManagement.md`

**Agent Instructions:**
1. Read ModuleName.md - Feature X.Y: [Section name]
2. Read Architecture.md for [what to look for]
3. Read DataManagement.md for [specific requirement]
4. Implement exact [structure/endpoint/logic] from specification

**Tasks:**
- [ ] Create/Implement [specific deliverable 1]
- [ ] Create/Implement [specific deliverable 2]
- [ ] Add [supporting element]
- [ ] Configure [setting/parameter]
- [ ] **Test Suite:**
  - Test [happy path scenario]
  - Test [error scenario]
  - Test [edge case 1]
  - Test [edge case 2]
  - Test [performance requirement]
- [ ] **Run:** `pytest tests/[module]/test_[feature].py -v`
- [ ] **Acceptance:** [When is this 100% complete?]
```

### Frontend Task Pattern:

```markdown
### Task X.Y.Z: [UI Component Name]

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `ModuleName.md`, `UserFlows.md`

**Agent Instructions:**
1. Read ModuleName.md - User Flow section
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Follow React 19 patterns (no forwardRef)
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create [component name] component
- [ ] Import UI components from 'internal-packages/ui'
- [ ] [UI element 1 - be specific]
- [ ] [UI element 2]
- [ ] [State management details]
- [ ] Form validation for [fields]
- [ ] API integration with [endpoints]
- [ ] **Jest Tests:**
  - Test [component rendering]
  - Test [user interaction 1]
  - Test [user interaction 2]
  - Test [form validation]
  - Test [error states]
  - Test [loading states]
  - Mock all API calls
- [ ] **Manual Test:**
  - [Specific user action 1]
  - [Specific user action 2]
  - [Edge case to verify]
- [ ] **Component Test (Jest):** `tests/components/ComponentName.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/feature-name.spec.js`
- [ ] **Acceptance:** [Complete UI functionality description]
```

---

## Step 5: Create Testing Gates

### Intermediate Gates (for large phases)

Place after major sections (e.g., after completing Protection Module before starting Investment Module):

```markdown
## 🚦 PHASE X [MODULE NAME] TESTING GATE

### Security Tests (CRITICAL)
- [ ] ✅ [Module-specific security requirement]
- [ ] ✅ [Data encryption working]

### Functional Tests
- [ ] ✅ [Feature 1 works]
- [ ] ✅ [Feature 2 works]

### Integration Tests
- [ ] ✅ [End-to-end flow through module]

### Code Quality
- [ ] ✅ Test coverage >80%
- [ ] ✅ Linting passes

**Acceptance Criteria:**
🎯 [Module name] complete and tested
```

### Final Phase Gate

At the very end of the phase:

```markdown
## 🚦 PHASE X COMPLETE TESTING GATE

### Security Tests (CRITICAL)
- [ ] ✅ [Phase-wide security tests]

### Functional Tests
**Module 1:**
- [ ] ✅ [All features work]

**Module 2:**
- [ ] ✅ [All features work]

### Integration Tests
- [ ] ✅ Full user journey: [describe complete flow]
- [ ] ✅ Load test: [N] concurrent users

### Code Quality
- [ ] ✅ Test coverage >80% for all modules
- [ ] ✅ All linting passes
- [ ] ✅ API docs complete

### Performance Tests
- [ ] ✅ [Key screens] load in <[N] seconds
- [ ] ✅ API responses <500ms

### User Acceptance
- [ ] ✅ Can [complete key user flow]
- [ ] ✅ All error messages clear

**Acceptance Criteria:**
🎯 **Phase X Complete**: [What users can now do]
🎯 **Ready for Phase [X+1]**: System ready for next features
```

---

## Step 6: Reference Context Files Correctly

### Available Context Files (from SHARDS_README.md):

**Core Modules:**
- `userAuth.md`
- `UserInfo.md`
- `CentralDashboard.md`
- `Protection.md`
- `Savings.md`
- `Investment.md`
- `Retirement.md`
- `IHT.md`

**Tax & Compliance:**
- `CoreTaxCalcs.md`
- `DTA.md`
- `TaxResidency.md`
- `taxInformationModule.md`

**AI & Intelligence:**
- `AIAdvisoryRecommendation.md`
- `GoalPlanning.md`
- `ScenarioWhatif.md`
- `Personalization.md`

**Cross-Cutting:**
- `Architecture.md`
- `DataManagement.md`
- `securityCompliance.md`
- `performance.md`
- `UserFlows.md`
- `Notifications.md`
- `reporting.md`
- `integration.md`
- `roadmapConsideration.md`
- `successMetrics.md`
- `riskMitigation.md`

### How to Reference:

1. **Primary context file** - The main feature specification
2. **Architecture/design files** - For patterns and structure
3. **Security/compliance files** - For security requirements
4. **Performance files** - For performance targets

**Example:**
```markdown
**Context Files:** `Protection.md`, `Architecture.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Protection.md - Feature 4.1 complete section
2. Read Architecture.md for data model design patterns
3. Read securityCompliance.md for PII encryption requirements
```

---

## Step 7: Maintain Task Checkboxes

### How Checkboxes Work

**Unchecked (task not started or in progress):**
```markdown
- [ ] Create users table
```

**Checked (task complete):**
```markdown
- [x] Create users table
```

### Checking Off Tasks

As you complete each subtask, change `[ ]` to `[x]`:

**Before:**
```markdown
### Task 2.1.1: Policy Data Models

**Tasks:**
- [ ] Create life_assurance_policies table
- [ ] Create beneficiaries table
- [ ] Add indexes
- [ ] **Test Suite:**
  - Test policy creation
  - Test beneficiary assignment
- [ ] **Run:** `pytest tests/models/test_policy.py -v`
- [ ] **Acceptance:** Policy models complete
```

**After completing table creation:**
```markdown
### Task 2.1.1: Policy Data Models

**Tasks:**
- [x] Create life_assurance_policies table
- [x] Create beneficiaries table
- [x] Add indexes
- [ ] **Test Suite:**
  - Test policy creation
  - Test beneficiary assignment
- [ ] **Run:** `pytest tests/models/test_policy.py -v`
- [ ] **Acceptance:** Policy models complete
```

**After completing everything:**
```markdown
### Task 2.1.1: Policy Data Models

**Tasks:**
- [x] Create life_assurance_policies table
- [x] Create beneficiaries table
- [x] Add indexes
- [x] **Test Suite:**
  - Test policy creation
  - Test beneficiary assignment
- [x] **Run:** `pytest tests/models/test_policy.py -v`
- [x] **Acceptance:** Policy models complete
```

### Testing Gate Checkboxes

Similarly, check off testing gate items as they pass:

**Before:**
```markdown
### Security Tests (CRITICAL)
- [ ] ✅ Password hashing uses Argon2
- [ ] ✅ JWT tokens signed with RS256
```

**After verification:**
```markdown
### Security Tests (CRITICAL)
- [x] ✅ Password hashing uses Argon2
- [x] ✅ JWT tokens signed with RS256
```

---

## Example: Phase 2 Creation

### 1. Copy template
```bash
cp .templates/phase_template.md phase2_tasks.md
```

### 2. Set phase details
- Phase Number: 2
- Phase Name: Core Modules
- Timeline: 4-5 months
- Prerequisites: Phase 1 complete (authentication and user info working)

### 3. Define modules (from roadmapConsideration.md)
- Protection Module
- Investment Module
- Tax Intelligence Engine (Basic)
- Basic Recommendations

### 4. Create task structure
```
2.1 Protection Module - Data Models
2.2 Protection Module - Business Logic
2.3 Protection Module - API Endpoints
2.4 Protection Module - Frontend UI
2.5 Investment Module - Data Models
2.6 Investment Module - Business Logic
[... etc ...]
```

### 5. Write tasks using Protection.md and Investment.md as context files

### 6. Add testing gates after each major module

### 7. Add final Phase 2 complete testing gate

---

## Tips for Success

### ✅ Do:
- Be specific in task descriptions
- Reference exact sections in context files
- Include comprehensive test requirements
- Write clear acceptance criteria
- Use consistent formatting
- Keep delegation markers (`🐍` or `⚛️`) visible

### ❌ Don't:
- Be vague ("Implement feature")
- Skip context file references
- Forget test requirements
- Leave acceptance criteria unclear
- Mix backend and frontend in same task
- Remove delegation markers

### Best Practices:
1. **One task = One deliverable** - Keep tasks focused
2. **Tests are mandatory** - Every task must have tests
3. **Context files first** - Always list what to read
4. **Clear acceptance** - Define "done" explicitly
5. **Check as you go** - Mark checkboxes immediately when complete
6. **Test gates are blocking** - Don't skip them

---

## Automation Tip

You can use this template with a script to generate phase files faster:

```bash
# Future enhancement: Create a script that:
# 1. Reads phase requirements from YAML
# 2. Generates phase file from template
# 3. Populates tasks based on shard file structure
```

---

**Ready to create Phase 2?** Use the template and this guide! 🚀
