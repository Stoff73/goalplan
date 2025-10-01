# Phase [NUMBER]: [PHASE NAME]

**Last Updated:** [DATE]
**Timeline:** [X-Y months]
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT PHASE UNTIL ALL TESTS PASS** ⛔

---

## 📋 Overview

**Goal:** [One-sentence description of what this phase delivers]

**Prerequisites:** Phase [N-1] complete ([brief description of what must be done first])

**Modules Included:**
- [N.1]: [Module/Section Name]
- [N.2]: [Module/Section Name]
- [N.3]: [Module/Section Name]
- [Add more as needed...]

**Outputs:**
- [Key deliverable 1]
- [Key deliverable 2]
- [Key deliverable 3]
- [Add more specific outputs...]

---

## 🔧 Instructions

**Before starting any task:**
1. Read `.claude/instructions.md` for complete agent delegation rules and testing strategy
2. Each task below marked with 🐍 or ⚛️ shows which agent to use
3. Read all listed "Context Files" before implementing

**Task markers:**
- 🐍 = Delegate to `python-backend-engineer` agent
- ⚛️ = Delegate to `react-coder` agent

**Testing:**
- Backend: `pytest` for all Python code
- Frontend: `Jest` for component tests, `Playwright` for E2E only
- See `.claude/instructions.md` for complete testing strategy

---

# PHASE [NUMBER]: [PHASE NAME IN CAPS]

## [N.1] [First Major Section Name]

### Task [N.1.1]: [Task Name]

**🐍 DELEGATE TO: `python-backend-engineer`**  *(or ⚛️ for React tasks)*
**Context Files:** `[file1].md`, `[file2].md`, `[file3].md`

**Agent Instructions:**
1. Read [file1].md - [Specific section to read]
2. Read [file2].md for [what to look for]
3. Read [file3].md for [additional context]
4. [Specific implementation instruction]

**Tasks:**
- [ ] [Specific subtask 1]
- [ ] [Specific subtask 2]
- [ ] [Specific subtask 3]
- [ ] **Test Suite:**
  - Test [scenario 1]
  - Test [scenario 2]
  - Test [edge case 1]
  - Test [edge case 2]
- [ ] **Run:** `pytest tests/[path]/test_[name].py -v` *(or npm test for React)*
- [ ] **Acceptance:** [Clear acceptance criteria]

### Task [N.1.2]: [Next Task Name]

**🐍 DELEGATE TO: `python-backend-engineer`**  *(or ⚛️ for React tasks)*
**Context Files:** `[file1].md`, `[file2].md`

**Agent Instructions:**
1. [Instruction 1]
2. [Instruction 2]
3. [Instruction 3]

**Tasks:**
- [ ] [Subtask 1]
- [ ] [Subtask 2]
- [ ] **Test Suite:**
  - Test [scenario]
  - Test [scenario]
- [ ] **Run:** `pytest tests/[path]/test_[name].py -v`
- [ ] **Acceptance:** [Criteria]

---

## [N.2] [Second Major Section Name]

### Task [N.2.1]: [Task Name]

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `[file1].md`, `[file2].md`

**Agent Instructions:**
1. [Instruction 1]
2. [Instruction 2]

**Tasks:**
- [ ] [Subtask 1]
- [ ] [Subtask 2]
- [ ] **Test Suite:**
  - Test [scenario]
- [ ] **Run:** `pytest tests/[path]/test_[name].py -v`
- [ ] **Acceptance:** [Criteria]

---

## [N.X] Frontend: [UI Section Name]

### Task [N.X.1]: [UI Component Name]

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `[module].md`, `UserFlows.md`

**Agent Instructions:**
1. Read [module].md - [Section]
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Follow React 19 patterns (no forwardRef)
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create [component name] component
- [ ] Import UI components from 'internal-packages/ui'
- [ ] [UI element 1]
- [ ] [UI element 2]
- [ ] [State management requirement]
- [ ] [API integration requirement]
- [ ] **Jest Tests:**
  - Test [component behavior 1]
  - Test [component behavior 2]
  - Test [error state]
  - Test [loading state]
  - Mock all API calls
