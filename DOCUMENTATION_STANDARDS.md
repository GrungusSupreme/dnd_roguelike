# Documentation Standards

**Purpose:** Prevent redundant documentation and ensure AI agents efficiently update existing context files instead of creating new ones.

---

## The 4 Core Documentation Files

### 1. **README.md**
- **Role:** User guide (how to play, install, use commands)
- **Audience:** Players, developers starting fresh
- **Update When:** CLI changes, new game modes, installation steps change
- **Do NOT:** Document internal architecture, design decisions, or development plans here

### 2. **ARCHITECTURE.md**
- **Role:** Technical reference (how the system works, module breakdown, design patterns)
- **Audience:** Developers understanding the codebase, AI agents implementing features
- **Update When:** Major refactors, new module structure, design pattern changes, significant class changes
- **Do NOT:** List what to build next (use ROADMAP), list what changed this session (use CHANGELOG)

### 3. **ROADMAP.md**
- **Role:** Development planning (what to build next, priorities, decision tree)
- **Audience:** Project manager, next developer, this developer deciding what to do next
- **Update When:** Features complete, new priorities emerge, blockers resolved
- **Do NOT:** Explain how the current code works (use ARCHITECTURE), celebrate what was done (keep brief)

### 4. **CHANGELOG.md**
- **Role:** Project state snapshot (what's working, what's broken, what's new this session)
- **Audience:** AI agents resuming work, developers checking current status
- **Update When:** Completing this session, especially before clearing chat
- **Do NOT:** Repeat architecture details (use ARCHITECTURE), plan next work (use ROADMAP)

---

## Chat Clearing Procedure

**When user says:** "save everything / i'm going to clear the chat / commit progress"

**AI Should:**

1. **Update CHANGELOG.md:**
   - Add new section for current session at top with: what was built, what tests pass, known issues, how to resume
   - Keep it concise (target: 200-400 words per session)
   - Reference ARCHITECTURE.md for deep dives

2. **Update ROADMAP.md:**
   - Refresh task priorities based on what's now complete
   - Remove completed tasks
   - Add any new blockers or opportunities discovered

3. **Update ARCHITECTURE.md (if needed):**
   - Only if major structural changes, new modules, or design pattern shifts
   - Otherwise, leave it alone

4. **Do NOT:**
   - Create SESSION_SUMMARY.md or similar
   - Create PROJECT_STATE.md or PROGRESS.md
   - Create any new context files

5. **Commit files:**
   - git add .
   - git commit -m "[message about what was built]"
   - Leave branch/push instructions in GIT_COMMIT_GUIDE.txt if git environment unclear

---

## File Size Targets

- **README.md:** <200 lines (quick start guide)
- **CHANGELOG.md:** <400 lines (current state only, old sessions trimmed)
- **ROADMAP.md:** <300 lines (prioritized, actionable next steps)
- **ARCHITECTURE.md:** <500 lines (could be longer if system is complex, but should be well-organized)

If docs exceed these, they're getting bloated → consolidate or move details to code comments.

---

## How AI Agents Should Use This

1. **When resuming work:** Read CHANGELOG.md (2 min) → ARCHITECTURE.md (5 min) → pick task from ROADMAP.md
2. **When adding features:** Update ARCHITECTURE.md if they change module structure, otherwise just code
3. **When done with session and clearing chat:** Update CHANGELOG.md + ROADMAP.md only, then commit
4. **When creating new docs:** Check this file first. If similar purpose exists, update it instead.

---

## Examples

**❌ WRONG:**
- Create "SESSION_NOTES.md" to document what was done
- Create "PROJECT_STATUS.txt" to track progress
- Create "NEXT_STEPS.md" (that's what ROADMAP is for)

**✅ RIGHT:**
- Update CHANGELOG.md with "Session 2: Added feature X, tests passing: 15/15, next: feature Y"
- Update ROADMAP.md to move completed items to done list
- Update ARCHITECTURE.md only if structure changed

---

**Last Updated:** 2026-02-08  
**Enforced By:** AI agents on every context save
