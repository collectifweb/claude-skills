# Pièges du passage page web → PDF par Chrome

Faire imprimer une page HTML par Chrome est pratique : mise en page en CSS, polices web, SVG. Mais Chrome est fait
pour l'écran et l'imprimante de bureau, pas pour l'imprimerie. Les pièges ci-dessous ont été rencontrés sur un projet
réel (un jeu de cartes, son plateau et son livret), puis **reproduits un par un le 8 octobre 2026 avec Chrome for
Testing 151.0.7922.34**, dans de petits tests isolés. Une autre version de Chrome peut se comporter autrement :
refaire le contrôle indiqué à chaque piège.

`scripts/fabriquer.py` applique les parades des pièges 1 à 3 et 8. `scripts/verifier.py` détecte les pièges 1, 4,
5, 6 et 7.

## La commande

```bash
chrome --headless --disable-gpu --no-pdf-header-footer --allow-file-access-from-files \
       --virtual-time-budget=5000 --print-to-pdf=sortie.pdf file:///chemin/absolu/page.html
```

- `--allow-file-access-from-files` laisse la page charger ses polices et ses images locales.
- `--virtual-time-budget=5000` laisse du temps au chargement. Dans les tests, une police locale s'est chargée même
  sans cette option : elle est gardée par précaution.
- Le Chrome de Playwright se trouve dans `~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome`. Playwright est
  une bibliothèque, pas une commande : `command -v chromium` ne le trouve pas.

## 1. Le format de page est arrondi

**Symptôme** : le PDF n'a pas le format demandé par `@page{size:…}`, quelle que soit l'unité.

| Demandé | Obtenu | Écart |
|---|---|---|
| 63 × 88 mm (178,58 × 249,45 pt) | 179,04 × 249,12 pt | +0,16 mm et −0,12 mm |
| 69 × 94 mm | 196,08 × 265,92 pt | +0,17 mm et −0,19 mm |
| 148 × 210 mm (A5) | 420 × 594,96 pt, soit 148,17 × 209,89 mm | +0,17 mm et −0,11 mm |
| 20 × 16 po | 1440 × 1152 pt | exact |

**Contrôle** : `verifier.py fichier.pdf --format 63x88mm` signale tout écart de plus de 0,02 mm.

**Parade** : imprimer sur une page plus grande, puis recadrer au point près avec pypdf, à partir du coin haut gauche,
en déclarant la zone de coupe (TrimBox) et la zone de débord (BleedBox). C'est ce que fait `fabriquer.py`. En mode
flux (texte réparti par Chrome, livret), la page ne peut pas être plus grande : le recadrage remet le format exact,
et l'arrondi laisse un liseré blanc d'environ 0,1 mm au bas de la page, dans le débord, donc retiré à la coupe.

## 2. Chaque boîte est calée sur un pixel entier

**Symptôme** : un élément placé à 3 mm du bord se retrouve à 2,91 mm. Chrome cale le bord de toute boîte (bloc, image,
SVG dans la page) sur un pixel CSS entier, soit 1 px = 0,75 pt = 0,265 mm.

| Position demandée | En pixels | Position obtenue |
|---|---|---|
| 3 mm | 11,34 px | 2,91 mm (11 px) |
| 3,1 mm | 11,72 px | 3,17 mm (12 px) |
| 12 px | 12 px | 3,18 mm |

L'erreur va jusqu'à un demi-pixel, 0,13 mm. Elle touche aussi le bord droit et le bas d'une boîte : un fond dimensionné
au format fini exact s'est arrêté à 0,03 mm avant la coupe à droite, et 0,11 mm après en bas.

**Contrôle** : rendre la page très agrandie (`pdftoppm -r 2540`, soit 100 px par mm) et mesurer le bord.

**Parade** :
- placer les bords qui comptent à un nombre entier de pixels. `fabriquer.py` pose le format fini à un nombre entier de
  pixels du bord de la page, puis le recadrage retire le surplus ;
- tout fond qui touche la coupe continue dans le débord : il ne doit jamais s'arrêter pile au bord du format fini ;
- un fond qui doit couvrir toute la page la dépasse de quelques pixels. Sinon l'arrondi laisse un filet blanc au bord.

## 3. Un texte centré par translateY est coupé quand une page suit

**Symptôme** : une carte perd ses dernières lignes dans le PDF de toutes les cartes, alors qu'imprimée seule, elle est
complète. Le texte était centré par `top:…; transform:translateY(-50%)`. Avant ce décalage, son bas dépassait de la
page, même si le texte décalé y tenait entièrement. Chrome coupe ce qui dépasse, mais seulement quand une autre page
suit.

Test : 10 mots dans une carte de 50 mm de haut, bloc placé à 35 mm et remonté de moitié. Carte seule : 10 mots.
Suivie d'une autre carte : 7 mots sur la première. Sur une page de 110 mm de haut : 10 mots.

**Contrôle** : compter les mots de chaque page avant et après un changement (`verifier.py nouveau.pdf --comparer
ancien.pdf`), ou comparer au texte source.

