---
name: roast
description: >
  Utiliser quand quelqu'un veut faire démolir une idée, un projet ou un livrable, le
  stress-tester avant ou après l'avoir construit, valider une idée business, réunir le jury,
  obtenir un deuxième avis brutal, roaster un site ou une maquette, ou tape /roast. Compose
  un jury de personas adapté à ce qu'on juge, les lance en parallèle pour attaquer sous tous
  les angles, puis un Juge rend un seul verdict FONCE / AJUSTE / LAISSE TOMBER avec la
  première chose à faire pour le dé-risquer.
---

# Roast — le jury qui teste ton idée à mort

Par défaut, l'assistant te donne raison. `/roast` fait l'inverse. Il compose un jury de personas qui déchirent et reconstruisent le sujet sous tous les angles, puis un Juge synthétise le tout en un seul verdict honnête. À utiliser avant de couler du temps et de l'argent dans la mauvaise chose, ou pour juger sans complaisance quelque chose qui existe déjà.

La force du roast tient à une seule chose : la friction. Un jury poli ne sert à rien. Le casting change selon ce qu'on juge, mais trois garanties ne bougent JAMAIS, sinon ce n'est plus un roast.

## Commande rapide

`/roast` suivi du sujet. Sans argument, on te demande le brief.

## L'ADN : les 3 garanties

Quel que soit le casting, le jury contient toujours :

1. **Un démolisseur frontal** — un persona dont le seul job est de le casser. Pas de « mais ça pourrait marcher ». Sans lui, tout le monde est gentil.
2. **Une voix extérieure réelle** — pas une abstraction interne : le vrai utilisateur, le vrai client, le vrai marché selon le sujet. C'est elle qui ramène le monde réel dans la salle.
3. **Un juge qui tranche** — une décision, pas une moyenne des notes.

Quand tu proposes un casting (étape 1c), vérifie que ces trois-là sont couverts avant de lancer.

## Étape 1 — Cadrer

### a. La famille du roast

Identifie à quoi on a affaire. C'est ça qui détermine le jury :

- **Idée / offre** — un service, une fonctionnalité, un modèle d'affaires à lancer.
- **Projet en conception** — on va *construire* quelque chose (site, application, refonte).
- **Artefact fini** — un livrable qui existe déjà et qu'on juge (site en ligne, maquette, document, campagne).
- **Autre** — rien ne colle : compose un casting sur mesure qui respecte quand même les 3 garanties.

### b. Le brief

Pose une série serrée de questions pour que le jury ait du vrai contexte. Ne demande que ce qui manque, et adapte à la famille (pour un site fini, ne demande pas de prix de vente). Maximum 3-4 questions, en un seul bloc. Selon le cas :

1. **Le sujet** en une ou deux phrases.
2. **Pour qui** c'est, et **ce que ça vise** : l'acheteur et le prix pour une offre ; qui s'en sert et ce que ça lui fait gagner pour un projet ou un livrable.
3. **Le contexte** : ton avantage, ce qui existe déjà, les contraintes (budget, échéance, pile technique imposée).

Si l'utilisateur dit « lance-le » ou en a déjà donné assez, saute les questions. Un tour, pas plus.

Écris le brief dans un seul court paragraphe que tu colleras à l'identique dans chaque membre du jury, pour que tous jugent exactement la même chose.

### c. Proposer le casting

Propose **5 personas nommés** (ajustable 4 à 6), tirés de la famille, chacun en français clair qu'on peut visualiser. Montre-les en une ligne chacun, puis demande : *« On part là-dessus, ou tu ajustes ? »*. L'utilisateur valide ou remplace en une ligne. Castings types :

**Idée / offre**
- **L'avocat du diable** — suppose que ça échoue, traque les failles fatales *(démolisseur)*.
- **Le visionnaire** — la version 10x, le vrai potentiel, les leviers cachés.
- **Le cartésien** — sans web : le mécanisme tient-il, les chiffres tiennent-ils en théorie.
- **L'enquêteur** — avec web : concurrents, prix pratiqués, signaux de demande *(voix réelle : le marché)*.
- **Le client** — le client cible, à la première personne : je paierais ou pas, et pourquoi.

**Projet en conception**
- **Le dev front** — faisabilité d'intégration, complexité, dette qu'on se crée.
- **Le dev back / intégration** — données, API, sécurité, ce qui casse en production *(démolisseur technique)*.
- **Le designer UX** — parcours, clarté, est-ce que ça sert vraiment la personne.
- **Le designer UI** — hiérarchie visuelle, cohérence, qualité perçue.
- **L'utilisateur qui s'en servira** — à la première personne, celui pour qui on construit *(voix réelle)*. Remplaçable par « celui qui va le maintenir dans un an » si le projet est surtout technique.

