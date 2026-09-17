#!/usr/bin/env bash
# Prints the session's orientation: state, recent commits, current phase plan head.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0
echo "=== docs/STATE.md ==="
[ -f docs/STATE.md ] && cat docs/STATE.md || echo "(no STATE.md yet — run /setup)"
echo
echo "=== git log -10 ==="
git log --oneline -10 2>/dev/null || echo "(no commits yet)"
echo
plan=$(ls -1t docs/superpowers/plans/*.md 2>/dev/null | head -1)
if [ -n "$plan" ]; then echo "=== current plan: $plan ==="; head -30 "$plan"; fi
exit 0