**Parades** (les deux testées) :
- centrer par flex (`display:flex; align-items:center` sur une boîte qui tient dans la page) plutôt que par
  translateY : même position, aucun mot perdu ;
- imprimer sur une page bien plus haute que la pièce, puis recadrer. `fabriquer.py` ajoute 60 mm de hauteur.

## 4. Une police refusée devient Times New Roman, sans prévenir

**Symptôme** : Chrome refuse un fichier de police qu'il juge invalide et prend Times New Roman à la place. Rien
n'apparaît sur la ligne de commande. Dans le projet d'origine, des polices extraites de PDF étaient refusées
(« OTS parsing error: cvt: misaligned table »). Test : une police tronquée sort en
`TimesNewRomanPSMT`.

**Contrôle** : `pdffonts sortie.pdf` ne doit lister que les polices prévues, soit `verifier.py --polices
Titre,Texte`.

**Parade** : utiliser les fichiers de police d'origine (TTF ou OTF du fondeur), pas des polices extraites d'un PDF.

## 5. Une lettre absente de la police est prise ailleurs

**Symptôme** : une police de titre gratuite n'avait ni ç, ni ?, ni parenthèses. Chrome est allé chercher ces lettres
seules dans Times New Roman. Test : « Où ça ? (oui) » dans cette police donne deux polices dans le PDF.

**Contrôle** : comme au piège 4. Mieux : vérifier avant l'impression que chaque lettre existe dans la police (table
`cmap`, lisible avec fontTools), et s'arrêter sinon.

**Parade** : donner une liste de polices, `font-family:'Titre','Texte'`. Chrome prend alors les lettres absentes dans
la seconde, choisie (testé : plus de Times dans le PDF).

## 6. Le gras simulé sort en police de type 3

**Symptôme** : `font-weight:bold` alors que seule la version normale de la police est déclarée. Chrome épaissit
lui-même les lettres et les écrit en police de type 3. Aucune source qui fait autorité ne dit si ce type de police
est admis en PDF/X : à vérifier auprès de l'imprimeur (voir notions.md). L'italique simulé, lui, reste une police normale
inclinée.

**Contrôle** : `pdffonts` affiche `Type 3` ; `verifier.py` le signale.

**Parade** : déclarer le vrai fichier gras (`@font-face{…; font-weight:700}`), ou se passer de gras.

## 7. Certains effets sont pixellisés

| Effet | Résultat dans le PDF |
|---|---|
| Masque SVG (`mask="url(#…)"`), même uniforme, en `<img>` ou dans la page | une image RVB à 300 ppi plus un masque de transparence |
| `filter: blur()` en CSS | une image et un masque |
| `opacity` en SVG ou en CSS, `fill-opacity` | reste vectoriel |
| `mix-blend-mode` en CSS | reste vectoriel |

Dans le projet d'origine, les transparences d'un PDF converti en SVG par `pdftocairo -svg` ressortaient en masques
uniformes.

**Contrôle** : `pdfimages -list sortie.pdf` ne doit rien lister si tout est censé être vectoriel ; `verifier.py`
compte les images et les masques.

**Parade** : remplacer chaque masque uniforme par un attribut `opacity` de même valeur ; éviter les filtres CSS.

## 8. En-tête et pied de page de Chrome

**Symptôme** : sans `--no-pdf-header-footer`, et dès que la page a des marges, Chrome imprime la date, le titre de la
page, **le chemin du fichier sur le disque** et « 1/1 », dans une autre police (Noto Sans dans le test). Avec des marges
nulles, rien n'apparaît, faute de place : le piège surgit plus tard, quand on ajoute des marges.

**Parade** : toujours passer `--no-pdf-header-footer`. Les numéros de page voulus se font en CSS :
`@page{@bottom-center{content:counter(page)}}`.

## 9. Ce que Chrome ne fait pas

- **CMJN** : ses PDF ne contiennent que des couleurs RVB (opérateurs `rg` et `RG`, constaté). La conversion se fait
  chez l'imprimeur ou avec un autre outil.
- **PDF/X** : aucun des PDF testés ne se déclare PDF/X.
- **Débord et zone de coupe** : il ne les déclare pas. Sans recadrage, le PDF annonce la page entière comme format
  fini.

## 10. Autres pièges rencontrés en chemin

- **Lire le texte d'un PDF donne de fausses alertes.** Des lettres décoratives écrites en texte (un « z » dessiné, un
  mot en filigrane) ressortent mêlées au texte. Avant d'annoncer une faute ou un mot perdu, la confirmer sur une image
  de la page (`pdftoppm -r 150`).
- **Extraire une ancienne version d'un PDF de git** : `git cat-file blob <commit>:<chemin> > ancien.pdf`. Un filtre
  qui réécrit la sortie de `git show` (rtk par exemple) peut abîmer le fichier : le PDF est passé de 0,8 à 1,4 Mo.
  `verifier.py` signale alors des erreurs de structure.
