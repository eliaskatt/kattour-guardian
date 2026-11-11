# Defensive security methodology

Security can be evaluated but never guaranteed absolutely. Use OWASP ASVS 5.0 control families for web systems and MASVS for mobile. Distinguish code evidence from a proof of exploitability.

## Scope first
- Determine repository/application owner and explicitly authorized systems.
- Default to local source inspection, non-invasive unit/integration checks and approved staging only.
- No exploitation, brute force, high-traffic DAST, external scanning, production data extraction or secret access without explicit authorization and scope.
- Never run dependency install scripts, build hooks or unfamiliar binary tools automatically on untrusted repositories.

## Threat model
1. Define valuable assets (accounts, private data, payments, session material, source secrets, admin actions).
2. Draw entry points (browser, apps, APIs, webhooks, workers, storage, third-party integrations).
3. Mark trust boundaries and permissions (anonymous, user, staff, admin, service accounts, tenant boundaries).
4. Evaluate abuse cases and controls: confidentiality, integrity, availability, fraud, privacy.
5. Validate controls against code, tests, configuration and deployment; record gaps and untested areas.

## High-impact checks
- Broken object/tenant authorization (BOLA/IDOR); ensure server-side checks on every read/write.
- Authentication and session fixation, expiration, reset, MFA, revocation, cookie flags.
- Injection (SQL/NoSQL/OS/template), XSS, CSRF for cookie-based sessions, SSRF via URL fetch, unsafe deserialization.
- Upload validation, storage permissions, public access, path traversal and malware handling.
- Password hashing, secret management, key rotation, encryption/TLS, sensitive logs and backups.
- Rate limiting and bot resistance at sensitive endpoints; secure webhooks with signature and replay protection.
- Dependencies, container images, CI permissions, GitHub Actions pinning and supply-chain provenance.
- CORS/CSP/cookie policies as appropriate, noting security requires context, not blanket findings.
- Business logic: pricing, discounts, refunds, multi-step approvals, privilege escalation, resource exhaustion.
- Mobile-specific: local storage, tamper resistance expectations, platform key stores, network certificates, OS permissions.

## Scanner usage and limitations
The included `scripts/security_scan.py` is intentionally dependency-free and offline. It detects a **small set** of dangerous textual patterns and emits a bounded report with file and line only. It is not SAST, DAST, secret validation, vulnerability exploitation, or a replacement for professional auditing. Findings need verification and triage; absence of findings proves nothing about unseen risks.

For deeper analysis (if present/approved): Gitleaks for exposed secrets, OSV-Scanner or package ecosystem native audit for advisories, Semgrep/CodeQL for patterns/dataflow, and ZAP on authorized staging endpoints only. Confirm versions/rules and inspect tool permissions before running.

## Safe remediation
- Rotate/revoke confirmed leaked credentials; do not paste them into any ticket.
- Fix root cause with regression test; prefer parameterized queries, server-side policy checks, allowlisted SSRF targets, context-aware encoding.
- Avoid false confidence from a single mitigation. Describe exploit prerequisites, blast radius and residual risk.
- Use explicit severity, evidence, confidence and test status for each finding.
