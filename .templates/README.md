# Phase Task Templates

**Purpose:** Templates and guides for creating new phase task files

---

## 📁 Files in This Directory

### 1. `phase_template.md`
**Complete template for creating new phase task files**

- Full phase structure with placeholders
- Backend and frontend task examples
- Testing gate templates
- Copy and customize for each new phase

### 2. `HOW_TO_USE_TEMPLATE.md`
**Comprehensive guide on using the template**

- Step-by-step instructions
- Placeholder reference table
- Task writing patterns
- Context file usage
- Testing gate creation
- Example Phase 2 creation

### 3. `CHECKBOX_TRACKING.md`
**Guide to tracking progress with checkboxes**

- How markdown checkboxes work
- Tracking individual tasks
- Tracking testing gates
- Best practices
- Example workflows
- Git integration tips

---

## 🚀 Quick Start

### To Create a New Phase File:

**1. Copy the template:**
```bash
cd /Users/CSJ/Desktop/goalplan
cp .templates/phase_template.md phase2_tasks.md
```

**2. Open `HOW_TO_USE_TEMPLATE.md`:**
```bash
# Read the guide first
cat .templates/HOW_TO_USE_TEMPLATE.md
```

**3. Replace placeholders:**
- Phase number: `[NUMBER]` → `2`
- Phase name: `[PHASE NAME]` → `Core Modules`
- Timeline: `[X-Y months]` → `4-5 months`
- And so on...

**4. Write your tasks:**
- Follow the task patterns in the template
- Reference appropriate context files (shard documents)
- Include comprehensive tests
- Add clear acceptance criteria

**5. Track progress:**
- Check off tasks as you complete them: `[ ]` → `[x]`
- See `CHECKBOX_TRACKING.md` for details

---

## 📋 Template Structure

```markdown
phase_template.md
├── Header (phase info, timeline, prerequisites)
├── Overview (goals, modules, outputs)
├── Instructions (reference to .claude/instructions.md)
├── Task Sections
│   ├── Backend tasks (🐍 delegation)
│   ├── Frontend tasks (⚛️ delegation)
│   └── Each with context files, tests, acceptance
└── Testing Gates
    ├── Intermediate gates (per major section)
    └── Final phase gate (comprehensive)
```

---

## 🎯 Task Structure Pattern

Every task follows this pattern:

```markdown
### Task X.Y.Z: [Task Name]

**[🐍 or ⚛️] DELEGATE TO: `[agent-name]`**
**Context Files:** `file1.md`, `file2.md`

**Agent Instructions:**
1. Read file1.md - [what to read]
2. Read file2.md for [context]
3. [Specific implementation instruction]

**Tasks:**
- [ ] [Subtask 1]
- [ ] [Subtask 2]
- [ ] **Test Suite:**
  - Test [scenario]
  - Test [scenario]
- [ ] **Run:** `[test command]`
- [ ] **Acceptance:** [Clear criteria]
```

---

## 📚 Context Files Reference

When writing tasks, reference these shard files:

**Core Modules:**
- `Protection.md`, `Savings.md`, `Investment.md`, `Retirement.md`, `IHT.md`

**Tax & Intelligence:**
- `CoreTaxCalcs.md`, `DTA.md`, `TaxResidency.md`
- `AIAdvisoryRecommendation.md`, `GoalPlanning.md`, `ScenarioWhatif.md`

**Cross-Cutting:**
- `Architecture.md`, `DataManagement.md`, `securityCompliance.md`
- `performance.md`, `UserFlows.md`, `Notifications.md`

**Full list:** See `SHARDS_README.md` in project root

---

## ✅ Testing Gate Structure

### Intermediate Gate (After Major Section)
```markdown
## 🚦 PHASE X [MODULE] TESTING GATE

### Security Tests (CRITICAL)
- [ ] ✅ [Specific security test]

### Functional Tests
- [ ] ✅ [Feature works]

### Code Quality
- [ ] ✅ Test coverage >80%
- [ ] ✅ Linting passes

**Acceptance Criteria:**
🎯 [Module complete statement]
```

### Final Phase Gate
```markdown
## 🚦 PHASE X COMPLETE TESTING GATE

### Security Tests (CRITICAL)
- [ ] ✅ [Phase security tests]

### Functional Tests
**Module 1:**
- [ ] ✅ [All features work]

### Integration Tests
- [ ] ✅ Full user journey
- [ ] ✅ Load test passes

### Code Quality
- [ ] ✅ All quality metrics met

### Performance Tests
- [ ] ✅ Performance targets met

### User Acceptance
- [ ] ✅ All user flows work

**Acceptance Criteria:**
🎯 Phase X Complete
🎯 Ready for Phase [X+1]
```

---

## 🔄 Development Workflow

### 1. Phase Planning
- Identify modules to build
- Determine task breakdown
- Estimate timeline

### 2. File Creation
- Copy `phase_template.md`
- Rename to `phaseN_tasks.md`
- Fill in all placeholders

### 3. Task Writing
- Write specific, actionable tasks
- Reference context files
- Include comprehensive tests
- Define clear acceptance

### 4. Development
- Work through tasks sequentially
- Check off as you complete: `[ ]` → `[x]`
- Run tests continuously
- Verify at testing gates

### 5. Phase Completion
- All task checkboxes checked
- All testing gate checkboxes checked
- Review acceptance criteria
- Ready for next phase!

---

## 📖 Additional Resources

**In Project Root:**
- `.claude/instructions.md` - All development rules and workflows
- `TASKS_README.md` - Overview of all phase files
- `SHARDS_README.md` - Feature specification documents
- `roadmapConsideration.md` - Overall development roadmap

**Agent Configurations:**
- `.claude/agents/python-backend-engineer.md`
- `.claude/agents/react-coder.md`

---

## 💡 Tips for Success

### Writing Tasks
✅ Be specific (not "implement feature", but "create X endpoint with Y validation")
✅ Reference exact sections in context files
✅ Include comprehensive test requirements
✅ Define clear acceptance criteria
✅ Keep one task = one deliverable

### Using Templates
✅ Replace ALL placeholders before starting development
✅ Customize testing gates to phase requirements
✅ Add intermediate gates for large phases
✅ Keep consistent formatting

### Tracking Progress
✅ Check boxes as you complete each subtask
✅ Don't check "Test Suite" until ALL tests pass
✅ Verify testing gates before proceeding
✅ Use checkboxes as your progress dashboard

---

## 🎯 Remember

**Critical Rules:**
- ⛔ DO NOT PROCEED until all tests pass
- 🎯 App functionality must be maintained at all times
- ✅ Testing gates are mandatory, not optional
- 📋 All tasks must reference context files
- 🤖 Always delegate to appropriate agents (🐍 or ⚛️)

**Testing Strategy:**
- Backend: `pytest` for all Python code
- Frontend: `Jest` for components, `Playwright` for E2E only
- See `.claude/instructions.md` for complete strategy

---

## 🚀 Ready to Create Phase 2?

1. Read `HOW_TO_USE_TEMPLATE.md` completely
2. Copy `phase_template.md` to `phase2_tasks.md`
3. Follow the step-by-step guide
4. Start building! 🎉

---

**Questions?** Refer to:
- `HOW_TO_USE_TEMPLATE.md` - Template usage
- `CHECKBOX_TRACKING.md` - Progress tracking
- `.claude/instructions.md` - Development rules
- `TASKS_README.md` - Phase file overview
