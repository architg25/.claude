#!/bin/bash
# Security blocking hook — blocks dangerous commands and protects sensitive files.
# Replaces security-block.py (bash is ~300ms faster due to no Python startup).
# Also includes the git-commit advisory (merged from standalone jq hook).

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')

if [[ "$TOOL" == "Bash" ]]; then
  CMD=$(echo "$INPUT" | jq -r '.tool_input.command')

  # Block dangerous patterns
  if echo "$CMD" | grep -qE 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|rf|-[a-zA-Z]*f[a-zA-Z]*r)\s'; then
    echo "BLOCKED: rm -rf variant" >&2; exit 2
  fi
  if echo "$CMD" | grep -qE '>\s*/dev/(?!null|stderr|stdout)'; then
    echo "BLOCKED: redirect to /dev device" >&2; exit 2
  fi
  if echo "$CMD" | grep -qE ':\(\)\s*\{'; then
    echo "BLOCKED: fork bomb" >&2; exit 2
  fi
  if echo "$CMD" | grep -qE 'curl\s+.*\|\s*(ba)?sh|wget\s+.*\|\s*(ba)?sh'; then
    echo "BLOCKED: piped download to shell" >&2; exit 2
  fi
  if echo "$CMD" | grep -qE 'mkfs\.|dd\s+if='; then
    echo "BLOCKED: destructive disk command" >&2; exit 2
  fi

  # Advisory for git commits (merged from standalone jq hook)
  if echo "$CMD" | grep -q "git commit"; then
    echo '{"additionalContext": "Before committing, ensure tests pass and code is formatted."}'
  fi

elif [[ "$TOOL" =~ ^(Edit|Write|MultiEdit)$ ]]; then
  FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path')

  # Block protected file patterns
  if echo "$FILE" | grep -qiE '\.env$|\.env\.|\.git/|credentials|secrets|id_rsa|id_ed25519|\.pem$|\.key$|password|\.netrc|\.npmrc|\.pypirc'; then
    echo "BLOCKED: protected file pattern" >&2; exit 2
  fi
fi

exit 0
