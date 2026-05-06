# Extraction du contenu de la session Claude Code courante

## Localisation du fichier de session

Les sessions sont stockées dans `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`, où `encoded-cwd` est le chemin absolu courant avec chaque caractère non-alphanumérique remplacé par `-`.

```bash
# Identifier le dossier de sessions du projet courant
PROJECT_DIR=$(pwd | sed 's|[^a-zA-Z0-9]|-|g')
SESSIONS_DIR="$HOME/.claude/projects/${PROJECT_DIR}"

# Fallback : nouveau chemin Claude Code v1.0.30+
if [ ! -d "$SESSIONS_DIR" ]; then
  SESSIONS_DIR="$HOME/.config/claude/projects/${PROJECT_DIR}"
fi

# Identifier la session courante (la plus récemment modifiée)
CURRENT_SESSION=$(ls -t "$SESSIONS_DIR"/*.jsonl 2>/dev/null | head -1)
```

**Note** : si plusieurs sessions Claude Code tournent en parallèle dans le même projet, l'heuristique "fichier le plus récent" peut être trompeuse. Vérifie avec `ls -lt "$SESSIONS_DIR"/*.jsonl | head -3` que la session identifiée est bien celle attendue (modifiée à l'instant).

## Format des entrées JSONL

Chaque ligne du fichier `.jsonl` est un objet JSON. Les champs principaux :

- `type` : `"user"` (message utilisateur) ou `"assistant"` (réponse Claude)
- `timestamp` : ISO 8601
- `message.content` : le contenu du message (texte ou array de blocs)
- `uuid` : identifiant du message
- `parentUuid` : référence au message parent (chaîne de conversation)

Pour les messages assistant, `message.content` peut contenir des blocs typés : `text`, `tool_use`, `tool_result`. Les blocs `tool_use` indiquent les outils que Claude a appelés (Read, Edit, Bash, etc.).

## Stratégie d'extraction pour la review

Tu as un budget tokens limité côté codex. Extrait intelligemment plutôt que tout coller :

### Ce qui est essentiel à extraire

1. **Premiers 2-3 messages utilisateur** : ils posent l'objectif initial de la session
2. **Tous les messages utilisateur** suivants : ils tracent les pivots, corrections, nouvelles demandes
3. **Synthèse des actions de Claude** : pas le verbatim complet, mais les outils appelés et les décisions prises (extraits des `tool_use` et des messages texte assistant les plus structurants)

### Ce qui peut être résumé / omis

- Les retours de tool (`tool_result`) volumineux : extraits de fichiers lus, sorties de commandes longues — mentionne juste "lecture de X" ou "commande Y exécutée"
- Les messages assistant intermédiaires de pure exécution sans décision (ex: "OK, je lance la commande...")

### Script Python d'extraction recommandé

Voici un script à exécuter pour produire un résumé structuré que tu colleras ensuite dans `01-context.md` :

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

session_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])

user_msgs = []
assistant_decisions = []  # Messages assistant texte de plus de 100 chars
tool_calls = []  # Récap des outils appelés

with session_path.open() as f:
    for line in f:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        if entry.get("type") == "user":
            content = entry.get("message", {}).get("content", "")
            if isinstance(content, list):
                # Filtrer les tool_results, garder uniquement le texte utilisateur réel
                texts = [b.get("text", "") for b in content if b.get("type") == "text"]
                content = "\n".join(t for t in texts if t)
            if content and isinstance(content, str) and not content.startswith("<system"):
                user_msgs.append({
                    "ts": entry.get("timestamp", ""),
                    "text": content[:2000]  # Cap par message
                })

        elif entry.get("type") == "assistant":
            content = entry.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if block.get("type") == "text":
                        text = block.get("text", "")
                        if len(text) > 100:
                            assistant_decisions.append({
                                "ts": entry.get("timestamp", ""),
                                "text": text[:1500]
                            })
                    elif block.get("type") == "tool_use":
                        tool_calls.append({
                            "ts": entry.get("timestamp", ""),
                            "name": block.get("name", ""),
                            "input_summary": str(block.get("input", ""))[:200]
                        })

# Composition du résumé
out = []
out.append(f"# Extraction de session\n\nFichier source : `{session_path}`\n")
out.append(f"\n## Messages utilisateur ({len(user_msgs)})\n")
for i, m in enumerate(user_msgs, 1):
    out.append(f"\n### [U{i}] {m['ts']}\n```\n{m['text']}\n```\n")

out.append(f"\n## Décisions/explications de Claude ({len(assistant_decisions)})\n")
# Limiter aux 30 plus longues décisions pour éviter saturation
top_decisions = sorted(assistant_decisions, key=lambda d: -len(d["text"]))[:30]
top_decisions.sort(key=lambda d: d["ts"])
for i, d in enumerate(top_decisions, 1):
    out.append(f"\n### [A{i}] {d['ts']}\n```\n{d['text']}\n```\n")

out.append(f"\n## Outils appelés par Claude ({len(tool_calls)})\n")
# Récap des tools sans verbatim
from collections import Counter
tool_counter = Counter(t["name"] for t in tool_calls)
for name, count in tool_counter.most_common():
    out.append(f"- `{name}` : {count}x\n")

# Aussi : les premiers et derniers appels pour donner une chronologie
out.append("\n### Chronologie (premiers 10 et derniers 10 appels)\n")
chronological = sorted(tool_calls, key=lambda t: t["ts"])
selected = chronological[:10] + (chronological[-10:] if len(chronological) > 20 else [])
for t in selected:
    out.append(f"- `{t['ts']}` `{t['name']}` — {t['input_summary']}\n")

output_path.write_text("\n".join(out))
print(f"Extraction écrite dans : {output_path}")
print(f"  - {len(user_msgs)} messages utilisateur")
print(f"  - {len(assistant_decisions)} décisions Claude (top 30 conservées)")
print(f"  - {len(tool_calls)} appels d'outils")
```

Sauvegarde ce script dans `/tmp/extract-session.py` et lance-le :

```bash
python3 /tmp/extract-session.py "$CURRENT_SESSION" /tmp/session-extract.md
cat /tmp/session-extract.md  # Pour vérifier
```

Tu colleras ensuite ce contenu (ou une version condensée) dans la section "Résumé chronologique des échanges" de `01-context.md`.

## Cas particulier : session reprise (`/resume`)

Si la session courante a été reprise depuis une précédente avec `/resume`, le `.jsonl` contient l'historique des deux sessions. Pour un review pertinent, tu peux choisir de :

- **Tout reviewer** (défaut) : laisse l'extraction complète
- **Reviewer seulement la partie récente** : filtre par timestamp (ex: garde les messages des 4 dernières heures)

```python
# Filtre temporel optionnel à ajouter dans le script ci-dessus
from datetime import datetime, timedelta, timezone

cutoff = datetime.now(timezone.utc) - timedelta(hours=4)
# ... dans la boucle :
ts = entry.get("timestamp", "")
if ts:
    msg_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if msg_dt < cutoff:
        continue
```

Demande à l'utilisateur si la session est très longue (>200 messages utilisateur) : "La session contient X échanges. Je review tout, ou seulement la partie récente (préciser une période) ?"

## Si l'extraction échoue

Si tu n'arrives pas à localiser la session courante (dossier introuvable, plusieurs candidats), demande à l'utilisateur de te coller manuellement un résumé de la session, ou simplement de te lister les objectifs/demandes principales. Le diff git restera disponible et représente déjà la moitié du contexte utile pour Codex.
