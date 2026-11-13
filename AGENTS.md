# AGENTS.md — AITeamWorkingModel Agent / Contributor Rules

## Mission
Build an **AI-Driven R&D Operating Model** where AI agents advance permitted research and engineering tasks, while **humans jointly review evidence, challenge conclusions, and retain final authority**. Maintain low-overhead but empirically verified backup readiness.

Read \`README.md\`, \`docs/01-operating-model.md\`, \`docs/02-workflow-and-takeover.md\`, \`docs/05-security-and-governance.md\` before writing code. For Operating Kit work, also read \`docs/09\`–\`docs/13\`; \`docs/13-opus-handoff.md\` lists the work orders and the invariants (I1–I10) that must never be weakened.

## Repository status
- This repository currently contains architecture documents and a mock offline UI; do not assume production services, real research data or integrations exist.
- It is a **public** repository. Never add secrets, personal data, customer data, real lab measurements, internal names, unreleased IP, machine credentials or confidential prompts.
- Use clearly fictional test cases. Do not mislabel examples as actual experiment outcomes.

## Mandatory engineering behavior
1. Make small scoped changes; explain the affected documents, interfaces, risk and rollback.
2. For code changes: add meaningful automated tests and provide exact commands + results. Never claim tests passed unless actually run.
3. Preserve canonical evidence. AI summaries, chat messages and vector search results are not authoritative sources.
4. Every research finding must be labeled VERIFIED / OBSERVED / HYPOTHESIS / RECOMMENDATION / UNKNOWN / REJECTED as appropriate.
5. Design API authorization at the backend for every project, source and action. Do not trust frontend-only permission controls.
6. No agent may approve its own high-risk actions, give itself permissions, run commands on real hardware, expose confidential data, or deploy to real systems without explicit authenticated authorization.
7. Agent scripts must have timeouts, resource budgets, idempotency for events, audit logs and clear blocked states.
8. PRs must document tests, remaining unknowns, security scope, source/evidence and acceptance criteria.
9. Do not introduce a dependency or service just because it is fashionable; prefer small, replaceable adapters.
10. English is fine for code/schema; document end-user workflows in Traditional Chinese.
11. Follow the execution playbook (\`docs/09\`) for this repository's own development: one work package per PR, branch \`wp/WP-NNN-<slug>\`, PR body per \`.github/pull_request_template.md\` with claims, must-read list, executed commands and unverified scope.
12. Agent-produced evidence is at most OBSERVED. Never label your own result VERIFIED, approve or merge your own PR, relax acceptance criteria, or change files outside the work package scope without a recorded human decision.
13. Never emit flashing, debugger, instrument or equipment-control commands. Physical actions are human tasks: prepare the procedure and analyse the records.

## Working directory contract
- \`docs/\`: operating model, workflows, architecture, API, governance, rollout and backlog.
- \`prompts/\`: approved agent contracts and output schemas.
- \`demo/\`: **offline / fictitious** interface demonstrations.
- \`kit/\`: Operating Kit sources — templates, checklists, and (future) domain packs, agent and forge integrations.
- \`work/\`: this repository's own missions and work packages (the kit is developed with its own process).
- \`packages/aitw/\`, \`examples/\`: (future) the CLI and fictional example projects, per \`docs/13-opus-handoff.md\`.
- Future code lives in \`apps/\`, \`services/\`, \`packages/\`, \`infra/\`, \`tests/\` as specified in \`docs/07-engineering-backlog.md\`.

## Completion checklist
- [ ] No confidential or real research data accidentally included.
- [ ] Tests/evidence truly executed or clearly marked NOT RUN.
- [ ] Risks and unverified assumptions listed.
- [ ] New results trace to immutable revisions or source URIs.
- [ ] Approval gates enforced server-side where applicable.
- [ ] Backup takeover remains safe and testable without Primary.
- [ ] README and relevant docs updated.
