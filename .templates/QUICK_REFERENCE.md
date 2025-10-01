# Quick Reference Card

**Keep this open while developing** 📌

---

## Checkbox Syntax

| Markdown | Renders As | Meaning |
|----------|------------|---------|
| `- [ ]` | ☐ | Not done |
| `- [x]` | ☑ | Done |

**To complete a task:** Change `[ ]` to `[x]`

---

## Task Markers

| Marker | Agent | Use For |
|--------|-------|---------|
| 🐍 | `python-backend-engineer` | All Python/backend code |
| ⚛️ | `react-coder` | All React/frontend code |

---

## Testing Frameworks

| Code Type | Framework | What To Test |
|-----------|-----------|--------------|
| Python Backend | `pytest` | Unit, integration, load tests |
| React Components | `Jest` | Component unit, integration, snapshots |
| User Flows | `Playwright` | E2E user journeys only |

**Run Commands:**
```bash
# Backend
pytest tests/path/test_name.py -v

# Frontend component tests
npm test tests/components/ComponentName.test.jsx

# E2E tests
npx playwright test e2e/feature-name.spec.js
```

---

## Context Files Quick List

**For Backend Tasks:**
- Primary: `[ModuleName].md` (Protection, Savings, etc.)
- Architecture: `Architecture.md`, `DataManagement.md`
- Security: `securityCompliance.md`
- Performance: `performance.md`

**For Frontend Tasks:**
- Primary: `[ModuleName].md`
- UX: `UserFlows.md`
- Architecture: `Architecture.md`
- Performance: `performance.md`

**Full list:** `SHARDS_README.md`

---

## Task Completion Checklist

Before marking a task complete, verify:

- [x] All subtasks done
- [x] All tests written
- [x] All tests passing (100%)
- [x] Code linted (0 errors)
- [x] Context files followed exactly
- [x] Acceptance criteria met

**Only then:** Change `- [ ]` to `- [x]` ✅

---

## Testing Gate Checklist

Before proceeding to next phase:

- [x] All security tests pass
- [x] All functional tests pass
- [x] All integration tests pass
- [x] Code coverage >80%
- [x] All linting passes
- [x] Performance targets met
- [x] User acceptance verified

**If ANY are unchecked:** ⛔ DO NOT PROCEED

---

## Common Patterns

### Backend Task Structure
```markdown
**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Module.md`, `Architecture.md`

**Agent Instructions:**
1. Read Module.md - Section X
2. Read Architecture.md for patterns
3. Implement exact structure from spec

**Tasks:**
- [ ] Create [specific deliverable]
- [ ] Add [supporting element]
- [ ] **Test Suite:**
  - Test [scenario]
- [ ] **Run:** `pytest tests/path/test_file.py -v`
- [ ] **Acceptance:** [Clear criteria]
```

### Frontend Task Structure
```markdown
**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Module.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Module.md - User Flow section
2. Import from 'internal-packages/ui'
3. React 19 patterns (no forwardRef)
4. Write comprehensive Jest tests

**Tasks:**
- [ ] Create [component name]
- [ ] Import UI components from 'internal-packages/ui'
- [ ] [UI element]
- [ ] **Jest Tests:**
  - Test [behavior]
  - Mock all API calls
- [ ] **Component Test (Jest):** `tests/components/Name.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/feature.spec.js`
- [ ] **Acceptance:** [UI works completely]
```

---

## File Locations

```
project-root/
├── .claude/
│   ├── instructions.md          ← START HERE for all rules
│   └── agents/
│       ├── python-backend-engineer.md
│       └── react-coder.md
├── .templates/
│   ├── phase_template.md        ← Copy to create new phase
│   ├── HOW_TO_USE_TEMPLATE.md   ← Guide for template
│   ├── CHECKBOX_TRACKING.md     ← Progress tracking guide
│   └── QUICK_REFERENCE.md       ← This file
├── phase0_tasks.md              ← Setup phase
├── phase1_tasks.md              ← Foundation phase
├── TASKS_README.md              ← Overview of all phases
└── [Shard files]                ← Feature specifications
    ├── Protection.md
    ├── Savings.md
    ├── Investment.md
    └── [etc...]
