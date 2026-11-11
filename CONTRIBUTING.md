# Contributing

Contributions that improve reproducibility, honest reporting, accessibility, and defensive security are welcome.

1. Open an issue describing the problem, intended users and observable acceptance criteria.
2. Avoid new runtime dependencies unless absolutely needed; justify each one.
3. Keep skill guidance portable and vendor-neutral; never include hidden prompts to exfiltrate data.
4. Add regression tests for new heuristic rules, including false-positive cases.
5. Validate locally:
   `python scripts/validate.py`
   `python -m unittest discover -s tests -v`
6. Do not submit production secrets, private data, or intrusive exploit code.

See SECURITY.md for privately reporting sensitive security issues.
