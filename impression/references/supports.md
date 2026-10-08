# Une fiche par support

Pour chaque support : ce qui compte pour celui qui le tient, ce qu'il faut demander à l'imprimeur et ce qu'il faut
contrôler. Les numéros entre crochets renvoient aux sources de notions.md. Ce qui n'a pas de source est une question,
pas une règle. Le jugement visuel (lisibilité, hiérarchie, envie) revient à /impeccable ; cette fiche lui donne le
cadre.

## Sommaire

1. Plateau de jeu
2. Cartes
3. Livret
4. Boîte
5. Dépliant
6. Affiche

## 1. Plateau de jeu

**Ce qui compte** : il se lit de loin, à plusieurs, sous des angles différents. Les joueurs sont autour de la table :
un texte n'est droit que pour une partie d'entre eux. Les cases, les chemins et les symboles doivent se distinguer à
un mètre, sans lire de mot.

**À demander à l'imprimeur** :
- le gabarit : format fini, nombre de plis et place des plis. Chez les trois fabricants cités, le plateau est un papier
  imprimé rabattu autour d'un carton, d'où un grand débord : 18 mm chez Panda [10], 20 mm chez LongPack [11], 22 mm
  pour l'habillage chez Efko [12] ;
- la distance à garder entre un élément important et un pli ;
- le dos du plateau : imprimé ou uni ? Efko le veut 5 mm plus petit que le plateau [12].

**À contrôler** :
- `verifier.py plateau.pdf --format … --debord … --surete …` ;
- une planche agrandie à 200 dpi au moins (`planche.py --zone X,Y,L,H --dpi 200`) : un trait fin, une cassure dans une
  courbe ou une jonction ratée ne se voient pas sur un aperçu entier ;
- un morceau imprimé à l'échelle 1 sur une imprimante de bureau, posé sur la table et regardé debout : c'est le seul
  vrai test de lecture à distance ;
- les traits fins blancs ou de plusieurs encres : 0,25 pt au moins en offset feuille [2], à confirmer.

**Exemple vécu** : un plateau de 20 × 16 po redessiné en vectoriel (bordures de 4,2 pt, séparations de 1,1 pt). Les
textes y sont en vraie police intégrée, donc vus par le contrôle de la marge de sécurité.

## 2. Cartes

**Ce qui compte** : tenues en main, lues de près, battues, glissées dans un paquet. Un recto différent par carte, un
verso commun par paquet.

**Formats** : « 63 × 88 mm » et « 2,5 × 3,5 po » ne sont pas le même format. 2,5 × 3,5 po font 63,5 × 88,9 mm : un
demi-millimètre de plus en largeur, presque un en hauteur. Demander le format exact à l'imprimeur avant de
dessiner, et le noter.

**À demander à l'imprimeur** :
- le format, le débord, la marge de sécurité et le rayon des coins arrondis ;
- comment il veut les fichiers : un PDF par face, ou recto puis verso de chaque carte, une page par exemplaire ou
  une page par carte différente avec un nombre d'exemplaires à part ;
- si le nombre de cartes est contraint par la feuille d'impression (cartes par planche) ;
- la tolérance de décalage entre recto et verso ;
- la finition (pelliculage, vernis, texture) et le papier.

**Le verso** : un cadre uniforme fait ressortir le moindre décalage de coupe. The Game Crafter le dit : « les
bordures exagèrent souvent le décalage qui peut se produire » [13]. Un verso sans cadre, avec un motif qui continue
dans le débord, pardonne mieux.

**Le texte** : lu à quelques dizaines de centimètres. Efko demande 6 pt au moins pour un texte d'une couleur, et des
traits de 0,1 mm au moins [12].

**À contrôler** :
- `verifier.py cartes.pdf --format … --debord … --surete … --polices …` : format de chaque page, débord,
  polices et chaque mot trop près de la coupe ;
- une planche coupe et débord (`planche.py cartes.pdf --vue coupe,debord`) ;
- après chaque changement, `verifier.py nouveau.pdf --comparer ancien.pdf` puis une planche avant/après des
  cartes touchées ;
- recto et verso ensemble sur une planche, pour voir le paquet comme le joueur le verra.

## 3. Livret

