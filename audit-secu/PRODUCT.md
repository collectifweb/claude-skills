# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack
Page artefact claude.ai : un seul fichier HTML (CSS et JS en ligne), données dans la capacité `db`
de la page. Imposé par le support, pas un choix ouvert.

## Users
Un seul utilisateur : le développeur qui lance `/audit-secu` sur son dossier de travail (environ
80 projets clients et internes). Il ouvre la page juste avant un passage d'audit, souvent depuis
son téléphone, pour dire quels projets scanner.

## Product Purpose
Choisir les projets inclus dans l'audit de sécurité. Certains projets sont vivants mais sans
mandat de sécurité, d'autres abandonnés ou suspendus sans être à la corbeille : ils ne doivent pas
être scannés ni apparaître dans le rapport. Réussite : la sélection se fait en moins d'une minute
et le skill la lit sans erreur.

## Operating Context
- Le skill écrit la liste des projets dans la base de la page avant chaque passage, puis lit les
  choix et attend le feu vert.
- Un projet apparu depuis le dernier passage arrive coché et marqué « nouveau ».
- Décocher un projet peut s'accompagner d'une raison, facultative : abandonné, pas de mandat,
  autre développeur, suspendu.

## Capabilities and Constraints
- Rien de confidentiel dans la page elle-même : les noms de projets vivent dans la base, jamais
  dans le code source (dépôt public).
- La page ne lance aucun scan : elle enregistre une sélection.

## Brand Commitments
Interface en français, sans anglicismes ; le nom de l'agence s'écrit « Collectif WEB ».

## Product Principles
- Tout est coché par défaut : un projet ne sort du scan que par une décision explicite.
- La raison d'une exclusion est visible d'un coup d'œil, pour qu'elle se remette en question.
- Rapide au pouce : la page se manipule au téléphone autant qu'à l'écran.
