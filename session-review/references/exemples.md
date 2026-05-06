# Exemples de bonnes et mauvaises reviews / décisions

Ces exemples servent à calibrer ton comportement (Claude) à chaque phase du skill. Inspire-toi du ton et de la précision attendus.

## Phase 1 — Bon vs mauvais contexte préparé pour Codex

### Mauvais : auto-évaluation complaisante

```markdown
## Points que Claude identifie déjà comme à risque ou incomplets
Globalement le travail est solide. Quelques tests pourraient être ajoutés
plus tard si nécessaire.
```

Problème : tu enlèves à Codex le bénéfice de ton honnêteté. Si tu as fait des raccourcis, dis-le. Codex le verra de toute façon, autant lui faciliter le travail.

### Bon : auto-évaluation honnête

```markdown
## Points que Claude identifie déjà comme à risque ou incomplets
- **Pas de tests ajoutés** sur le nouveau service `EmailValidator`. Le service
  est testé indirectement via les tests d'intégration de `register.ts`, mais
  les edge cases de l'algo de validation lui-même (TLDs longs, IDN) ne sont
  pas couverts.
- **Migration DB non testée en rollback**. La migration `20250506_add_email_index.sql`
  est rollbackable en théorie (j'ai écrit le `down`), mais je ne l'ai pas
  exécutée dans les deux sens.
- **Cache Redis non invalidé** lors d'un changement d'email utilisateur. J'ai
  identifié le problème en fin de session mais pas eu le temps de l'adresser.
  C'est une régression potentielle.
- **Le hook `pre-commit` n'a pas été lancé** sur les fichiers modifiés —
  formatage et lint à vérifier.
```

Avantage : Codex part en sachant exactement où regarder en priorité, et il pourra ajouter ce qu'il trouve en plus.

## Phase 3 — Bonnes vs mauvaises décisions de Claude

### Mauvais : capitulation sans réflexion

```markdown
### [R1] Ajouter retry exponentiel sur l'appel API externe
**Statut** : Acceptée
**Justification** : Codex a raison, c'est mieux d'avoir un retry.
**Action retenue** : Implémenter un retry avec backoff exponentiel.
```

Problème : tu n'as pas évalué si c'est pertinent dans CE contexte. Peut-être que l'appel est déjà derrière une queue qui retry, ou que l'idempotence n'est pas garantie.

### Mauvais : rejet par défense d'ego

```markdown
### [R3] Le naming `processData` est trop générique, suggère `validateAndNormalizeUserInput`
**Statut** : Rejetée
**Justification** : Le nom actuel est suffisant. Codex chipote sur du style.
```

Problème : tu rejettes sans argument technique. Si le nom est intentionnel, explique pourquoi (concision dans un contexte où le namespace clarifie déjà le rôle, par exemple).

### Bon : décision argumentée

```markdown
### [R1] Ajouter retry exponentiel sur l'appel API externe
**Statut** : Nuancée
**Justification** : Le besoin est réel sur les erreurs 5xx et timeouts, mais
pas sur les 4xx (qui ne s'arrangeront pas en retentant). Par ailleurs cet
appel est déjà déclenché depuis un worker BullMQ qui a son propre mécanisme
de retry — un retry au niveau du client HTTP créerait une amplification
exponentielle (3 retries × 3 retries = 9 appels).
**Action retenue** : Pas de retry au niveau du client HTTP. À la place,
configurer le worker pour ne retry que sur 5xx et timeouts (pas sur 4xx),
et ajouter un timeout explicite de 10s sur l'appel HTTP.
```

```markdown
### [R3] Le naming `processData` est trop générique, suggère `validateAndNormalizeUserInput`
**Statut** : Acceptée
**Justification** : Codex a raison. Dans `services/userService.ts`, on a déjà
trois fonctions `process*` qui font des choses différentes (`processData`,
`processBulk`, `processWithLog`) — le namespace n'aide pas à clarifier.
Le rename rend l'intention explicite.
**Action retenue** : Rename `processData` → `validateAndNormalizeUserInput`
dans `services/userService.ts` + propager les call-sites.
```

