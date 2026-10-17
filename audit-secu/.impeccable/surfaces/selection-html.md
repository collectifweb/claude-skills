---
version: 1
slug: "selection-html"
primary_target: "selection.html"
related_targets: []
---

# Panneau d'audit (page de sélection des projets)

Mode : Operate. Un seul utilisateur, souvent au téléphone, juste avant un passage d'audit.
Tâche : décider quels projets sont scannés ; donner, si besoin, la raison d'une exclusion.
Données : collection `projets` (nom, scanner, raison, nouveau) et document `meta/panneau` dans la
capacité `db`, écrits par le skill. Rien de confidentiel dans le code de la page.
Construction : code d'abord (aucun générateur d'images sur ce poste).

## Direction contract

THESIS: La sélection est un panneau électrique : chaque projet est un circuit avec son disjoncteur,
et l'audit n'alimente que les circuits sous tension. Refuse la liste de réglages faite de rangées
identiques à interrupteur.

OWN-WORLD: Tôle émaillée gris chaud (graphite la nuit), plaque de façade un ton plus claire, épine
centrale en acier rivetée. Disjoncteurs en thermoplastique noir, ON/OFF moulés, levier qui pointe
vers l'épine quand il est sous tension. Étiquettes en ruban blanc, lettres condensées noires,
numéros de circuit en chiffres tabulaires. Une seule couleur : l'orange sécurité, réservé à
l'étiquette de cadenassage d'un circuit hors audit. « Nouveau » : ruban inversé, noir.
Barlow et Barlow Condensed.

STORY: Il ouvre, lit « 78 sous tension · 2 hors audit », parcourt l'annuaire, coupe un circuit,
accroche l'étiquette avec la raison, referme. Le skill lit le panneau et attend le feu vert.

FIRST VIEWPORT: En haut, la porte du panneau : nom, relevé des compteurs, recherche et quatre
filtres (Tous, Sous tension, Hors audit, Nouveaux), état d'enregistrement. Juste dessous, le
panneau commence : circuits impairs à gauche, pairs à droite de l'épine sur grand écran, une colonne
avec l'épine à gauche au téléphone. L'action principale est le levier de chaque disjoncteur.

FORM: Tableau électrique, candidat 1 de ma liste (pick), seed 7e37dd9d. Interaction signature : le
levier claque (160 ms) et l'étiquette orange pivote depuis son œillet en se posant ; sans
mouvement réduit, rien ne pivote.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
