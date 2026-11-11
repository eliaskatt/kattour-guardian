# Reporting and severity contract

## Severity
- **CRITICAL:** Evidence of immediate, broad-impact exploitability or credential compromise under the stated threat model.
- **HIGH:** Credible serious exposure of sensitive data, privilege, integrity or availability with reasonable conditions.
- **MEDIUM:** Material weakness with narrower prerequisites, or concerning patterns requiring further verification.
- **LOW:** Defense-in-depth, maintainability or usability issue with limited security impact.
- **INFO:** Observation, best practice or untested hypothesis; do not present as a confirmed defect.

Never assign severity solely because a regex matched a string. Report **confidence** (high/medium/low), **evidence**, and **verification status** (confirmed/likely/unverified) separately.

## Required report

### Summary
- Objective, scope and environment.
- Decision: ready / conditional / not ready / undetermined, with rationale.
- Work completed vs recommended, and important untested areas.

### Findings (ordered by severity)
For each finding:
- ID, title, category, severity, confidence, status.
- Affected file:line, endpoint or screen, omitting secret values.
- Evidence and prerequisites, avoiding unsupported exploit claims.
- User/business impact and minimal safe remediation.
- How to retest, and whether correction was applied.

### Design assessment
- Primary task flow, visual hierarchy, navigation, responsive states and accessibility observations.
- Prioritized changes (P0/P1/P2), with measurable acceptance criteria.

### Engineering quality
- Architecture concerns, test coverage, performance data where actually measured.

### Verification log
- Command/tool, environment, result, evidence summary.
- Items skipped and why.

### Residual risks and handoff
- Dependencies, permissions, potential production effects, rollback and next owner actions.

## Safe output conventions
- No raw tokens, private keys, passwords, session cookies or personal data in the report.
- Label heuristic scanner findings as *potential* until validated.
- Do not imply a security scan was performed when it was not.
