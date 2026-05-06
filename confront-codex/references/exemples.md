# Exemples — Calibrer le ton du débat

Ce fichier illustre ce qu'est un bon débat technique vs un mauvais débat. À consulter si tu te demandes comment formuler un point ou comment réagir à une critique de Codex.

## Bon débat : honnête, technique, sans ego

### Exemple 1 — Claude reconnaît que Codex a raison

**Round 1 Claude** : "J'utiliserai des contextes React pour partager l'état utilisateur entre les composants."

**Round 1 Codex** : "Le projet utilise déjà Zustand pour le state management (vu dans `src/stores/`). Introduire un Context React pour ce cas crée deux systèmes parallèles. Utilise le store Zustand existant."

**Round 2 Claude** :
> ## Points où je rejoins Codex
> - **Gestion d'état** : Codex a raison, j'avais raté la présence de Zustand. Utiliser un Context en parallèle créerait une incohérence architecturale. J'ajuste : l'état utilisateur sera ajouté au store Zustand existant dans `src/stores/userStore.ts`.

C'est bien parce que : reconnaissance directe, explication de l'erreur initiale, ajustement concret.

### Exemple 2 — Claude tient sa position

**Round 1 Claude** : "Pour la validation des formulaires, j'utiliserai Zod côté frontend et côté backend, avec un schéma partagé dans `packages/shared/`."

**Round 1 Codex** : "Le double validation est redondant. Valide uniquement côté backend, c'est suffisant et plus simple."

**Round 2 Claude** :
> ## Points où je tiens ma position
> - **Validation Zod côté frontend** : Je maintiens. La validation backend seule signifie que l'utilisateur attend le round-trip réseau pour voir ses erreurs de saisie, ce qui dégrade fortement l'UX sur les longs formulaires. Le schéma partagé évite la duplication de logique — c'est exactement le pattern que Zod permet via `packages/shared/`. Le coût (quelques ko de JS supplémentaires) est largement justifié par le gain UX. La validation backend reste évidemment présente comme garde-fou de sécurité.

C'est bien parce que : argument technique précis, prend en compte la critique sans céder, explique le trade-off.

## Mauvais débat : à éviter

### Anti-exemple 1 — Capitulation par politesse

**Round 1 Codex** : "Tu devrais utiliser MongoDB au lieu de PostgreSQL."

**Round 2 Claude (mauvais)** : "Tu as raison, je vais passer sur MongoDB."

Pourquoi c'est mauvais : aucune analyse de l'argument de Codex (qui d'ailleurs n'a même pas donné d'argument ici). Si le projet a des relations complexes, MongoDB peut être un mauvais choix. Capituler sans réfléchir trahit la mission du débat.

**Bonne version** : "Codex propose MongoDB sans argument. Je maintiens PostgreSQL parce que [contraintes du projet : relations entre entités, besoin de transactions ACID, équipe familière avec SQL]. Si Codex avait des arguments concrets, je les évaluerais."

### Anti-exemple 2 — Défense crispée sans considération

**Round 1 Codex** : "Le découpage des composants en `Header`, `MainContent`, `Footer` est trop générique. Pour une app de chat, des composants comme `MessageList`, `ConversationSidebar`, `ComposerInput` seraient plus alignés avec le domaine."

**Round 2 Claude (mauvais)** : "Mon découpage est correct. `Header`/`MainContent`/`Footer` est un pattern standard."

Pourquoi c'est mauvais : Codex fait un point valide sur l'alignement avec le domaine, qui n'est pas adressé. La défense est purement formelle.

**Bonne version** : "Codex a raison sur le principe — un découpage par domaine est plus parlant qu'un découpage géographique pour une app métier. J'ajuste : `MessageList`, `ConversationSidebar`, `Composer` au top-level. `Header` reste comme composant mineur dans la `ConversationSidebar`."

### Anti-exemple 3 — Débat qui tourne en rond

Si au round 3 tu te retrouves à répéter les mêmes arguments qu'au round 1 sans nouvelle information, c'est le signal qu'il faut soit :
- Demander à l'utilisateur d'arbitrer
- Proposer explicitement une voie de compromis qui n'a pas été explorée

Ne refais pas un round 4 qui répète round 2. Ça ne sert plus.

## Calibrage du ton de Codex

Codex peut être plus catégorique que toi par défaut. Ce n'est pas un problème — c'est même utile. Si Codex dit "ce choix est mauvais" sans nuances, lis ses arguments avant de réagir au ton. Le fond compte plus que la forme.

Si à l'inverse Codex est trop complaisant et valide tout sans critiquer, c'est suspect. Dans ce cas, dans le round suivant, tu peux explicitement lui demander d'être plus critique : "Codex a validé sans réserve. Je voudrais m'assurer qu'il a réellement examiné [point sensible X]." Et le prompt round-N peut être ajusté pour réinjecter de l'esprit critique.
