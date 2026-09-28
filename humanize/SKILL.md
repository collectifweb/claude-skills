---
name: humanize
description: >
  Filtre d'écriture qui détecte et corrige les tics LLM dans les textes français pour les rendre humains.
  Déclencher ce skill dès que l'utilisateur tape /humanize, demande d'« humaniser » un texte, de « nettoyer
  le style IA », de « virer le slop », de « rendre naturel », ou prépare un contenu destiné à être envoyé
  à quelqu'un (rapport, mail client, message, article, post). Aussi quand il mentionne les tirets cadratins,
  les majuscules après deux-points, le style robot, le ton IA, ou dit que « ça sonne ChatGPT ».
  Aussi pour retirer un filigrane (« watermark ») ou des caractères invisibles d'un texte.
  Utiliser ce skill AVANT d'envoyer tout livrable : rapport, e-mail client, message, article, post LinkedIn,
  document, présentation textuelle. Si le texte sort de l'IA et va vers un humain, ce skill s'applique.
---

# Humanize — Filtre anti-tics LLM

Prend un texte et le réécrit pour qu'il sonne humain. Ne change PAS les idées, les arguments, la logique, les données. Change uniquement les formulations et structures qui trahissent une écriture IA.

## Commande rapide

`/humanize` suivi du texte, d'un chemin de fichier, ou sans argument (appliqué au dernier texte produit).

## Quand s'applique ce skill

- L'utilisateur tape `/humanize`
- L'utilisateur demande d'humaniser, nettoyer, dé-slopper un texte
- L'utilisateur prépare un livrable destiné à un humain (mail, rapport, article, message client)
- Le texte produit par l'IA va être copié-collé et envoyé tel quel

## Compatibilité

Un seul outil, facultatif : Python 3 (sans dépendance) pour le script de la passe anti-filigrane. Sans terminal, cette passe se fait à la main. Le reste est un filtre de texte, au format standard des skills (lisible par Claude Code et par Codex CLI).

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

## Interdit absolu — ne rien fabriquer

Humaniser un texte, ce n'est jamais y ajouter de l'information fausse. Ne JAMAIS inventer un fait, un nom, une date, un chiffre, une étude ou une citation qui ne figure pas déjà dans le texte d'origine.

Quand une règle réclame plus de concret (un ancrage, une source) et que le texte n'en fournit pas : le signaler et demander la donnée réelle à l'auteur. Ne pas combler le vide avec une donnée plausible mais inventée. Un chiffre fabriqué est pire que son absence.

---

## Passe anti-filigrane — caractères invisibles

Un texte généré ou copié depuis le web peut porter des caractères qu'on ne voit pas : espaces sans chasse, marques de direction, espaces exotiques. Ils suivent le texte au copier-coller et un outil qui les cherche les trouve. C'est ce qu'on appelle un filigrane (« watermark »).

La passe se fait deux fois : sur le texte source avant la réécriture, puis sur le texte final pendant l'auto-audit.

**Avec un terminal**, lancer le script du dossier de ce skill. Un texte collé dans la conversation s'écrit d'abord dans un fichier temporaire.

```bash
python3 <dossier de ce skill>/scripts/invisibles.py texte.txt > texte-propre.txt
```

Le texte nettoyé sort dans `texte-propre.txt`, le fichier d'origine n'est pas touché. Le rapport s'affiche dans le terminal : chaque caractère retiré avec son code et son nombre, puis les tirets cadratins encore présents. Reporter ce qui a été retiré dans « Ce qui a été corrigé » (ex. « 3 espaces sans chasse (U+200B) retirées »). Sur le texte final, le rapport doit dire « Aucun caractère invisible. » et ne signaler aucun tiret cadratin.

**Sans terminal**, faire la passe à la main avec la liste ci-dessous, et l'écrire dans la sortie : « passe anti-filigrane faite à la main, non vérifiée par le script ».

Ce que fait le script :
- il retire les caractères sans largeur (U+200B à U+200D, U+2060, U+FEFF), le trait d'union conditionnel (U+00AD), les marques et commandes de direction (U+200E, U+200F, U+202A à U+202E, U+2066 à U+2069), les opérateurs mathématiques invisibles (U+2061 à U+2064), les sélecteurs de variante, les caractères d'étiquette (U+E0000 à U+E007F) et quelques remplissages invisibles (hangûl, braille vide) ;
- il remplace par une espace normale les espaces exotiques (U+2000 à U+200A, U+205F, U+3000), pour ne pas coller les mots ;
- il garde l'espace insécable (U+00A0) et l'espace fine insécable (U+202F), dont la typographie française se sert avant le deux-points, dans les guillemets « » et dans les nombres (10 000). Il garde aussi les liants collés à un émoji conservé (❤️, 👨‍💻), sinon l'émoji se casse en deux.

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

