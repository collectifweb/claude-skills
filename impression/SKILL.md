---
name: impression
description: >
  Prépare et contrôle des fichiers destinés à l'imprimerie : jeux de société (plateau, cartes, boîte), livrets,
  dépliants, affiches. Fixe le cadre avant de dessiner (format fini, débord, marge de sécurité), fait passer une page
  web en PDF par Chrome au format exact avec zone de coupe et zone de débord déclarées, vérifie un PDF (polices
  intégrées, images et résolution, zones, texte trop près de la coupe, mots perdus entre deux versions), compose des
  planches de comparaison avant/après et prépare les questions à poser à l'imprimeur (CMJN, profil, PDF/X).
  Utiliser ce skill dès qu'un fichier doit être imprimé ou envoyé à un imprimeur, même sans le mot « impression » :
  « prépare les cartes pour l'imprimeur », « le PDF est-il bon à imprimer ? », débord, fond perdu, traits de coupe,
  zone de sécurité, CMJN, PDF/X, épreuve, gabarit de boîte, « vérifie ce PDF », « compare les deux versions ».
  Complète /impeccable sans le remplacer : impeccable juge le visuel, impression s'occupe de ce qui rend le fichier
  imprimable.
---

# Impression : des fichiers bons à imprimer

Ce skill s'occupe de tout ce qui sépare un beau visuel d'un fichier que l'imprimeur peut utiliser sans surprise : le
format exact, le débord, la marge de sécurité, les polices, les images, les couleurs et la preuve que rien ne s'est
perdu en route. Le visuel (composition, typographie, couleurs, envie) revient à /impeccable. Les deux travaillent
ensemble : impression pose le cadre au début et contrôle le fichier à la fin, impeccable dessine à l'intérieur.

Les chemins `scripts/` et `references/` sont relatifs au dossier de ce skill.

## La règle des sources

Des chiffres comme « 3 mm de débord » ou « 6 pt au minimum » circulent comme des règles. Ce ne sont que des habitudes
d'imprimeurs : aucune norme ne les fixe (voir notions.md). Une valeur fausse envoyée à un imprimeur peut coûter un
tirage. D'où trois règles :

- **Une valeur technique vient d'une source citée** : la fiche de l'imprimeur choisi, une norme ou une
  spécification de la profession. `references/notions.md` donne les sources trouvées, et dit ce pour quoi il n'en
  existe aucune (le débord et la marge de sécurité, par exemple).
- **Sans source, c'est « à vérifier auprès de l'imprimeur »**, et c'est écrit tel quel dans ce qu'on remet. Ne
  jamais inventer une norme, ni présenter l'habitude d'un imprimeur comme une règle générale.
- **Distinguer ce qu'on a mesuré de ce qu'on a lu.** Un rapport de `verifier.py` est une mesure ; une valeur tirée
  de notions.md est une lecture ; une valeur rapportée par quelqu'un est une parole. Le compte rendu dit laquelle est
  laquelle.

## Au début : poser le cadre

Avant que /impeccable dessine quoi que ce soit, ces dimensions doivent être connues, parce qu'elles décident de la
mise en page.

1. **Le support.** Lire sa fiche dans `references/supports.md` (plateau, cartes, livret, boîte, dépliant, affiche) :
   ce qui compte pour celui qui le tient, ce qu'il faut demander, ce qu'il faut contrôler.
2. **L'imprimeur.** Chercher dans le projet une fiche d'imprimeur remplie (modèle dans `references/imprimeur.md`).
   - Si elle existe, ses valeurs font foi.
   - Sinon, prendre des valeurs provisoires dans le tableau d'exemples de `references/notions.md`, les marquer
     **provisoires, à confirmer avec l'imprimeur** et noter les questions à lui poser.
3. **Écrire le cadre dans le projet** (README, notes de conception ou un fichier dédié), pour que la prochaine session
   le retrouve : format fini, débord, marge de sécurité, unités, imprimeur visé et, pour chaque valeur, sa source ou la
   mention « provisoire ».
4. **Passer la main à /impeccable** avec ces chiffres : la zone où placer le texte et les éléments importants est le
   format fini moins la marge de sécurité ; les fonds qui touchent le bord continuent jusqu'au bout du débord.

## Pendant : fabriquer le PDF

**Depuis une page web, par Chrome** : lire `references/chrome-pdf.md` avant d'écrire la page. Chrome arrondit le
format, cale les boîtes au pixel, coupe un texte centré par translateY, remplace une police refusée par Times New
Roman, pixellise les masques et simule le gras en police de type 3, sans rien signaler. Chaque piège y est décrit
avec son contrôle et sa parade.

`scripts/fabriquer.py` fait l'impression et le recadrage :

```bash
python3 scripts/fabriquer.py page.html cartes.pdf --format 63x88mm --debord 3mm
python3 scripts/fabriquer.py livret.html livret.pdf --format 148x210mm --debord 3mm --flux
```

- **Pages fixes** (cartes, plateau, boîte, affiche) : une `<section class="page">` par page, avec dedans une
  `<div class="fini">` au format fini. Le fond de la section remplit le débord. Le script donne leur taille aux deux
  boîtes.
- **`--flux`** (livret) : Chrome répartit le texte ; les marges se règlent avec `@page{margin:…}`, débord compris.
- Il demande pypdf (`pip install pypdf`, de préférence dans un environnement virtuel) et un Chrome : `--chrome`, la
  variable `CHROME`, celui de Playwright dans `~/.cache/ms-playwright/` ou un chromium du PATH.

