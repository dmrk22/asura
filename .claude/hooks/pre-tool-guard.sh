#!/usr/bin/env bash
# Blocks force pushes, rm -rf outside build dirs, and anything that prints secrets.
set -uo pipefail
payload=$(cat)
cmd=$(printf '%s' "$payload" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null) || exit 0
[ -z "$cmd" ] && exit 0

deny() { echo "BLOCKED by pre-tool-guard: $1" >&2; exit 2; }

printf '%s' "$cmd" | grep -qE 'push .*(--force|-f)([[:space:]]|$)' && deny "force push"

if printf '%s' "$cmd" | grep -qE 'rm[[:space:]]+(-[a-zA-Z]*[rR][a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*[rR])'; then
  printf '%s' "$cmd" | grep -qE 'rm[[:space:]]+-[a-zA-Z]+[[:space:]]+[^;|&]*(node_modules|\.next|dist|\.venv|build|__pycache__|\.pytest_cache|\.ruff_cache)' \
    || deny "rm -rf outside build dirs (allowed: node_modules .next dist .venv build __pycache__ .pytest_cache .ruff_cache)"
fi

printf '%s' "$cmd" | grep -qE '(cat|less|more|head|tail|bat|strings|xxd|od)[[:space:]]+[^;|&]*\.env([[:space:]]|$|[^.a-zA-Z])' && deny "reading .env"
printf '%s' "$cmd" | grep -qE 'grep[^;|&]*[[:space:]]\.env([[:space:]]|$)' && deny "grepping .env"
printf '%s' "$cmd" | grep -qE 'echo[[:space:]]+\$[A-Z_]*(API_KEY|TOKEN|SECRET|PASSWORD|DATABASE_URL|REDIS_URL)' && deny "printing a secret"
printf '%s' "$cmd" | grep -qE '(printenv|env)([[:space:]]|$)' && printf '%s' "$cmd" | grep -qE '(API_KEY|TOKEN|SECRET)' && deny "printing a secret"

exit 0