**Ce qui compte** : on le lit, posé ou tenu, parfois en pleine partie pour trancher un doute. Le texte doit être
confortable, et chaque règle facile à retrouver.

**Le nombre de pages** : un livret agrafé au pli est fait de feuilles pliées en deux, soit 4 pages par feuille, donc
un total multiple de 4. Prévoir les pages blanches. À vérifier auprès de l'imprimeur pour toute autre reliure.

**À demander à l'imprimeur** :
- la reliure (agrafes, dos carré collé…) et la marge intérieure qu'elle demande ;
- le débord, si la couverture ou une page a un fond qui touche le bord ;
- le papier de la couverture et celui de l'intérieur ; intérieur en noir seul ou en couleurs ;
- le noir du texte : comment il convertit le noir RVB, en noir pur (encre noire seule) ou en noir composé des quatre
  encres. Panda demande le texte en noir pur [10], Efko aussi (100 % de noir) [12].

**Avec Chrome** : `fabriquer.py livret.html livret.pdf --format … --debord … --flux`. Chrome répartit le texte sur les
pages ; les marges se règlent avec `@page{margin:…}`, débord compris, et la couverture avec `@page:first{margin:0}`.
Les numéros de page : `@page{@bottom-center{content:counter(page)}}`. Pas de gras sans le vrai fichier gras de la
police (chrome-pdf.md, piège 6).

**À contrôler** : `verifier.py livret.pdf --format … --debord … --surete …`, le nombre de pages et une relecture sur
papier.

## 4. Boîte

**Ce qui compte** : donner envie, en rayon ou en photo. C'est le terrain de /impeccable. La technique, elle, se
résume à suivre le gabarit du fabricant.

**À demander à l'imprimeur** :
- **le gabarit de découpe**, toujours. Panda fournit un générateur de gabarits « pour avoir les bonnes lignes de
  découpe, le bon débord et les bonnes marges » [10] ; Efko envoie ses gabarits sur demande [12] ;
- le débord de rabat : chez ces fabricants, la boîte est un carton habillé d'un papier rabattu à l'intérieur.
  18 mm chez Panda et Efko, 20 mm chez LongPack [10] [11] [12] ;
- la marge à garder près des plis et des coupes : 3 mm chez Efko [12] ;
- comment livrer les lignes de découpe : Panda les veut hors de l'illustration [10], Efko dans un calque à part,
  masqué à l'export [12] ;
- les mentions à faire figurer (âge, avertissements, code-barres) : selon le pays de vente, à vérifier.

**Avec Chrome** : la boîte se dessine à plat sur le gabarit, comme une affiche du format du gabarit. Placer le gabarit
en fond pour travailler, et le retirer avant l'export si l'imprimeur ne le veut pas dans l'illustration.

**À contrôler** : la planche avec le gabarit par-dessus, chaque face lue dans le bon sens une fois pliée et une
maquette papier découpée et pliée.

## 5. Dépliant

**Ce qui compte** : il se déplie dans un ordre. L'ordre des volets à plat, recto puis verso, n'est pas l'ordre de
lecture.

**À demander à l'imprimeur** :
- le type de pli (roulé, accordéon, fenêtre) et la largeur exacte de chaque volet : sont-ils tous égaux ?
- la place exacte des plis et la marge à garder de part et d'autre ;
- le rainage pour un papier épais.

**À contrôler** : une maquette papier, imprimée recto verso, pliée, avant tout envoi. C'est elle qui dit si les volets
sont dans le bon ordre et dans le bon sens.

## 6. Affiche

**Ce qui compte** : lue de loin, en passant. Peu de mots, très grands.

**Chiffres GWG2022 pour le grand format** [5] : texte blanc ou de plusieurs encres de 5 pt au moins, traits de 0,15 pt
au moins, images en erreur à 239 ppi et en avertissement à 299 ppi (à leur taille imprimée). À confirmer avec
l'imprimeur.

**À demander à l'imprimeur** : le procédé (offset ou numérique grand format), le papier, le débord, le fichier à
l'échelle 1 ou réduite.

**Avec Chrome** : un format de 20 × 16 po s'imprime sans difficulté ; un format A0 ou plus n'a pas été essayé.

**À contrôler** : `verifier.py affiche.pdf --format … --debord … --resolution …` et un morceau imprimé à l'échelle 1.
