---
name: Panneau d'audit
description: Sélection des projets scannés par /audit-secu, sous la forme d'un tableau électrique
colors:
  fond: "#d3d0c7"
  plaque: "#e5e2da"
  arete: "#b4b0a5"
  encre: "#1c1e21"
  encre-2: "#4c4f54"
  module: "#222529"
  levier: "#474c53"
  moule: "#9ca2a9"
  epine: "#8f9399"
  ruban: "#f6f5f1"
  ruban-encre: "#141516"
  cadenas: "#e3540a"
  cadenas-encre: "#141516"
  focus: "#1c1e21"
typography:
  display:
    fontFamily: "Barlow Condensed, Arial Narrow, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "0.01em"
  headline:
    fontFamily: "Barlow Condensed, Arial Narrow, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.02rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "0.02em"
  title:
    fontFamily: "Barlow Condensed, Arial Narrow, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 700
    lineHeight: 1.2
    fontFeature: "tnum"
  numero:
    fontFamily: "Barlow Condensed, Arial Narrow, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 600
    lineHeight: 1
    fontFeature: "tnum"
  body:
    fontFamily: "Barlow, Helvetica Neue, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Barlow Condensed, Arial Narrow, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.05em"
  moule:
    fontFamily: "Barlow Condensed, Arial Narrow, Helvetica Neue, Arial, sans-serif"
    fontSize: "10px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.06em"
rounded:
  ruban: "1px"
  vis: "2px"
  module: "3px"
  plaque: "4px"
  queue: "12px"
spacing:
  xs: "4px"
  sm: "6px"
  md: "8px"
  lg: "12px"
  xl: "16px"
components:
  disjoncteur:
    backgroundColor: "{colors.module}"
    rounded: "{rounded.module}"
    width: "58px"
    height: "38px"
  ruban:
    backgroundColor: "{colors.ruban}"
    textColor: "{colors.ruban-encre}"
    typography: "{typography.headline}"
    rounded: "{rounded.ruban}"
    padding: "5px 9px 4px"
  ruban-nouveau:
    backgroundColor: "{colors.module}"
    textColor: "{colors.ruban}"
    rounded: "{rounded.ruban}"
    padding: "5px 7px 4px"
  filtre:
    backgroundColor: "{colors.plaque}"
    textColor: "{colors.encre-2}"
    typography: "{typography.label}"
    padding: "11px 12px"
  filtre-actif:
    backgroundColor: "{colors.module}"
    textColor: "{colors.ruban}"
  recherche:
    backgroundColor: "{colors.plaque}"
    textColor: "{colors.encre}"
    rounded: "{rounded.module}"
    padding: "10px 12px"
  cadenas:
    backgroundColor: "{colors.cadenas}"
    textColor: "{colors.cadenas-encre}"
    rounded: "{rounded.module}"
    padding: "7px 10px 8px 8px"
  raison:
    textColor: "{colors.cadenas-encre}"
    rounded: "{rounded.vis}"
    padding: "8px 8px 7px"
  raison-active:
    backgroundColor: "{colors.cadenas-encre}"
    textColor: "{colors.cadenas}"
  barre-etat-mobile:
    backgroundColor: "{colors.module}"
    textColor: "{colors.ruban}"
    padding: "11px 16px"
---

# Design System: Panneau d'audit

## Overview

**Creative North Star: "Le tableau électrique"**

La sélection des projets est un panneau électrique. Chaque projet est un circuit qui a son disjoncteur, et l'audit n'alimente que les circuits sous tension. La page est faite des matériaux d'un vrai panneau : tôle émaillée gris chaud (graphite la nuit), plaque de façade un ton plus claire, épine centrale en acier avec ses rivets, disjoncteurs en thermoplastique noir avec ON et OFF moulés, étiquettes en ruban blanc. Une seule couleur dans tout le système : l'orange sécurité de l'étiquette de cadenassage.

