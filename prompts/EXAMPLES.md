# Example prompts

## Full product review
Use kattour-guardian to review this application end to end. First understand the stack and user journeys. Then evaluate UX, accessibility, architecture, privacy, performance, and defensive security. Run only permitted local checks. Distinguish confirmed findings from unverified risks. Produce prioritized fixes, a verification log and a release decision.

## New feature
Use kattour-guardian to implement [feature]. Preserve the existing stack. Define acceptance criteria, design responsive and accessible user states, add server-side authorization and tests, then validate the changed behavior before presenting the result.

## Strict security review
Use kattour-guardian in AUDIT mode, read-only. Do not deploy or scan public/production endpoints. Review OWASP ASVS/MASVS controls relevant to the stack. Report evidence, confidence, prerequisites, actionable remediations and untested areas; do not claim complete security.

## Visual and experience redesign
Use kattour-guardian in DESIGN mode. Audit the main user journey, navigation, mobile layouts, keyboard flow, focus, errors, labels, loading and empty states, contrast and RTL. Implement only agreed high-priority changes; specify browser and screen-reader checks still required.

## Token-aware agent mode (v0.2)

> Use kattour-guardian in low-token mode. First build a compact project map using
> context_pack.py for this exact task. Read code snippets selectively; never dump
> entire files, repository contents, or unfiltered logs. Use log_compact.py for
> noisy test output and a same-conversation delta snapshot to avoid resending
> unchanged files. Keep final feedback concise, but do not skip necessary tests,
> architecture reasoning, authorization review or security checks. Report actual
> tests and limitations; do not invent a token-saving percentage.
