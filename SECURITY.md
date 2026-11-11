# Security policy

Kattour Guardian is an instruction and local heuristic tooling package. It does **not** guarantee that software under review is secure. It does not send scanned source to a server, require API keys, or run a remote scanner by default. The chosen AI coding agent may process user-provided code under its own service terms; inspect its privacy and data-handling settings independently.

## Reporting a security concern
Please avoid posting real secrets, exploitable production targets or personal data in public issues. Contact the project maintainer privately using the GitHub repository's security advisory reporting feature if it is available. If you accidentally exposed credentials, rotate/revoke them immediately.

## Trust and authorization
- Install and run this repository only after reviewing its code.
- Do not grant it access to production or external systems by default.
- Review third-party dependencies and CI actions before enabling privileged workflows.
- Use the included heuristic checks only as an early signal; security assessment requires broader review and testing.
