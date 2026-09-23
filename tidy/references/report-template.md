# Modèle du rapport tidy

À recopier dans `docs/tidy/report-AAAA-MM-JJ.md`, en remplaçant les `<…>` et en répétant chaque section autant de fois que nécessaire.

```markdown
# Tidy report — <date longue>

**Repo** : `<nom>`
**Branche** : `<branche>`
**Mode** : default | --deep
**Fichiers analysés** : <n>
**Propositions** : <X déplacements, Y archivages, Z suppressions, W alertes sécu, Q questions>

---

## 🗂️ Réorganisation (déplacements)

> Exécutés via `git mv`. Réversible avec `git mv` inverse.

### `<chemin/source.md>` → `<chemin/cible.md>`

**Pourquoi** : <raison concise, 1-2 phrases>
**Références à mettre à jour** : <liste de fichiers qui pointent vers l'ancien chemin, ou « aucune »>

```bash
git mv "<source>" "<cible>"
```

<répéter pour chaque déplacement>

---

## 📦 Archivage

> Déplacement vers `docs/archives/<topic>/`. Le fichier reste lisible, on déclare juste qu'il n'est plus actif.

### `<chemin/source.md>` → `docs/archives/<topic>/<nom>.md`

**Pourquoi** : <raison : feature livrée, débat clos, plan abandonné…>
**Preuves** :
- <commit sha qui livre la feature : « feat(x): … »>
- <ou : section du code qui implémente la décision>

```bash
mkdir -p "docs/archives/<topic>"
git mv "<source>" "docs/archives/<topic>/<nom>.md"
```

<répéter>

---

## 🗑️ Suppressions proposées

> ⚠️ Action irréversible (récupérable seulement via `git revert` ou `git reflog`).
> Chaque suppression demandera une confirmation explicite.

### `<chemin/file>`

**Pourquoi** : <raison>
**Vérifications effectuées** :
- Aucune référence trouvée : `git grep "<basename>"` → 0 résultat
- Dernier commit : <date>
- Contenu : <résumé en une ligne>

```bash
git rm "<file>"
```

<répéter>

---

## 🔐 Sécurité

### CRITIQUE — <titre>

**Fichier** : `<path>:<ligne>`
**Type** : <AWS key | Anthropic key | …>
**Dans l'historique git** : oui (commit `<sha>`, il y a <durée>) / non
**Action recommandée** :
1. <…>
2. <…>

<répéter pour chaque alerte, ordonnées par gravité>

---

## ❓ Questions en suspens

Décisions que je n'ai pas su trancher seul. Réponds dans la session, ce ne sera pas exécuté tant que tu ne valides pas.

### Q1 — `<file>`

**Situation** : <description neutre>
**Hypothèses** :
- (a) Garder tel quel — <conséquence>
- (b) Déplacer vers `<x>` — <conséquence>
- (c) Archiver — <conséquence>
- (d) Supprimer — <conséquence>

**Ma recommandation** : <a/b/c/d> parce que <raison>

<répéter>

---

## Plan d'exécution

Le skill va te proposer chaque catégorie séquentiellement :

1. 🗂️ Réorganisation (sûre, réversible facilement)
2. 📦 Archivage (sûre, réversible facilement)
3. 🗑️ Suppressions (irréversible — confirmation supplémentaire)
4. 🔐 Sécurité (action par action)
5. ❓ Questions (réponses dans la conversation)

Tu peux à chaque étape : **GO** (tout valider), **EDIT** (modifier la liste), **SKIP** (passer cette catégorie), **STOP** (arrêter complètement).
```
