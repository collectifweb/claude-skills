#!/usr/bin/env bash
# Hook PreCompact (matcher: "manual") — bloque /compact si le handoff
# (.claude/handoff/.state.json, écrit par le skill "handoff") n'a pas été
# régénéré depuis les derniers changements du projet, ou est trop ancien.
#
# Exit 0 => compaction autorisée à continuer normalement.
# Exit 2 => compaction bloquée, le message stderr est renvoyé à Claude
#           comme erreur ; Claude peut alors lancer le skill "handoff"
#           lui-même puis l'utilisateur retente /compact.
#
# Installation : voir references/settings-snippet.json

set -euo pipefail

# Ce hook ne s'applique qu'à l'intérieur d'un dépôt git.
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  exit 0
fi

cd "$(git rev-parse --show-toplevel)"

STATE_FILE=".claude/handoff/.state.json"
MAX_AGE_MINUTES="${HANDOFF_MAX_AGE_MINUTES:-120}"

# Pas de handoff du tout => on bloque directement.
if [ ! -f "$STATE_FILE" ]; then
  echo "Aucun handoff enregistré pour l'état actuel du projet. Lance le skill \"handoff\" avant de compacter, puis relance /compact." >&2
  exit 2
fi

CURRENT_HASH=$(git status --porcelain | sha256sum | cut -d' ' -f1)
CURRENT_HEAD=$(git rev-parse HEAD 2>/dev/null || echo "no-commit")

# Extraction simple (le fichier est écrit par nous-mêmes, format connu et stable).
STORED_HASH=$(grep -o '"hash": *"[^"]*"' "$STATE_FILE" | sed 's/.*"\([a-f0-9]*\)"$/\1/')
STORED_HEAD=$(grep -o '"head": *"[^"]*"' "$STATE_FILE" | sed 's/.*"\(.*\)"$/\1/')
STORED_TS=$(grep -o '"timestamp": *"[^"]*"' "$STATE_FILE" | sed 's/.*"\(.*\)"$/\1/')

AGE_MINUTES=999999
if command -v python3 >/dev/null 2>&1; then
  AGE_MINUTES=$(python3 - "$STORED_TS" <<'PYEOF'
import sys, datetime
try:
    stored = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    print(int((now - stored).total_seconds() // 60))
except Exception:
    print(999999)
PYEOF
)
fi

STALE_REASON=""
if [ "$CURRENT_HASH" != "$STORED_HASH" ]; then
  STALE_REASON="des changements non commités ont eu lieu depuis le dernier handoff"
elif [ "$CURRENT_HEAD" != "$STORED_HEAD" ]; then
  STALE_REASON="le commit HEAD a changé depuis le dernier handoff"
elif [ "$AGE_MINUTES" -gt "$MAX_AGE_MINUTES" ]; then
  STALE_REASON="le handoff date de plus de ${MAX_AGE_MINUTES} minutes (${AGE_MINUTES} min)"
fi

if [ -n "$STALE_REASON" ]; then
  echo "Handoff périmé : ${STALE_REASON}. Relance le skill \"handoff\" avant de compacter, puis relance /compact." >&2
  exit 2
fi

exit 0