- [ ] **Manual Test:**
  - [User action 1]
  - [User action 2]
  - [User action 3]
- [ ] **Component Test (Jest):** `tests/components/[ComponentName].test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/[feature-name].spec.js`
- [ ] **Acceptance:** [UI works completely with all interactions]

---

## 🚦 PHASE [NUMBER] [SECTION NAME] TESTING GATE

*(Include intermediate testing gates for major sections if phase is large)*

### Security Tests (CRITICAL)

- [ ] ✅ [Security requirement 1]
- [ ] ✅ [Security requirement 2]
- [ ] ✅ [Security requirement 3]

### Functional Tests

- [ ] ✅ [Feature 1 works]
- [ ] ✅ [Feature 2 works]
- [ ] ✅ [Feature 3 works]

### Integration Tests

- [ ] ✅ [End-to-end flow 1]
- [ ] ✅ [End-to-end flow 2]

### Code Quality

- [ ] ✅ Test coverage >80%
- [ ] ✅ All linting passes
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 [Specific acceptance statement for this gate]

---

## 🚦 PHASE [NUMBER] COMPLETE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ [Phase-specific security test 1]
- [ ] ✅ [Phase-specific security test 2]
- [ ] ✅ [Phase-specific security test 3]
- [ ] ✅ SQL injection blocked on all endpoints
- [ ] ✅ XSS attempts sanitized
- [ ] ✅ Rate limiting on all mutation endpoints

### Functional Tests

**[Module 1] ([N.1]):**
- [ ] ✅ [Feature 1 works]
- [ ] ✅ [Feature 2 works]
- [ ] ✅ [Feature 3 works]

**[Module 2] ([N.2]):**
- [ ] ✅ [Feature 1 works]
- [ ] ✅ [Feature 2 works]

**[Module 3] ([N.3]):**
- [ ] ✅ [Feature 1 works]
- [ ] ✅ [Feature 2 works]

### Integration Tests

- [ ] ✅ Full user journey: [describe complete flow through phase features]
- [ ] ✅ [Cross-module integration 1]
- [ ] ✅ [Cross-module integration 2]
- [ ] ✅ Load test: [N concurrent users] using all features

### Code Quality

- [ ] ✅ Test coverage >80% for all modules
- [ ] ✅ All linting passes (backend and frontend)
- [ ] ✅ Security audit passes (npm audit / safety check)
- [ ] ✅ API documentation complete for all endpoints
- [ ] ✅ Component documentation complete
- [ ] ✅ No console errors in browser
- [ ] ✅ Mobile responsive on all pages

### Data Quality

- [ ] ✅ [Data integrity check 1]
- [ ] ✅ [Data integrity check 2]
- [ ] ✅ Historical data retained (audit trails)
- [ ] ✅ Currency conversion uses correct rates (if applicable)
- [ ] ✅ Soft deletes work (no hard deletes)

### Performance Tests

- [ ] ✅ [Key screen] loads in <[N] seconds
- [ ] ✅ [Key calculation] completes in <[N]ms
- [ ] ✅ API responses <500ms (95th percentile)
- [ ] ✅ Database queries optimized (no N+1)
- [ ] ✅ Frontend bundle size reasonable (<500KB gzipped)

### User Acceptance

- [ ] ✅ Can [complete user flow 1]
- [ ] ✅ Can [complete user flow 2]
- [ ] ✅ Can [complete user flow 3]
- [ ] ✅ [Key feature] visible and accurate
- [ ] ✅ [Key status indicator] clear
- [ ] ✅ All error messages clear and helpful

**Acceptance Criteria:**
🎯 **Phase [N] Complete**: [Comprehensive statement of what users can now do]

🎯 **[Key Achievement]**: [What's been built and validated]

🎯 **Ready for Phase [N+1]**: Codebase clean, tested, documented, and ready to add [next phase features].

---
