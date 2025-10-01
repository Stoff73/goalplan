# Task Checkbox Tracking Guide

**Purpose:** Track progress as you complete tasks in phase files

---

## How Checkboxes Work

Markdown checkboxes use this syntax:
- `- [ ]` = Unchecked (not done)
- `- [x]` = Checked (done)

**In your phase files, simply change the space to an 'x' to mark complete.**

---

## Tracking Individual Tasks

### Initial State (Nothing Complete)

```markdown
### Task 1.1.1: User Registration - Data Models

**Tasks:**
- [ ] Create `users` table with all fields from specification
- [ ] Create `email_verification_tokens` table
- [ ] Add appropriate indexes (email, token, expires_at)
- [ ] Create database migration using Alembic
- [ ] Create User model/entity with Pydantic/SQLAlchemy
- [ ] **Test Suite:**
  - Test user model creation
  - Test unique email constraint
  - Test default status is PENDING_VERIFICATION
- [ ] **Run:** `pytest tests/models/test_user_model.py -v`
- [ ] **Acceptance:** All model tests pass
```

### In Progress (Some Items Complete)

```markdown
### Task 1.1.1: User Registration - Data Models

**Tasks:**
- [x] Create `users` table with all fields from specification
- [x] Create `email_verification_tokens` table
- [x] Add appropriate indexes (email, token, expires_at)
- [x] Create database migration using Alembic
- [ ] Create User model/entity with Pydantic/SQLAlchemy  ← Currently working on
- [ ] **Test Suite:**
  - Test user model creation
  - Test unique email constraint
  - Test default status is PENDING_VERIFICATION
- [ ] **Run:** `pytest tests/models/test_user_model.py -v`
- [ ] **Acceptance:** All model tests pass
```

### Complete (All Items Done)

```markdown
### Task 1.1.1: User Registration - Data Models

**Tasks:**
- [x] Create `users` table with all fields from specification
- [x] Create `email_verification_tokens` table
- [x] Add appropriate indexes (email, token, expires_at)
- [x] Create database migration using Alembic
- [x] Create User model/entity with Pydantic/SQLAlchemy
- [x] **Test Suite:**
  - Test user model creation
  - Test unique email constraint
  - Test default status is PENDING_VERIFICATION
- [x] **Run:** `pytest tests/models/test_user_model.py -v`
- [x] **Acceptance:** All model tests pass
```

---

## Tracking Test Suites

### Within a Task

Tests are part of the task checklist:

```markdown
- [ ] **Test Suite:**
  - Test user model creation          ← Individual test scenarios
  - Test unique email constraint       ← are documented here
  - Test default status                ← for reference
- [ ] **Run:** `pytest tests/models/test_user_model.py -v`
```

**Don't check off the Test Suite item until ALL tests pass:**

```markdown
- [x] **Test Suite:**  ← Only check when 100% of tests pass
  - Test user model creation
  - Test unique email constraint
  - Test default status
- [x] **Run:** `pytest tests/models/test_user_model.py -v`
```

---

## Tracking Testing Gates

Testing gates have many items to verify:

### Before Testing

```markdown
## 🚦 PHASE 1 AUTH TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ Password hashing uses Argon2 correctly
- [ ] ✅ JWT tokens signed with RS256
- [ ] ✅ Sessions expire correctly (15 min access, 7 days refresh)
- [ ] ✅ Rate limiting prevents brute force (tested)
- [ ] ✅ Account lockout works after 5 failed attempts
```

### During Testing (Incremental Progress)

```markdown
## 🚦 PHASE 1 AUTH TESTING GATE

### Security Tests (CRITICAL)

- [x] ✅ Password hashing uses Argon2 correctly          ← Verified
- [x] ✅ JWT tokens signed with RS256                    ← Verified
- [x] ✅ Sessions expire correctly (15 min access, 7 days refresh)  ← Verified
- [ ] ✅ Rate limiting prevents brute force (tested)     ← Testing now
- [ ] ✅ Account lockout works after 5 failed attempts   ← Not tested yet
```

### After Complete Testing

```markdown
## 🚦 PHASE 1 AUTH TESTING GATE

### Security Tests (CRITICAL)

- [x] ✅ Password hashing uses Argon2 correctly
- [x] ✅ JWT tokens signed with RS256
- [x] ✅ Sessions expire correctly (15 min access, 7 days refresh)
- [x] ✅ Rate limiting prevents brute force (tested)
- [x] ✅ Account lockout works after 5 failed attempts
```

