#!/usr/bin/env bash
# Exit 2 if apps/ changed this turn but docs/STATE.md did not.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
changed=$(git status --porcelain 2>/dev/null)
echo "$changed" | grep -qE '^\s*[AMR?]{1,2}\s+apps/' || exit 0
echo "$changed" | grep -qE '^\s*[AMR?]{1,2}\s+docs/STATE\.md' && exit 0
echo "apps/ changed but docs/STATE.md did not. Update docs/STATE.md (phase, task, blockers, next action) before stopping." >&2
exit 2
