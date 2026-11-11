# Verification, quality and performance

## Quality gates
- Run existing lint, formatter, typecheck, unit and integration tests. Record exact commands and outcomes.
- Run the production build when permitted. Check for deprecations or misconfigured environment variables.
- Maintain a regression test for each fixed bug and a negative test for each corrected authorization defect.
- Validate cross-browser behavior and representative devices for user-facing UI.
- Do not create tests that merely assert hardcoded implementation details without covering behavior.

## Testing pyramid
- Unit: isolated business rules, parsing, formatting and authorization conditions.
- Integration: database persistence, queues, API boundaries and external adapters using approved fakes.
- End-to-end: login, onboarding, payment/order, permissions, errors and recovery.
- Security: unauthorized access, malformed input, malicious uploads, replay/idempotency and cross-tenant scenarios.
- Accessibility: keyboard, focus, semantic labels, screen reader and automated WCAG regression checks.

## Performance review
- Identify hot paths first: browser waterfall, render timing, network transfer, server latency, database query plans.
- Check bundle budgets, image sizing, caching headers, lazy loading, hydration cost, expensive effects and unnecessary re-renders.
- Evaluate index usage, N+1 queries, pagination, connection pools and request/worker concurrency.
- Add observability and safe, production-realistic testing before proposing large optimizations.
- Never fabricate Lighthouse scores, Core Web Vitals, benchmarks or estimated speedups.

## Release criteria
1. Critical/high confirmed vulnerabilities resolved or explicitly risk-accepted by authorized owner.
2. Relevant tests run and pass; new behavior has regression coverage.
3. Accessibility and supported-device checks done or marked not tested.
4. Secrets and configuration reviewed; backup/rollback and monitoring documented.
5. Any remaining high-impact uncertainty listed in a release decision with responsible owner.