```

---

## Critical Rules

### ⛔ NEVER:
- Proceed without all tests passing
- Skip testing gates
- Delete historical data (soft delete only)
- Use `forwardRef` in React 19
- Import from `@/components/ui` (use `internal-packages/ui`)
- Mark task complete if tests failing

### ✅ ALWAYS:
- Read context files before coding
- Write comprehensive tests
- Use appropriate agent (🐍 or ⚛️)
- Check boxes as you complete tasks
- Verify testing gates before proceeding
- Keep app functional at all times

---

## Quality Standards

### Code Coverage
- **Target:** >80%
- **Minimum:** 80%
- **Ideal:** 90%+

### Response Times
- **Login:** <200ms
- **API calls:** <500ms (95th percentile)
- **Dashboard:** <2 seconds
- **Calculations:** <100ms

### Bundle Sizes
- **Frontend:** <500KB gzipped
- **Initial load:** <3 seconds

---

## Security Checklist

Every task must consider:

- [ ] Input validation (Pydantic)
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] Rate limiting
- [ ] Authentication required
- [ ] Authorization checked
- [ ] Sensitive data encrypted
- [ ] PII protected

---

## React 19 Patterns

### ✅ Do:
```jsx
// Pass ref as regular prop
function MyInput({ ref, ...props }) {
  return <input ref={ref} {...props} />
}

// Import from correct location
import { Button } from 'internal-packages/ui/button'

// Avoid useEffect when possible
const derivedValue = computeFromProps(props)
```

### ❌ Don't:
```jsx
// No forwardRef in React 19
const MyInput = forwardRef((props, ref) => { ... })

// Wrong import location
import { Button } from '@/components/ui/button'

// Unnecessary useEffect
useEffect(() => {
  setValue(computeFromProps(props))
}, [props])
```

---

## Git Workflow (Optional)

```bash
# Create feature branch
git checkout -b phase1/task-1.1.1-user-models

# Commit as you complete subtasks
git add .
git commit -m "Create users table and migration"

# Mark task complete in phase file
# Change [ ] to [x] in phase1_tasks.md
git add phase1_tasks.md
git commit -m "Complete Task 1.1.1 - all tests passing"

# Push when ready
git push origin phase1/task-1.1.1-user-models
```

---

## Need Help?

| Question | Read This |
|----------|-----------|
| How do I delegate tasks? | `.claude/instructions.md` |
| How do I use the template? | `.templates/HOW_TO_USE_TEMPLATE.md` |
| How do I track progress? | `.templates/CHECKBOX_TRACKING.md` |
| What's in this phase? | `phase[N]_tasks.md` (header) |
| What features to build? | `[ModuleName].md` (shard files) |
| What's the overall plan? | `roadmapConsideration.md` |
| Testing strategy? | `.claude/instructions.md` |

---

## Daily Workflow

**Morning:**
1. ☑ Open current phase file
2. ☑ Find first unchecked task
3. ☑ Read context files listed
4. ☑ Understand requirements

**During Development:**
1. ☑ Implement code
2. ☑ Write tests
3. ☑ Run tests - fix failures
4. ☑ Check off subtasks: `[ ]` → `[x]`

**End of Day:**
1. ☑ Run all tests one more time
2. ☑ Commit progress
3. ☑ Update checkboxes in phase file
4. ☑ Review what's left for tomorrow

**End of Task:**
1. ☑ All subtasks checked
2. ☑ All tests passing (100%)
3. ☑ Code linted (0 errors)
4. ☑ Acceptance criteria met
5. ☑ Check final acceptance box ✅

**End of Phase:**
1. ☑ All tasks checked
2. ☑ Run full test suite
3. ☑ Verify testing gate (all checked)
4. ☑ Proceed to next phase! 🎉

---

**Print this and keep it visible while coding!** 📌
