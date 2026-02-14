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
## Approved Special-Purpose Documents

Some documents are allowed for specific investigative or reference purposes (NOT for session tracking):

### **D&D_AUDIT_REPORT.txt** ✅ APPROVED
- **Purpose:** Deep-dive audit of one specific system issue (2024 D&D rules compliance)
- **When to keep:** Document lasts as long as the issue exists (until ability scores implemented)
- **When to remove:** Once the investigation is complete AND findings are integrated into code/architecture

### **SRD 5.2.1 Reference Docs** ✅ APPROVED
- **Purpose:** Reference guide for SRD 5.2.1 rules used in this project
- **When to keep:** Always (authoritative for mechanics and content)
- **Files:**
   - RULES_REFERENCE.md
   - CLASS_REFERENCE.md
   - SPECIES_REFERENCE.md
   - FEATS_REFERENCE.md
   - EQUIPMENT_REFERENCE.md
   - SPELLS_REFERENCE.md
   - MAGIC_ITEMS_REFERENCE.md
   - MONSTERS_REFERENCE.md

### **Other Special Docs** (Examples: API_SPECIFICATION.md, PERFORMANCE_ANALYSIS.md, etc.)
- Only create if: the document serves a purpose beyond session tracking
- Only keep if: it continues to be useful as work progresses
- Otherwise: integrate findings into ARCHITECTURE.md and delete

---

## Rules Reference Policy

- **Use only the SRD 5.2.1 reference docs in this repo** for rules, spells, items, and monsters.
- **Apply rules consistently across all systems** (combat, classes, loot, AI behavior, UI copy).
- **Avoid external sources** (wikis, blogs, non-SRD content) to prevent copyright risk.

---

## ❌ FORBIDDEN - Never Create These

- **SESSION_X_SUMMARY.txt** ← Put session info in CHANGELOG.md instead
- **PROJECT_STATE.md** ← Use CHANGELOG.md for state
- **PROGRESS_TRACKING.txt** ← No separate progress files; update ROADMAP.md
- **NEXT_STEPS.md** ← This is what ROADMAP.md is for
- **IMPROVEMENTS_FOUND.txt** ← Add to CHANGELOG.md as issues, link to ROADMAP.md
- **WEEK_3_NOTES.md** ← Just update CHANGELOG.md
- **TODO_LIST.txt** ← This is what ROADMAP.md is for (prioritized list)

---

## Chat Clearing Procedure

**When user says:** "save everything / i'm going to clear the chat / commit progress"

**AI Should:**

1. **Update CHANGELOG.md:**
   - Add new section for current session at top with: what was built, what tests pass, known issues, how to resume
   - Keep it concise (target: 200-400 words per session)
   - Reference ARCHITECTURE.md for deep dives
   - **TRIM OLD SESSIONS:** Keep last 3 sessions, move older ones to git history comments

2. **Update ROADMAP.md:**
   - Refresh task priorities based on what's now complete
   - Remove completed tasks
   - Add any new blockers or opportunities discovered

3. **Update ARCHITECTURE.md (if needed):**
   - Only if major structural changes, new modules, or design pattern shifts
   - Otherwise, leave it alone

4. **Special Documents:**
   - If you created an audit/investigation document (D&D_AUDIT_REPORT.txt), keep it ONLY if:
     - [ ] The issue still exists
     - [ ] The document will be useful for future work
   - Otherwise DELETE IT after consolidating findings into ARCHITECTURE.md or CHANGELOG.md

5. **Do NOT create new files** unless they serve a permanent reference purpose

6. **Commit files:**
   - Remove any temp/session-specific files first
   - git add .
   - git commit -m "[message about what was built]"

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
5. **When tempted to create a session/progress/tracking file:** DON'T. Use CHANGELOG.md instead.

---

## Examples

**❌ WRONG:**
- Create "SESSION_NOTES.md" to document what was done
- Create "PROJECT_STATUS.txt" to track progress
- Create "NEXT_STEPS.md" (that's what ROADMAP is for)
- Create duplicate "DND_RULES_VERIFICATION.txt" when "D&D_AUDIT_REPORT.txt" already exists

**✅ RIGHT:**
- Update CHANGELOG.md with "Session 3: Added class features (32 across 13 classes), fixed feature bugs, tests passing 15/15"
- Update ROADMAP.md to move completed items to done list and add new blockers
- Update ARCHITECTURE.md only if structure changed
- If creating audit document, make it comprehensive and keep it only while issue exists

---

## Red Flag Questions to Ask Before Creating a New File

1. **"Does a file already exist with a similar purpose?"** → Update that instead
2. **"Is this documenting what was done in a session?"** → Put it in CHANGELOG.md
3. **"Is this a list of next steps?"** → It belongs in ROADMAP.md
4. **"Will this file be useful 6 months from now?"** → Only create if yes
5. **"Is this a reference guide or investigative report?"** → OK to create, but scope it clearly
6. **"Am I creating this because 'documentation is good'?"** → Bloat. Delete it.

If uncertain, ask: "Would a developer 6 months later find this useful, or would they find the same info in CHANGELOG/ARCHITECTURE/ROADMAP?"

---

**Last Updated:** 2026-02-09  
**Enforced By:** AI agents on every context save
