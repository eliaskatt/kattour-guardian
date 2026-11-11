# Platform-specific review hints

These are targeted starting points. Discover the actual stack first.

## React / Next.js / Vue / Svelte
- Test hydration, keyboard interaction, state transitions and client/server trust boundaries.
- Verify cookie/session configuration, server actions and API authorization server-side.
- Guard XSS when rendering trusted HTML and sanitize only where HTML rendering is genuinely needed.
- Use real browser tests for accessibility rather than static scans of JSX/Vue templates.

## Node.js / Express / NestJS
- Centralized request validation and scoped authorization; safe error handling.
- Dependency audits, production environment flags, request body limits, CORS/cookie/CSRF design.
- Parameterized queries; SSRF controls for server-side fetch; webhook signature/replay validation.

## Python / Django / FastAPI
- Check server-side permissions, trusted hosts, CSRF/cookies for session apps, debug configuration.
- Use ORM parameterization, validation, secret management and authentication tests.
- Type checks and dependency advisories are useful but not security certification.

## PHP / Laravel / Yii
- Query binding and output escaping; route policy middleware; CSRF and session handling.
- Avoid unsafe file includes and permissive upload paths; check job/cron authorization boundaries.

## Shopify and commerce apps
- Check tenant/shop isolation, OAuth scopes and callback validation, signed webhooks, uninstallation data lifecycle.
- Validate prices and discounts on server; protect billing, order and fulfillment state machines.
- Review API rate limits and app permissions against least privilege.

## Mobile (iOS/Android/React Native/Flutter)
- Use OWASP MASVS/MASTG for platform threats, not only web scanners.
- Check secure storage, API authorization, deep links, certificate handling and logs containing sensitive data.
- Respect platform permission prompts and minimize data collection.
