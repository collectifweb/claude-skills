#!/usr/bin/env bash
# Hook PreCompact (matcher: "auto") — filet de sécurité pour la compaction
# automatique (déclenchée par Claude Code quand le contexte est plein).
#
# Contrairement au hook "manual", celui-ci NE BLOQUE JAMAIS : bloquer une
# compaction automatique risquerait d'empêcher Claude Code de libérer du
# contexte quand il en a réellement besoin, ce qui peut planter la session.
# Il se contente de sauvegarder le transcript brut, en tâche async, comme
# dernier filet de sécurité si le handoff manuel n'a pas été fait à temps.
#
# Installation : voir references/settings-snippet.json (penser à "async": true)

set -euo pipefail

INPUT=$(cat)

TRANSCRIPT_PATH=$(echo "$INPUT" | grep -o '"transcript_path" *: *"[^"]*"' | sed 's/.*"\(\/[^"]*\)"$/\1/' || true)

if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
  exit 0
fi

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  PROJECT_ROOT=$(git rev-parse --show-toplevel)
else
  PROJECT_ROOT="$(pwd)"
fi

BACKUP_DIR="$PROJECT_ROOT/.claude/handoff/auto-backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
cp "$TRANSCRIPT_PATH" "$BACKUP_DIR/transcript-${TIMESTAMP}.jsonl" 2>/dev/null || true

# Garde seulement les 10 derniers backups auto pour ne pas accumuler indéfiniment.
ls -t "$BACKUP_DIR"/transcript-*.jsonl 2>/dev/null | tail -n +11 | xargs -r rm -f

exit 0