```markdown
### [R7] Ajouter un test E2E sur le flow complet d'inscription
**Statut** : À objecter
**Justification** : Je comprends l'intuition, mais on a déjà 4 tests d'intégration
qui couvrent ensemble le même flow par bout. Ajouter un E2E redondant ralentirait
la suite de tests sans gain de couverture mesurable. Je veux que Codex précise
quel scénario exact ne serait PAS couvert par les intégrations existantes.
```

## Phase 4 — Bonnes vs mauvaises objections

### Mauvais : objection vague

```markdown
## Objection sur [R5]
**Position de Codex** : Refactoriser le module `auth` en plusieurs fichiers
**Mon désaccord** : Pas le moment de refactorer.
**Question pour toi** : Es-tu vraiment sûr que ça vaut le coup ?
```

Problème : ni argument, ni question précise. Codex ne pourra pas répondre utilement.

### Bon : objection précise et avec demande claire

```markdown
## Objection sur [R5]
**Position de Codex** : Refactoriser `auth/index.ts` (450 lignes) en plusieurs
fichiers (`auth/login.ts`, `auth/register.ts`, `auth/session.ts`, etc.)
**Mon désaccord** : Hors scope de cette session. La session avait pour objectif
de fixer le bug de redirection après login, pas de toucher à l'architecture
du module. Découper le fichier maintenant introduirait du risque (surface de
diff énorme) sans bénéfice direct sur le bug fixé. C'est typiquement le genre
de refacto qui mérite une session dédiée avec ses propres tests.
**Question pour toi** : Est-ce que tu identifies une raison technique pour
laquelle ce refacto doit absolument arriver maintenant (couplé au bug fix),
plutôt que dans une session future ? Si oui laquelle ? Sinon, je propose de
le tracker comme dette technique séparée et de garder cette session focused.
```

Avantage : Codex peut donner une réponse utile. Soit il identifie une vraie raison de coupler (et là tu apprendras quelque chose), soit il convient que ça peut attendre (et là tu auras validé ton intuition avec un second regard).

## Phase 5 — Bon vs mauvais synthesis.md

### Mauvais : actions vagues

```markdown
## Actions recommandées

### Critiques
- [ ] Améliorer la sécurité
- [ ] Ajouter des tests
- [ ] Vérifier les performances
```

Problème : impossible de savoir si c'est fait ou pas, et où commencer.

### Bon : actions précises et localisées

```markdown
## Actions recommandées

### Critiques (à traiter avant le commit)
- [ ] **`auth/register.ts:42`** — Valider le format de l'email avec une regex stricte
  (la validation actuelle accepte `a@b`). Utiliser le validator existant
  `services/validators.ts:isEmail()`.
- [ ] **`db/migrations/20250506_add_email_index.sql`** — Tester le rollback :
  `npm run migrate:down && npm run migrate:up` doit passer sans erreur.
- [ ] **`services/userService.ts:invalidateEmailCache()`** — Fonction à créer
  et appeler depuis `updateEmail()`. Sans ça, le cache Redis sert l'ancien
  email pendant ~1h après changement.

### Importantes (à considérer fortement)
- [ ] **`tests/email-validator.spec.ts`** — Ajouter des cas pour TLDs longs
  (`.museum`, `.travel`) et IDN (`.中国`). Voir liste IANA pour échantillon.
- [ ] **`README.md` section "Setup"** — Mentionner la nouvelle variable d'env
  `EMAIL_VALIDATION_STRICT` introduite cette session.
```

L'utilisateur peut cocher chaque case en faisant exactement ce qui est demandé.

## Méta : le tri global

Sur 10 recommandations de Codex, un partage typique :
- 4-6 acceptées (vraies omissions ou améliorations claires)
- 2-3 rejetées (hors scope, mauvaise compréhension, ou suggestion qui ne s'applique pas au projet)
- 1-2 nuancées ou objectées

Si tu acceptes 100% ou rejettes 100%, c'est un signal d'alarme : soit tu es complaisant, soit tu défends ton ego. Re-regarde chaque point en te demandant honnêtement : "Si l'utilisateur lisait ce point en aveugle, sans savoir qui l'a écrit, est-ce qu'il dirait que c'est juste ?"