**Depuis un autre outil** (InDesign, Affinity, Inkscape, Canva, un fichier reçu d'un graphiste) : ce skill ne couvre
pas leurs réglages d'export, mais le contrôle de fin s'applique à tout PDF.

## À la fin : contrôler

### 1. Le rapport de `verifier.py`

```bash
python3 scripts/verifier.py cartes.pdf --format 63x88mm --debord 3mm --surete 3mm --resolution 300 --polices Lora,Inter
python3 scripts/verifier.py cartes.pdf --comparer ancienne-version.pdf
```

Sans option, il décrit le fichier et ne signale que ce qui pose problème partout : police non intégrée, police de
type 3, page sans zone de coupe distincte, fichier abîmé. Avec les options (les valeurs de l'imprimeur), il signale :

- un format fini différent du format demandé (au-delà de 0,02 mm) ;
- un débord plus petit que demandé ;
- chaque mot plus près de la coupe que la marge de sécurité, avec sa page et sa distance ;
- chaque image sous la résolution demandée ;
- toute police hors de la liste attendue, avec les pages où elle apparaît ;
- avec `--comparer`, chaque page dont les mots ont changé, et lesquels.

Il sort avec le code 1 s'il a trouvé une alerte. Ce qu'il ne voit pas : l'épaisseur des traits, les couleurs des
tracés, le texte dessiné en tracés et tout ce qui demande un œil.

Une alerte se confirme sur une image de la page avant d'être annoncée. L'extraction de texte d'un PDF mêle parfois
des lettres décoratives au texte, et la boîte d'un mot inclut la hauteur de ligne de sa police.

### 2. La planche de `planche.py`

```bash
python3 scripts/planche.py avant.pdf apres.pdf -o planche.jpg --etiquettes "Avant,Après" --pages 1-12
python3 scripts/planche.py cartes.pdf -o coupe.jpg --vue coupe,debord --pages 1-6
python3 scripts/planche.py plateau-v1.pdf plateau-v2.pdf -o detail.jpg --zone 100,50,60,40 --dpi 200
```

- **Avant/après** : la même page de chaque version côte à côte. C'est ainsi qu'un changement se valide : chaque pièce
  touchée, regardée à côté de la version précédente ou du modèle.
- **Coupe et débord** : ce que la coupe retirera.
- **Gros plan** : un détail à 200 dpi au moins, en mm depuis le coin haut gauche du format fini. Un trait fin ou une
  courbe cassée ne se voient pas sur un aperçu entier.

Regarder la planche soi-même (lire l'image) avant d'en parler, et la montrer.

### 3. La liste de contrôle avant l'envoi

Cocher chaque ligne, ou dire pourquoi elle ne s'applique pas.

**Le fichier**
- [ ] Le format fini de chaque page est celui de la fiche de l'imprimeur (`--format`).
- [ ] Le débord est déclaré et suffisant de chaque côté (`--debord`). Les fonds qui touchent la coupe continuent dans
  le débord (planche `--vue debord`).
- [ ] Aucun texte ni élément important dans la marge de sécurité (`--surete`, puis la planche pour ce qui est dessiné).
- [ ] Toutes les polices sont intégrées, ou vectorisées si l'imprimeur le demande. Aucune police de remplacement.
  Pas de type 3 sans son accord.
- [ ] Aucune image sous la résolution demandée, ni d'image inattendue (un effet pixellisé).
- [ ] Aucune erreur de structure signalée par le script.
- [ ] Le texte de chaque page est complet : comparé à la source ou à la version précédente (`--comparer`).
- [ ] Le mode de couleur, le profil et le noir du texte sont convenus avec l'imprimeur.
- [ ] Le format de fichier (PDF, PDF/X, version) est celui qu'il demande.

**Le contenu**
- [ ] Relu sur une planche à taille lisible, recto et verso ensemble.
- [ ] Les nombres justes : cartes, exemplaires, pages (un multiple de 4 pour un livret agrafé).
- [ ] Les traits fins et les petits textes regardés agrandis : le script ne les mesure pas.
- [ ] Une maquette papier pour tout ce qui se plie (boîte, dépliant, plateau).
- [ ] Les licences des polices et des images permettent l'usage prévu (commercial ou non).

**L'envoi**
- [ ] Des noms de fichiers clairs, avec une date ou un numéro de version.
- [ ] La fiche de l'imprimeur est à jour, et les questions encore ouvertes sont posées (`references/imprimeur.md`).
- [ ] Une épreuve est demandée avant le tirage.

## Rendre compte

Le compte rendu sépare trois choses :

1. **Mesuré** : ce que les scripts ont trouvé, avec la commande lancée et le fichier visé. Une alerte confirmée sur
   une image est dite « confirmée à l'œil ».
2. **À voir** : ce que les scripts ne contrôlent pas, et ce que la planche montre.
3. **À demander** : les valeurs encore provisoires et les questions pour l'imprimeur.

Ne jamais écrire qu'un fichier est « prêt à imprimer » tant que les valeurs utilisées ne viennent pas de l'imprimeur
choisi. Écrire plutôt : « conforme aux valeurs provisoires suivantes, à confirmer avec l'imprimeur ».

## Références

| Fichier | À lire quand |
|---|---|
| `references/notions.md` | une notion ou un chiffre est en jeu : débord, marge, polices, résolution, traits, texte, couleurs, PDF/X. Sources en fin de fiche |
| `references/supports.md` | au début d'un support, et pour savoir quoi contrôler à la fin |
| `references/chrome-pdf.md` | avant de produire un PDF par Chrome, et quand un PDF de Chrome surprend |
| `references/imprimeur.md` | pour préparer les questions et remplir la fiche de l'imprimeur |
