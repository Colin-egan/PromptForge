# Bob Standing Orders — PromptForge Project

This document defines the automated workflow Bob follows throughout the PromptForge project to maintain an audit trail for the IBM AI Builders Challenge submission.

---

## Session Start Protocol

At the **start of every session**, Bob will:

1. **Ask**: "What's the goal for this session?"
2. **Create a new entry** in [`BOB_LOG.md`](../BOB_LOG.md) using this template:

```markdown
## YYYY-MM-DD — <short title>
**Goal:** <one sentence>
**What Bob did:** 
- <bullet added as work progresses>

**Outcome:** <files touched, % Bob-authored estimate>
**Artifacts:** <screenshot filenames, commit hashes>
**Tags:** [category], [category]
```

---

## During Session — Real-Time Updates

As work progresses, Bob will **update the current session entry** in real time by adding bullets to "What Bob did:" whenever Bob:
- Drafts or modifies code
- Proposes architecture or design decisions
- Debugs errors or resolves issues
- Writes documentation
- Performs any other significant contribution

---

## Session End Protocol

At the **end of every session**, Bob will prompt:

> "Session wrap-up — should I (a) finalize the BOB_LOG entry, (b) suggest a commit message with the [bob] tag, and (c) note any screenshots I should take?"

Then Bob will:

1. **Finalize the BOB_LOG entry** with:
   - Complete "Outcome" section (files modified, estimated % Bob-authored)
   - Complete "Artifacts" section (commit hashes, screenshot filenames)
   - Add appropriate tags from the category list

2. **Suggest a commit message** in this format:
```
<type>(<scope>): <summary>

<body describing what changed>

Bob-session: <BOB_LOG.md anchor or screenshot filename>
[bob] or [bob+manual] or [manual]
```

3. **Recommend screenshots** to capture for the submission (UI states, architecture diagrams, terminal output, etc.)

---

## Weekly Review Protocol

On the **first session of each week**, Bob will:

1. Remind you to review [`BOB_LOG.md`](../BOB_LOG.md)
2. Suggest 2-3 entries as highlight-reel candidates for [`BOB_HIGHLIGHTS.md`](./BOB_HIGHLIGHTS.md)

---

## Highlight Creation

When you say **"highlight this"**, Bob will:

1. Copy the current session entry from BOB_LOG.md
2. Transform it into polished prose format in [`BOB_HIGHLIGHTS.md`](./BOB_HIGHLIGHTS.md):
   - **What I asked**: The problem or task presented
   - **What Bob delivered**: The solution, code, or architecture Bob provided
   - **What it unlocked**: The downstream impact on the project
3. Include appropriate category tags

---

## Category Tags

Every session entry must include one or more tags from:
- `[architecture]` — System design, component structure, technical decisions
- `[feature]` — New functionality implementation
- `[ibm-integration]` — watsonx.ai, Granite, or IBM-specific integrations
- `[debugging]` — Error resolution, troubleshooting
- `[refactor]` — Code cleanup, optimization, restructuring
- `[docs]` — Documentation, README updates, inline comments
- `[testing]` — Unit tests, integration tests, test infrastructure
- `[devops]` — CI/CD, Docker, deployment configuration

**Goal**: Demonstrate breadth across categories for the IBM AI Builders Challenge submission.

---

## Commit Message Attribution Tags

- `[bob]` — 100% Bob-authored (generated code, no manual edits)
- `[bob+manual]` — Bob-generated with manual refinements
- `[manual]` — Human-authored, Bob provided guidance only

---

## File Locations

- **Session log**: [`BOB_LOG.md`](../BOB_LOG.md) (root directory)
- **Highlights**: [`docs/BOB_HIGHLIGHTS.md`](./BOB_HIGHLIGHTS.md)
- **Session artifacts**: `docs/bob-sessions/` (screenshots, diagrams, etc.)
- **This workflow doc**: [`docs/BOB_WORKFLOW.md`](./BOB_WORKFLOW.md)
