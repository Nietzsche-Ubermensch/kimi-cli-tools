# Repository Self-Sufficiency & Surgical Cleanup

## Goals
- Enable seamless, independent operation without constant supervision.
- Maintain meticulous standards: no complacency in reviews or code.
- Surgical approach: targeted fixes, thorough auditing, organized components.

## Key Practices

### Linear-Driven Workflow
- Every task starts with a Linear item (KIM-xxx).
- Assign to self, set In Progress, add start comment.
- Create branch: `feat/KIM-xxx-short-slug`.
- Commit with `[KIM-xxx]` prefix.
- Open PR that closes the Linear item.
- Link PR back to Linear.
- Merge after CI, update Linear to Done.

### Code & Review Hygiene
- Push code frequently.
- Debug issues promptly with minimal, focused changes.
- Organize files and remove redundancy.
- Audit everything under review rigorously.
- Document decisions for transparency.

### Transport & Architecture
- Continue evolving MCP transport support (stdio, HTTP, SSE).
- Keep BaseMCPServer and client modular.

## Current Cleanup Actions (KIM-10)
- Added this guide for self-sufficiency.
- Ensured recent PRs (KIM-3, KIM-8, KIM-9) are properly linked and documented.
- Improved architecture docs with transport details.

This setup allows the workflow to run autonomously while maintaining high quality.

## Automated Commit Message Generation (Implemented)
- We use Conventional Commits with Linear IDs.
- Interactive commits: `npm run commit` (Commitizen).
- Commits are validated via commitlint + husky `commit-msg` hook.
- Required format: `[KIM-xxx] <type>: <description>`.
