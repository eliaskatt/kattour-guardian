# Offline visual regression (v0.8.0)

This is **optional** screenshot pixel comparison for a web app you are authorized to inspect. It does not judge design quality, detect all UX defects, certify WCAG compliance, or upload screenshots.

## Install

```bash
python -m pip install Pillow
# Optional: to capture local screenshots using the existing browser auditor
python -m pip install playwright
python -m playwright install chromium
```

## Capture and compare

Run two authorized local builds at the same URL or ports, using the **same viewport dimensions, OS, fonts, browser version and deterministic sample data**. Disable animations and nondeterministic content where possible. Use the bundled localhost-only browser auditor to capture screenshots:

```bash
python skills/kattour-guardian/scripts/browser_audit.py http://127.0.0.1:3000/ --screenshot-dir .guardian-baseline
# After your UI changes and restart at the same origin:
python skills/kattour-guardian/scripts/browser_audit.py http://127.0.0.1:3000/ --screenshot-dir .guardian-candidate
python scripts/visual_compare.py --baseline-dir .guardian-baseline --candidate-dir .guardian-candidate --pixel-threshold 15 --max-change-percent 1.0
```

The compare tool expects `guardian-mobile.png` and `guardian-desktop.png` in both directories. It returns only pixel counts, percent changed, bounding rectangles and mismatch status. Exit codes: **0** within threshold; **1** change requires review; **2** input/configuration error. Passing is not proof of correct UI. A change may be intentional; a screenshot can miss behavioral bugs.

## Privacy and security

Screenshots may contain personal information, account names, or secrets. Keep them **local**, outside tracked source; do not upload them as public GitHub artifacts or attach them to public PRs without explicit review. The tool refuses symlink screenshot files and oversized images. Pillow is an **optional** local dependency; core Skill and MCP server do not require it. For consistent baselines, pin fonts/browser/runtime and mask sensitive or dynamic content **before** capture, not by automatically exfiltrating screenshots for AI analysis.
