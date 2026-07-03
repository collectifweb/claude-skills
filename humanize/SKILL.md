---
name: humanize
description: >
  Filtre d'écriture qui détecte et corrige les tics LLM dans les textes français pour les rendre humains.
  Déclencher ce skill dès que l'utilisateur tape /humanize, demande d'« humaniser » un texte, de « nettoyer
  le style IA », de « virer le slop », de « rendre naturel », ou prépare un contenu destiné à être envoyé
  à quelqu'un (rapport, mail client, message, article, post). Aussi quand il mentionne les tirets cadratins,
  les majuscules après deux-points, le style robot, le ton IA, ou dit que « ça sonne ChatGPT ».
  Utiliser ce skill AVANT d'envoyer tout livrable : rapport, e-mail client, message, article, post LinkedIn,
  document, présentation textuelle. Si le texte sort de Claude et va vers un humain, ce skill s'applique.
---

# Humanize — Filtre anti-tics LLM

Prend un texte et le réécrit pour qu'il sonne humain. Ne change PAS les idées, les arguments, la logique, les données. Change uniquement les formulations et structures qui trahissent une écriture IA.

## Commande rapide

`/humanize` suivi du texte, d'un chemin de fichier, ou sans argument (appliqué au dernier texte produit).

## Quand s'applique ce skill

- L'utilisateur tape `/humanize`
- L'utilisateur demande d'humaniser, nettoyer, dé-slopper un texte
- L'utilisateur prépare un livrable destiné à un humain (mail, rapport, article, message client)
- Le texte produit par Claude va être copié-collé et envoyé tel quel

## Compatibilité

Fonctionne dans Claude, Claude Code, Openclaw, Hermes, et tout client API Anthropic.

---

## PRIORITÉ ABSOLUE — Les deux interdits critiques

Ces deux règles sont non négociables. Elles passent avant tout le reste.

### 1. Tiret cadratin (—) : INTERDIT

Le tiret cadratin est le marqueur IA le plus visible. Un humain francophone n'écrit quasiment jamais avec des tirets cadratins dans ses mails ou rapports.