**Résidus de conversation IA** — « Bien sûr ! Voici… », « J'espère que cela vous aidera », « N'hésitez pas à me dire… », « En tant qu'IA… », « à la date de ma dernière mise à jour », « Souhaitez-vous que je… »... Les politesses et offres d'aide d'un assistant qui fuient au copier-coller. Supprimer entièrement : ne garder que le texte lui-même.

**Périphrases de remplissage** — afin de → pour, en raison du fait que → parce que, au niveau de → pour/dans, de manière à ce que → pour que, dans le cadre de (souvent supprimable). Lourdeurs administratives qui ont toutes une forme courte.

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

**Autorité fantôme** — « de nombreuses études montrent », « les experts s'accordent », « selon certains observateurs », « il est communément admis »... Appel à une autorité anonyme pour crédibiliser une affirmation sans jamais nommer de source. Deux issues : citer la source réelle si elle existe, sinon assumer l'affirmation en son nom propre. Ne jamais inventer la source.

**Liste à étiquette en gras** — le motif « **Terme** : description » répété en série (deux entrées ou plus) transforme le texte en fiche produit. Convertir en prose, ou en liste simple sans étiquette grasse.

**Empilement de modalisateurs** — « il se pourrait éventuellement que… peut-être », « pourrait potentiellement »... Plusieurs précautions de langage superposées dans une même phrase. Garder un seul modalisateur, ou aucun si l'affirmation est certaine.

**Sycophantisme** — ne pas présenter le sujet comme important juste parce que c'est le sujet. « Enjeu majeur pour l'avenir » → dire en quoi c'est un enjeu, concrètement.

### Injections positives (à ajouter si absentes)

**Connecteurs logiques** — viser au moins 1 connecteur pour 4 phrases. Le texte doit expliciter les relations logiques (car, donc, or, pourtant, en revanche...).

**Varier la longueur des phrases** — mélanger phrases longues et phrases courtes. Viser environ 40 % de phrases courtes (moins de 10 mots) et une majorité du reste à 15 mots ou plus. Alerte sous 15 % de phrases courtes.

**Ruptures de registre** — au moins une rupture de ton pour 400 mots. Question directe, formule orale, incise personnelle, phrase très courte après un développement dense.

**Ancrages concrets** — un texte sans date, lieu, nom propre ni chiffre sonne désincarné. S'il en manque (moins de 1 par section de 300 mots), le signaler et demander à l'auteur une donnée réelle. Ne jamais en inventer (voir l'interdit de fabrication plus haut).

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

## Passe finale d'auto-audit

Avant de livrer, relire une dernière fois le texte réécrit et se poser une seule question : reste-t-il un seul marqueur IA (un tiret cadratin oublié, une majuscule après deux-points, une transition morte, un résidu de conversation) ? Si oui, corriger avant de rendre. Puis repasser le texte final au script de la passe anti-filigrane. Cette relecture ne figure pas dans la sortie : seul le texte propre est livré.

---

## Barème

Partir de 100. Retirer des points pour chaque pattern détecté. Les occurrences multiples d'un même pattern s'additionnent jusqu'à 2x la pénalité de base.

| Catégorie | Pénalité par occurrence |
|---|---|
| Tiret cadratin (—) | -10 |
| Majuscule après deux-points | -8 |
| Caractère invisible (filigrane) | -5 |
| Expression interdite (tables de remplacement) | -5 |
| Pattern de contenu (gonflement, sycophantisme, fausse émotion...) | -8 |
| Pattern structurel (transitions mortes, ouvertures, listes...) | -5 |
| Conclusion passe-partout ou paragraphe creux | -10 |
| Résumé conclusif compulsif | -10 |

Le tiret cadratin est au niveau de pénalité maximal (-10) parce que c'est le marqueur le plus flagrant.

---

## Pour aller plus loin

Le fichier `references/tics-llm.json` contient les 44 règles complètes avec :
- Les listes exhaustives de mots et expressions à détecter
- Les exemples avant/après pour chaque règle
- Les seuils et paramètres (nombre max d'occurrences, scope...)
- Les exceptions à respecter

Consulter ce fichier quand une règle nécessite un jugement nuancé ou quand le texte à traiter est long et complexe.