**Artefact fini**
- **Le visiteur pressé (mobile)** — arrive, ne comprend pas en 5 secondes, repart *(démolisseur)*.
- **Le client potentiel sceptique** — pourquoi te faire confiance, qu'est-ce qui me retient.
- **L'œil technique** — performance, accessibilité, référencement, ce qui est cassé.
- **L'utilisateur cible précis** — la personne réelle de l'audience (peu à l'aise avec le web, pressée, exigeante…) *(voix réelle)*.
- **Le proprio qui paie** — défend le livrable, dit ce dont il est fier et ce qu'il ne lâchera pas.

### d. Si c'est visuel

Pour un site, une maquette, un visuel : le jury doit VOIR, pas lire une description, sinon il hallucine. Récupère une URL ou une capture. Si tu as une URL et un navigateur sur la machine, prends toi-même une capture (pleine hauteur de préférence) et note son chemin. Sinon, demande la capture à l'utilisateur.

## Étape 2 — Réunir le jury (en parallèle)

Lance **tous les personas en parallèle, en une seule fois** (un sous-agent chacun ; dans Claude Code, `subagent_type: general-purpose`). Remplis ce gabarit de mandat pour chacun :

> Tu es **[NOM DU PERSONA]** dans un roast. Ton angle : **[l'angle du persona]**. Reste à 100 % dans ce rôle, aucune nuance polie, aucune politesse de façade. [Si visuel : **Ouvre la capture au chemin `[CHEMIN]` avec ton outil de lecture de fichier et juge ce que tu VOIS**, pas ce qu'on t'en dit.] Rends : ta position en une ligne, tes 3 à 5 points les plus tranchants, la seule chose que [NOM] doit absolument faire entendre, et une note sur 10 sur ta dimension (1 = passe ton chemin, 10 = évidence). LE SUJET : [brief]

Le démolisseur reste impitoyable. La voix extérieure parle à la première personne. L'enquêteur, s'il n'a pas accès au web, le dit et marque comme telle toute affirmation tirée de sa seule mémoire.

## Étape 3 — Le Juge rend le verdict

Une fois les réponses revenues, TOI tu joues le Juge. Lis chaque membre, pèse, et tranche. Ne fais pas la moyenne des notes : nomme la vraie tension entre les personas et résous-la.

Intègre toi-même la **lecture coût / impact** : pour une offre, prix approximatif et délai avant le premier dollar ; pour un projet ou un livrable, le coût en temps ou en budget face au gain attendu.

Rends le verdict exactement dans cette forme :

```
## LE VERDICT : FONCE / AJUSTE / LAISSE TOMBER
Confiance : [faible / moyenne / élevée]

**La décision en une ligne :** [la décision, franchement]

**Pourquoi :** [2-3 phrases qui tranchent la tension du jury]

**Le plus gros risque :** [la seule chose la plus susceptible de le tuer]
**Le plus gros potentiel :** [la meilleure raison de foncer]

**Lecture coût / impact :** [prix et premier dollar pour une offre ; temps ou budget vs gain pour un projet ou un livrable]

**Par où commencer :** [pour une idée : le test le moins cher en 48 h qui valide
l'hypothèse la plus risquée AVANT de construire. Pour un artefact fini : le correctif
le plus rentable à faire en premier.]

**Si AJUSTE :** [le changement précis qui règle la faille sans perdre le potentiel]
```

Ensuite, aligne les notes du jury sur une ligne, avec les vrais noms du casting du jour : `[Persona 1] X/10 · [Persona 2] X/10 · …`.

## Règles

- Les 3 garanties priment sur tout. Un casting qui n'a pas de démolisseur, pas de voix extérieure réelle, ou pas de juge qui tranche, n'est pas un roast : corrige-le avant de lancer.
- Chaque persona reste dans son rôle. Aucun ne nuance ni n'adoucit. La valeur est dans la friction.
- Le Juge doit trancher pour vrai. « Ça dépend » n'est pas un verdict. Choisis FONCE, AJUSTE ou LAISSE TOMBER, et assume.
- « Par où commencer » est la sortie la plus importante : c'est l'action concrète qui fait avancer sans tout reconstruire.
- Garde le verdict final survolable. Le jury fait la profondeur, le Juge fait la décision.
