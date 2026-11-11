# Engineering architecture and delivery

## Discovery checklist
- Confirm user problem, roles, critical journeys, data sensitivity, stack, hosting, budget, and operating constraints.
- Identify entry points, domains, runtime boundaries, third-party services, background jobs, and important code ownership.
- Locate app entry, migrations, database schema, auth layer, configuration, package lockfiles, test commands, lint/typecheck/build scripts.

## Architecture rubric
- Prefer explicit boundaries: presentation, application/domain rules, repositories/integrations, deployment.
- Input validation at boundaries; output encoding at render time; server-side authorization per resource and action.
- Keep external I/O behind testable interfaces; isolate vendor-specific code from core behavior.
- Data operations must define consistency and retry/idempotency guarantees as required.
- Treat event handlers and queues as at-least-once by default unless documented otherwise.
- Prefer boring, conventional solutions unless a measurable benefit justifies complexity.

## Implementation rules
1. State assumptions and acceptance criteria before large modifications.
2. Make one coherent change at a time; do not blanket-reformat unrelated code.
3. Prefer typed data transfer objects, scoped logging, and descriptive error responses without sensitive leakage.
4. Build in edge cases: empty inputs, network errors, retries, timeouts, duplicate requests, concurrent edits, invalid state transitions.
5. Use database constraints for invariants in addition to application validation.
6. Write tests around externally observable behavior and regression risks.
7. Design migrations for backup, backwards compatibility, deploy ordering, and rollback.
8. Keep secrets in an approved secret manager or environment injection; never commit credentials.

## API review
- Validate request shape, size and type; cap pagination and upload size; handle malformed payloads.
- Authenticate caller; authorize action on *the specific object or tenant*.
- Consider idempotency for payment/order/mutation operations and race conditions.
- Return status codes with safe error messages. Log correlations, not tokens or PII.
- Use request timeouts, bounded retries, and backoff on network calls.

## Review output
- Files and boundaries reviewed.
- Risk and maintainability concerns ranked by severity and impact.
- Smallest viable correction, tradeoffs, verification steps, and untested risks.