La densité est celle d'un outil de travail : environ 80 circuits doivent se parcourir et se basculer en moins d'une minute, au pouce comme à la souris. Pas de cartes, pas d'illustration, pas de rangées identiques avec interrupteur générique. Le relief reste physique et court : un objet posé sur la tôle projette une ombre d'un ou deux pixels, rien de plus.

Le mouvement est mécanique : le levier claque en 160 ms avec un léger dépassement, et l'étiquette orange pivote depuis son œillet en se posant. Avec le mouvement réduit, rien ne bouge.

**Key Characteristics:**
- Un circuit = un disjoncteur, un numéro tabulaire et un ruban étiqueté.
- Épine centrale : impairs à gauche, pairs à droite sur grand écran ; une colonne avec l'épine à gauche au téléphone.
- Le levier pointe vers l'épine quand le circuit est sous tension.
- L'orange n'existe que sur l'étiquette « Hors audit ».
- Tout le texte est en Barlow Condensed, sauf le texte courant en Barlow.

## Colors

Une palette de matériaux industriels neutres, gris chaud le jour et graphite la nuit, percée d'un seul orange de signalisation.

### Primary
- **Orange de cadenassage** (cadenas) : le fond de l'étiquette « Hors audit » qui pend sous un circuit coupé, et rien d'autre. Version nuit un peu plus lumineuse (#f06a1f) pour rester lisible sur graphite. Encre noire dessus (cadenas-encre, contraste 4,8:1 le jour, 5,9:1 la nuit).

### Neutral
- **Tôle émaillée** (fond) : le fond de page et de la porte collante. Nuit : #1a1a19.
- **Plaque de façade** (plaque) : la plaque qui porte les circuits, le champ de recherche, les filtres au repos. Nuit : #262523.
- **Arête de tôle** (arete) : les filets d'un pixel (bas de la porte, contour de la plaque, séparations des filtres). Nuit : #3b3a37.
- **Encre de sérigraphie** (encre) : titres, valeurs du relevé, texte principal. Nuit : #e8e6e0.
- **Encre secondaire** (encre-2) : numéros de circuit, intitulés du relevé, filtres au repos, notes de bas de page (5,3:1 sur la tôle). Nuit : #b0ada6.
- **Thermoplastique noir** (module) : le corps des disjoncteurs, le filtre actif, le ruban « Nouveau », la barre d'état du téléphone. Nuit : #0f0f0e.
- **Levier** (levier) : la manette du disjoncteur, en dégradé vertical vers 20 % de blanc. Nuit : #575653.
- **Moulage** (moule) : les lettres ON et OFF au repos ; la lettre de l'état actif passe en ruban. Nuit : #8f8d88.
- **Acier de l'épine** (epine) : la barre verticale centrale. Nuit : #64625e.
- **Ruban d'étiqueteuse** (ruban) et **encre du ruban** (ruban-encre) : les noms de projets. Nuit : ruban #e2e0d8, encre inchangée.

### Named Rules
**La règle de l'orange unique.** L'orange sécurité est réservé à l'étiquette de cadenassage d'un circuit hors audit. Ni le compteur « Hors audit », ni les erreurs, ni le survol, ni le focus ne le prennent : le compteur se souligne à l'encre, l'erreur s'inverse en noir et blanc.

**La règle de l'erreur en encre.** Un état d'erreur se signale par inversion ou par une pastille de l'encre courante, jamais par une couleur ajoutée.

## Typography

**Display Font:** Barlow Condensed (avec Arial Narrow, Helvetica Neue, Arial)
**Body Font:** Barlow (avec Helvetica Neue, Arial)

**Character:** Les lettres condensées d'une étiqueteuse et d'une plaque sérigraphiée, serrées et lisibles ; Barlow droite pour les phrases.

### Hierarchy
- **Display** (700, 1,75rem, 1,05, capitales) : le nom du panneau dans la porte, seul titre de la page.
- **Headline** (600, 1,02rem, 1,15) : le nom du projet sur son ruban. Coupe n'importe où plutôt que de déborder.
- **Title** (700, 1,15rem, chiffres tabulaires) : les valeurs du relevé des compteurs.
- **Numéro** (600, 0,95rem, chiffres tabulaires) : le numéro de circuit, en encre secondaire.
- **Body** (400, 15px, 1,45) : texte courant, messages du panneau, note de bas de page (70ch au plus).
- **Label** (600, 0,85rem, 0,05em, capitales) : filtres. Variantes du même rôle : intitulés du relevé (0,8rem, 0,06em, capitales), « HORS AUDIT » (700, 0,9rem, 0,1em), ruban « NOUVEAU » (700, 0,72rem, 0,12em), boutons de raison (600, 0,85rem, 0,03em, casse normale).
- **Moulage** (700, 10px, 0,06em) : ON et OFF moulés dans le disjoncteur.

### Named Rules
**La règle des chiffres de compteur.** Tout nombre affiché (numéros de circuit, relevé) est en chiffres tabulaires, pour que les colonnes ne dansent pas.

**La règle du ruban.** Un nom de projet ne s'écrit jamais en texte nu : il est toujours imprimé sur un ruban.

## Layout

Une colonne centrée de 1080px au plus, marges latérales de 16px au minimum (zones sûres respectées). En haut, la porte du panneau : titre et ligne d'inventaire, relevé des compteurs, recherche et groupe de quatre filtres, état d'enregistrement. Elle colle en haut de l'écran à partir de 760px. Dessous, la plaque.

Sur la plaque, une grille de circuits espacés de 6px verticalement. À partir de 760px : deux colonnes de part et d'autre d'une épine de 10px centrée, circuits impairs à gauche en miroir (ruban, numéro, disjoncteur), pairs à droite (disjoncteur, numéro, ruban). En dessous de 760px : une seule colonne, épine à gauche, numéros alignés à gauche, et l'état d'enregistrement devient une barre noire fixée en bas de l'écran.

Rythme : 4, 6, 8, 12 et 16px reviennent partout ; quelques valeurs de calage optique (5, 7, 9, 11px) servent au centrage des rubans et des boutons.

## Elevation & Depth

Relief physique, court et cohérent avec une seule lumière venant d'en haut. La plaque se détache de la tôle par une ombre de 1 à 2px ; le disjoncteur a un reflet d'arête en haut et une ombre portée de 1 à 2px ; le levier et le ruban, une ombre de 1px. Les rivets de l'épine sont des creux (ombre intérieure). L'étiquette orange n'a pas d'ombre : elle pend à plat.

### Shadow Vocabulary
- **Plaque posée** (`box-shadow: 0 1px 2px rgb(0 0 0 / 0.14)`) : la plaque de façade.
- **Module moulé** (`box-shadow: inset 0 1px 0 rgb(255 255 255 / 0.08), 0 1px 2px rgb(0 0 0 / 0.35)`) : le corps du disjoncteur.
- **Levier** (`box-shadow: 0 1px 1px rgb(0 0 0 / 0.5)`) : la manette.
- **Ruban collé** (`box-shadow: 0 1px 1px rgb(0 0 0 / 0.18)`) : l'étiquette de nom.
- **Rivet** (`box-shadow: inset 0 1px 0 rgb(0 0 0 / 0.3)`) : le point de 4px sur l'épine en face de chaque circuit.

### Named Rules
**La règle du relief de matière.** Une ombre ne sert qu'à dire qu'un objet est posé ou moulé : 2px de flou au plus, jamais de halo, jamais de décalage dur.

## Shapes

Des coins presque droits, comme de la tôle découpée et du plastique moulé : 1px pour les rubans, 2px pour l'épine et les boutons de raison, 3px pour les disjoncteurs, les champs et les filtres, 4px pour la plaque. Une seule forme marquée : l'étiquette de cadenassage a un coin de 12px côté opposé à l'œillet, comme une étiquette pendue (en bas à gauche à droite de l'épine, en bas à droite à gauche de l'épine). Filets d'un pixel en arête de tôle ; le groupe de filtres est un seul bloc découpé, séparé par des filets.

## Components

### Disjoncteur
Thermoplastique noir, mécanique et franc. C'est l'action principale de chaque circuit.
- **Forme :** 58 × 38px, coins de 3px, fente sombre au centre où glisse un levier de 18 × 16px.
- **États :** le levier pointe vers l'épine quand le circuit est sous tension (à droite de l'épine il est à gauche ; à gauche de l'épine il est à droite). La lettre moulée de l'état actif passe en ruban, l'autre reste en moulage.
- **Mouvement :** le levier glisse de 18px en 160 ms (`cubic-bezier(.3, 1.45, .55, 1)`), un claquement avec léger dépassement. Survol : levier éclairci de 15 %. Désactivé (lecture seule) : 60 % d'opacité.
- **Accessibilité :** interrupteur à deux états nommé « Scanner [projet] » ; ON et OFF sont masqués aux lecteurs d'écran.

### Ruban
- **Style :** ruban blanc, encre noire, coins de 1px, ombre de 1px. Circuit hors audit : ruban à 62 % d'opacité.
- **Nouveau :** ruban inversé noir, lettres ruban espacées, posé à côté du nom.

### Étiquette de cadenassage
- **Style :** orange, encre noire, œillet de 12px percé (couleur de la plaque, anneau d'encre à 30 %), « HORS AUDIT » espacé puis « Raison, si tu veux : ».
- **Raisons :** quatre boutons contour d'encre de 1,5px, coins de 2px ; survol à 12 % d'encre ; choisi = encre pleine, texte orange. Un second appui retire la raison.
- **Mouvement :** à la pose, elle pivote de 7° autour de son œillet jusqu'à l'horizontale en 200 ms (`cubic-bezier(.2, .9, .25, 1)`), sens inversé à gauche de l'épine. Mouvement réduit : aucune rotation.

### Filtres
- **Style :** groupe d'un seul tenant, contour en encre secondaire (5,3:1 sur la tôle), coins de 3px ; boutons plaque en capitales condensées, encre secondaire.
- **États :** survol à l'encre ; actif en thermoplastique noir, texte ruban.

### Recherche
- **Style :** plaque, contour de 1px en encre secondaire (5,3:1 sur la tôle), coins de 3px, Barlow 500 à 1rem ; texte indicatif en encre secondaire.

### Relevé et état d'enregistrement
- **Relevé :** intitulés en capitales secondaires, valeurs en chiffres tabulaires gras ; la valeur « Hors audit » est soulignée d'un trait d'encre de 3px.
- **État :** ligne discrète en encre secondaire dans la porte ; au téléphone, barre noire fixée en bas. Erreur : pastille d'encre de 8px sur grand écran, barre inversée en ruban au téléphone.

### Focus
Contour de 2px en encre (focus), décalé de 2px ; sur l'étiquette orange, contour en encre du cadenas.

## Do's and Don'ts

### Do:
- **Do** faire pointer le levier vers l'épine pour « sous tension », en miroir de chaque côté.
- **Do** garder l'orange (cadenas) pour la seule étiquette « Hors audit ».
- **Do** imprimer chaque nom de projet sur un ruban, et chaque nombre en chiffres tabulaires.
- **Do** garder ON et OFF moulés sur le disjoncteur : ce sont des marques du matériel, masquées aux lecteurs d'écran ; tout texte à lire reste en français.
- **Do** couper le claquement du levier et la pose de l'étiquette quand le mouvement réduit est demandé.

### Don't:
- **Don't** remplacer le disjoncteur par un interrupteur générique en pilule, ni aligner des rangées identiques de réglages.
- **Don't** colorer une erreur, un compteur ou un survol en orange ou en rouge.
- **Don't** utiliser d'ombre de plus de 2px de flou, de halo ni de décalage dur.
- **Don't** arrondir au-delà de 4px, sauf le coin de queue de 12px de l'étiquette pendue.
