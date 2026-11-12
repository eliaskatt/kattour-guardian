# Playground privacy and data handling

Kattour Guardian Playground is a static offline-first web application.

- **No application backend:** generating plans, prompts, acceptance criteria and exports runs in your browser. The code does not call a model provider.
- **Local storage:** saved sessions and templates use browser `localStorage` on the current origin. This storage is not encrypted, can be accessed by scripts on the same origin, and may be cleared by the browser. Do not store credentials or private information.
- **Optional shared brief link:** clicking *Share brief link* prompts for explicit consent. The project type, stack, mode, agent, detail level, goal and constraints are encoded in the URL fragment (`#brief=...`). URL fragments are not normally sent in HTTP requests, but **anyone receiving or viewing the link can read the brief**. Links may be exposed through chat previews, browser history, screenshots, extensions, or copy/paste. The app removes the fragment from the address bar after the receiver accepts/declines loading it.
- **Credential filtering:** common credential patterns and private-key headers are detected or redacted as a best-effort safety check. It is not a full DLP system. Human review is required.
- **Export/import:** Markdown, JSON and plain-text prompt exports use browser downloads. JSON imports are validated against the supported local schema and are regenerated as project briefs; raw output is not treated as trusted code.
- **Feedback:** clicking the GitHub Issues link navigates to GitHub, subject to GitHub's terms and privacy practices. No project brief is included in this link.
- **No automatic telemetry, ads, ratings manipulation or analytics cookies** are included in this release. Platform logs and browser behavior are separate from the application logic.

Do not input secret keys, private repositories, production data, user health details or anything you would not safely store in an unencrypted browser profile or optional share link.