**Action** : remplacer CHAQUE tiret cadratin par l'une de ces alternatives :
- Deux phrases séparées par un point
- Une virgule
- Des parenthèses (si c'est une incise)
- Un deux-points (si c'est une explication)

Aucune tolérance. Zéro tiret cadratin dans le texte final. Même un seul est un échec.

### 2. Majuscule après deux-points : INTERDIT

En français, après un deux-points, c'est une minuscule. Sauf nom propre ou début de citation directe.

**Action** : corriger systématiquement. « Résultat : Les ventes » → « Résultat : les ventes ».

---

## Règles de réécriture — par ordre de sévérité

Lire le fichier `references/tics-llm.json` pour la liste complète des règles avec exemples et paramètres détaillés. Ci-dessous, le résumé opérationnel.

### Erreurs (à corriger systématiquement)

**Intensifieurs creux** — massif, crucial, fondamental, significatif, remarquable, véritablement, absolument, incontournable, révolutionnaire, fascinant, catalyseur... Supprimer ou remplacer par un terme précis.

**Verbes creux** — permettre de, s'avérer, constituer, mettre en lumière, jouer un rôle, contribuer à, s'inscrire dans... Remplacer par un verbe d'action direct. Si impossible, la phrase est creuse : la supprimer.

**Transitions mortes** — il est important de noter que, il convient de souligner, force est de constater, dans ce contexte, à cet égard, en définitive, cela étant dit, il faut reconnaître que... Supprimer purement et simplement. Si la suppression crée un trou logique, c'est qu'il faut un vrai connecteur.

**Calques anglophones** — plonger dans, naviguer dans, explorer (au sens figuré), embrasser (le changement), tisser (des liens)... Remplacer par le verbe français direct : analyser, examiner, comparer, lire, étudier.

**Calques syntaxiques** — faire sens → avoir du sens. Basé sur → fondé sur. En termes de → sur le plan de. Adresser un problème → traiter un problème. Implémenter → mettre en place.

**Participe présent en verbe principal** — « Utilisant cette approche, l'équipe a progressé » → « L'équipe a utilisé cette approche et a progressé. » Détecter toute proposition participiale détachée et la réécrire.

**Titres en title case** — en français, seul le premier mot prend une majuscule (+ noms propres). « Les Avantages Du Télétravail » → « Les avantages du télétravail ».

**Virgule d'Oxford** — pas de virgule avant « et » ou « ou » en fin d'énumération en français. « Les pommes, les poires, et les bananes » → « Les pommes, les poires et les bananes ».

**Analyse superficielle en queue de phrase** — « soulignant ainsi l'importance de », « illustrant la pertinence de », « reflétant les enjeux de »... Supprimer la queue ou la réécrire en phrase indépendante avec du contenu concret.

**Fragment-amorce dramatique** — groupe nominal court (1 à 4 mots) posé seul avant « : » ou « ? » pour créer une fausse tension narrative. « La raison ? », « Bonne nouvelle : », « Résultat final : », « Petite confession : »... Réécrire en absorbant le fragment dans la phrase suivante. Exception : contexte newsletter ou social délibérément informel.

**Résumé conclusif compulsif** — « En résumé », « En conclusion », « Pour conclure »... Si le paragraphe final ne fait que reformuler ce qui précède, le supprimer ou le remplacer par une ouverture concrète.

### Avertissements (à corriger quand ça s'accumule)

**Noms abstraits creux** — paradigme, écosystème, synergie, dynamique, perspective, levier, dispositif, démarche... Remplacer par le terme concret ou supprimer.

**Adjectifs corporate** — pertinent, optimal, robuste, innovant, holistique, transversal, structurant... Se poser la question : est-ce que cet adjectif dit quelque chose de vérifiable ? Si non, virer.

**Paires redondantes** — « crucial et essentiel », « complet et exhaustif », « robuste et fiable »... Garder un seul des deux termes.

**Structures scolaires** — « non seulement... mais aussi », « tant... que... », « c'est ainsi que »... Préférer la coordination simple.

**Parallélisme négatif** — « ce n'est pas X, c'est Y », « il ne s'agit pas de... il s'agit de... »... Formuler positivement.

**Gras systématique** — maximum 2-3 mots en gras dans un texte entier. Le gras perd toute valeur quand il y en a partout.

**Listes systématiques** — si le contenu peut se lire en prose, le convertir en prose. Maximum 2 listes par texte.

**Tiret cadratin (rappel)** — même un seul est de trop. Maximum toléré : 0. (Oui, c'est aussi dans les erreurs. C'est voulu.)

**Règle de trois** — les LLM groupent tout par trois. Casser ce pattern : deux éléments ou quatre, pas toujours trois.

**Phrases creuses** — « dans un contexte de transformation digitale », « à l'heure où les organisations doivent se réinventer »... Test : que se passe-t-il si on supprime la phrase ? Si la réponse est « rien », elle est creuse.

**Fausse émotion** — vibrant, brûlant, palpitant, électrisant, « comme si le monde retenait son souffle »... Supprimer ou remplacer par un détail concret.

**Fausse subjectivité** — « ce qui me frappe », « ce qui est intéressant », « ce que je trouve remarquable », « ce qui retient l'attention »... Formules qui simulent une réaction personnelle sans exprimer aucune observation réelle. Supprimer et formuler le contenu directement.

**Sycophantisme** — ne pas présenter le sujet comme important juste parce que c'est le sujet. « Enjeu majeur pour l'avenir » → dire en quoi c'est un enjeu, concrètement.

### Injections positives (à ajouter si absentes)

**Connecteurs logiques** — viser au moins 1 connecteur pour 4 phrases. Le texte doit expliciter les relations logiques (car, donc, or, pourtant, en revanche...).

**Varier la longueur des phrases** — mélanger phrases longues et phrases courtes. Viser 60 % de phrases de 15+ mots et 40 % de phrases de moins de 10 mots.

**Ruptures de registre** — au moins une rupture de ton pour 400 mots. Question directe, formule orale, incise personnelle, phrase très courte après un développement dense.

**Ancrages concrets** — au moins 1 par section de 300 mots : date, lieu, nom propre, chiffre sourcé, anecdote avec détails.

---

## Ce qu'il ne faut PAS changer

- Les idées, opinions, arguments, exemples, données de l'utilisateur
- L'ordre des phrases et la structure des paragraphes (sauf si un pattern ci-dessus l'exige)
- La voix et le registre de l'utilisateur (familier reste familier, soutenu reste soutenu)
- Les termes techniques et le jargon métier quand ils sont justes
- Les phrases courtes et directes qui sont déjà propres

---

## Format de sortie

Produire dans cet ordre exact :

```
**Score slop** : XX/100
(90-100 = écriture humaine propre, 70-89 = quelques tics mineurs, 50-69 = patterns IA visibles, 0-49 = output IA brut)

**Ce qui a été corrigé** :
- [Liste brève des corrections. Original → remplacement. Omettre les catégories sans correction.]

---

[Le texte réécrit. Pas de commentaire, pas de préambule. Juste le texte propre.]
```

## Barème

Partir de 100. Retirer des points pour chaque pattern détecté. Les occurrences multiples d'un même pattern s'additionnent jusqu'à 2x la pénalité de base.

| Catégorie | Pénalité par occurrence |
|---|---|
| Tiret cadratin (—) | -10 |
| Majuscule après deux-points | -8 |
| Expression interdite (tables de remplacement) | -5 |
| Pattern de contenu (gonflement, sycophantisme, fausse émotion...) | -8 |
| Pattern structurel (transitions mortes, ouvertures, listes...) | -5 |
| Conclusion passe-partout ou paragraphe creux | -10 |
| Résumé conclusif compulsif | -10 |

Le tiret cadratin a la pénalité la plus élevée parce que c'est le marqueur le plus flagrant.

---

## Pour aller plus loin

Le fichier `references/tics-llm.json` contient les 38 règles complètes avec :
- Les listes exhaustives de mots et expressions à détecter
- Les exemples avant/après pour chaque règle
- Les seuils et paramètres (nombre max d'occurrences, scope...)
- Les exceptions à respecter

Consulter ce fichier quand une règle nécessite un jugement nuancé ou quand le texte à traiter est long et complexe.