**⛔ DO NOT PROCEED TO NEXT PHASE until ALL checkboxes in the gate are checked!**

---

## Visual Progress Tracking

### At a Glance

You can quickly see progress by scanning checkboxes:

```markdown
## 1.1 User Authentication System

### Task 1.1.1: User Registration - Data Models
- [x] Complete

### Task 1.1.2: Password Hashing Service
- [x] Complete

### Task 1.1.3: Email Service Integration
- [ ] In progress (50% done based on checkboxes inside)

### Task 1.1.4: Registration Endpoint Implementation
- [ ] Not started

### Task 1.1.5: Email Verification Endpoint
- [ ] Not started
```

---

## Editor Support

### VS Code

VS Code supports markdown checkboxes natively:
- Click checkbox in preview to toggle
- Or edit the markdown directly: `[ ]` → `[x]`

### GitHub

If you push to GitHub, checkboxes render as interactive:
- ☐ Unchecked appears as empty box
- ☑ Checked appears as checked box

---

## Best Practices

### ✅ Do:

1. **Check off immediately** when complete
   - Mark subtask done → Check box
   - All tests pass → Check test suite box
   - Task fully complete → Check acceptance box

2. **Be honest** about completion
   - Only check if truly done and tested
   - Partial completion = still unchecked

3. **Use as your progress tracker**
   - Check daily to see what's left
   - Verify testing gates before proceeding

### ❌ Don't:

1. **Don't check prematurely**
   - "Almost done" = still `[ ]` not `[x]`
   - Tests failing = still `[ ]` not `[x]`

2. **Don't skip test checkboxes**
   - Tests are mandatory
   - Can't mark task complete without tests passing

3. **Don't ignore testing gates**
   - They're blocking by design
   - All must be checked before next phase

---

## Example: Complete Task Flow

### Day 1: Start task
```markdown
### Task 1.1.1: User Registration - Data Models
- [ ] Create `users` table
- [ ] Create `email_verification_tokens` table
- [ ] Add indexes
- [ ] Create migration
- [ ] Create models
- [ ] **Test Suite:**
- [ ] **Run:** `pytest`
- [ ] **Acceptance:** All tests pass
```

### Day 2: Made progress
```markdown
### Task 1.1.1: User Registration - Data Models
- [x] Create `users` table                    ← Done yesterday
- [x] Create `email_verification_tokens` table ← Done yesterday
- [x] Add indexes                             ← Done today
- [ ] Create migration                        ← Working on now
- [ ] Create models
- [ ] **Test Suite:**
- [ ] **Run:** `pytest`
- [ ] **Acceptance:** All tests pass
```

### Day 3: Code complete, testing
```markdown
### Task 1.1.1: User Registration - Data Models
- [x] Create `users` table
- [x] Create `email_verification_tokens` table
- [x] Add indexes
- [x] Create migration
- [x] Create models
- [ ] **Test Suite:**                         ← Writing tests now
  - Test user model creation
  - Test unique email constraint
- [ ] **Run:** `pytest`
- [ ] **Acceptance:** All tests pass
```

### Day 4: Tests written and passing
```markdown
### Task 1.1.1: User Registration - Data Models
- [x] Create `users` table
- [x] Create `email_verification_tokens` table
- [x] Add indexes
- [x] Create migration
- [x] Create models
- [x] **Test Suite:**
  - Test user model creation
  - Test unique email constraint
- [x] **Run:** `pytest tests/models/test_user_model.py -v`  ← All pass!
- [x] **Acceptance:** All model tests pass                  ← Task complete!
```

**✅ Task is now 100% complete. Move to next task.**

---

## Git Integration (Optional)

You can commit checkbox updates as you go:

```bash
# After completing subtasks
git add phase1_tasks.md
git commit -m "Complete user table creation and migration"

# After task fully complete
git add phase1_tasks.md
git commit -m "Complete Task 1.1.1: User Registration Data Models - all tests passing"
```

This gives you a commit history of progress! 📊

---

## Summary

**Simple formula:**
1. Work on task
2. Complete subtask → Change `[ ]` to `[x]`
3. All subtasks done + tests pass → Check acceptance box
4. Move to next task
5. At end of section → Verify testing gate
6. All gate boxes checked → Proceed to next phase

**The checkboxes are your development tracker - use them!** ✅
