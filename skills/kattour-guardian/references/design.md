# UI/UX and accessible product design

## Diagnose before redesigning
- Identify the main job-to-be-done and high-frequency paths. Draw task flow from entry to completion.
- Check information architecture: navigation clarity, meaningful labels, task-first grouping, visible hierarchy.
- Inspect current UI and real device sizes when tools and a runnable build exist. Never invent screenshots or measured scores.
- Separate aesthetics from task efficiency and accessibility.

## Design quality checks
- Consistent spacing, type scale, radii, component states, color semantics and design tokens.
- Strong visual hierarchy, understandable primary action, restrained decoration and adequate whitespace.
- Responsive layout: test representative narrow mobile, tablet, desktop, extreme text zoom, and orientation as applicable.
- Handle long translations, RTL, mixed-direction data, and large dynamic content without clipping.
- Ensure forms have visible labels, clear inline errors, helpful hints, error summaries for long flows, and preserved user input.
- Provide states for loading, empty, success, error, offline and access denied; define their next action.
- Make destructive actions deliberate and reversible where feasible.
- Avoid manipulative dark patterns, hidden fees, misleading defaults, and unnecessary friction.

## Accessibility (WCAG 2.2 AA target where applicable)
- Keyboard reachability; logical focus order; visible focus indication; no traps; meaningful skip/navigation mechanisms.
- Use semantic HTML before ARIA. Buttons are buttons, links are links; interactive targets have accessible names.
- Sufficient contrast: typical targets 4.5:1 for normal text, 3:1 for large text; non-text contrast where required.
- Do not convey essential information via color alone. Support reduced motion and appropriate touch target sizing.
- Images need meaningful alt text, or empty alt for decorative content.
- Ensure modals manage focus and can be dismissed appropriately, with context retained.
- Label and announce important form errors, loading and success states when necessary.
- Verify at 200% text zoom and 400% reflow scenarios when possible; test with browser accessibility tree and screen reader.

## UI testing stack
- Static HTML heuristic: included `scripts/html_a11y.py` (partial signals only).
- Automated browser axe-core tests for supported screens, plus Playwright or equivalent for keyboard and flows.
- Manual screen-reader review, responsive viewports, device/browser testing, and task completion usability sessions.

## Deliverable
Include a prioritized critique with evidence, proposed hierarchy, component inventory, token changes, before/after interaction details, edge states, accessibility tradeoffs, and measurable acceptance criteria.
