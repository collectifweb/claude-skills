# Notions de base

Ce qui rend un fichier bon à imprimer, avec la source de chaque chiffre. Un chiffre sans source qui fait autorité
est marqué **à vérifier auprès de l'imprimeur**. Les fiches des imprimeurs cités le sont comme exemples de ce qu'ils
demandent, jamais comme une norme. Les numéros entre crochets renvoient aux sources en fin de fiche.

## Sommaire

1. Les zones d'une page : format fini, débord, marge de sécurité
2. Polices intégrées
3. Vectoriel ou image, et la résolution
4. Épaisseur minimale des traits
5. Taille minimale du texte
6. Couleurs : RVB, CMJN, conditions d'impression
7. PDF/X
8. Ce que la norme ne dit pas

## 1. Les zones d'une page

Un PDF peut déclarer cinq zones par page [1] :

| Zone PDF | En français | Ce qu'elle dit |
|---|---|---|
| MediaBox | page entière | la feuille sur laquelle le PDF est dessiné |
| CropBox | zone visible | ce qu'affiche un lecteur de PDF ; par défaut, la page entière |
| BleedBox | zone de débord | jusqu'où le contenu est imprimé avant la coupe |
| TrimBox | zone de coupe, format fini | les dimensions de la pièce une fois coupée |
| ArtBox | zone utile | l'étendue du contenu qui a du sens pour l'auteur |

Ce qu'en dit la norme PDF (ISO 32000-1, §14.11.2) [1] :

- la zone de coupe « définit les dimensions voulues de la page finie après la coupe » ;
- la zone de débord « peut inclure la surface de débord nécessaire pour absorber les limites physiques des machines
  de coupe, de pliage et de massicotage » ;
- **sans déclaration, la zone de coupe et la zone de débord valent la zone visible.** Un PDF qui ne déclare rien
  annonce donc que la page entière est le format fini, sans débord.

**Le débord** : tout ce qui touche le bord fini (fond, illustration, cadre) doit continuer au-delà de la coupe, dans
le débord, parce que la coupe n'est jamais exacte. Panda Game Manufacturing donne une tolérance de coupe de ±1 mm
pour la plupart de ses pièces [10].

Taille du débord : **aucune norme trouvée, à vérifier auprès de l'imprimeur.** Exemples relevés le 8 octobre 2026 :

| Imprimeur | Débord | Marge de sécurité |
|---|---|---|
| Panda Game Manufacturing (fabricant de jeux) [10] | 3 mm au moins ; 18 mm pour une boîte ou un plateau (3 mm plus 15 mm rabattus) | 3 mm au moins |
| LongPack Games (fabricant de jeux) [11] | 3 mm ; 20 mm pour une boîte ou un plateau | 3 mm au moins |
| Efko (fabricant de jeux) [12] | 3 mm au moins (5 mm si nécessaire) ; 18 mm pour une boîte, 22 mm pour l'habillage d'un plateau | 3 mm sur les cartes, 4 mm des lignes de découpe ailleurs |
| The Game Crafter (impression à la demande) [13] | 1/8 po (3,175 mm) | 1/8 po, soit 1/4 po depuis le bord de l'image débord compris |
| MakePlayingCards [14] | 1/8 po | 1/8 po |
| PrintNinja (plateaux) [15] | 0,125 po | 0,125 po |
| Vistaprint [16] | 0,125 po dans son exemple | 0,125 po dans son exemple |

**La marge de sécurité** (zone de sûreté) : la bande, à l'intérieur de la coupe, où rien d'important ne doit se
trouver, pour qu'une coupe décalée ne le rogne pas. Aucune norme trouvée non plus : **à vérifier auprès de
l'imprimeur** (exemples dans le tableau).

Ce que demande le Ghent Workgroup, l'association qui publie les règles de contrôle des fichiers d'impression
(GWG2015) [2] :

- la zone visible doit être égale à la page entière (§4.3) ;
- toutes les pages doivent avoir la même taille de format fini, et aucune ne doit être pivotée (§4.4).

## 2. Polices intégrées

Une police intégrée voyage dans le PDF : l'imprimeur n'a pas besoin de l'avoir. Pour PDF/X, quelle qu'en soit la
version : « les polices doivent être intégrées (en entier, ou en sous-ensemble contenant tous les caractères
utilisés) » [4]. `pdffonts` le dit dans sa colonne `emb`.

- **Police de type 3** : aucune source qui fait autorité ne dit si elle est admise en PDF/X. **À vérifier auprès de
  l'imprimeur.** Avec Chrome, elle trahit un gras simulé (voir chrome-pdf.md).
- **Polices vectorisées** : Efko demande au contraire de convertir les polices en tracés, si l'on n'est pas sûr que
  le logiciel les intègre correctement [12]. Le texte n'est alors plus du texte : ni recherche, ni contrôle de
  la marge de sécurité par le script.
- **Licence** : vérifier que la licence de chaque police permet l'usage commercial et l'intégration dans un PDF.

## 3. Vectoriel ou image, et la résolution

Un tracé vectoriel (texte, forme, SVG) n'a pas de résolution : il reste net à toute taille. Une image est une
grille de pixels ; sa **résolution effective** est son nombre de pixels divisé par sa taille imprimée en pouces.
Une image de 750 px imprimée sur 2,5 po est à 300 ppi. `pdfimages -list` donne cette résolution effective
(colonnes `x-ppi` et `y-ppi`).

- Adobe : « une résolution de 300 pixels par pouce est le standard de l'industrie pour des impressions de haute
  qualité » ; pour une image tramée, on vise « environ 1,5 à 2 fois la linéature de trame » [3].
- Ghent Workgroup, seuils de contrôle des images en couleur ou en niveaux de gris [2] [5] :

| Procédé (variante GWG) | Erreur à ou sous | Avertissement à ou sous |
|---|---|---|
| Offset feuille, CMJN (GWG2015 SheetCmyk, et GWG2022) | 149 ppi | 224 ppi |
| Presse et magazine (Magazine Ads) | 149 ppi | 224 ppi |
| Journal (Newspaper Ads) | 99 ppi | 149 ppi |
| Impression numérique (GWG2022 Digital Print) | 95 ppi | 149 ppi |

  Images au trait (1 bit) : erreur à 549 ppi, avertissement à 799 ppi en offset ; 349 et 599 ppi en numérique.
- Les fabricants de jeux cités demandent 300 ppi ou plus [10] [11] [12], comme The Game Crafter [13],
  MakePlayingCards [14] et Vistaprint [16].

**Le seuil exact : à vérifier auprès de l'imprimeur.** Le mieux reste de garder en vectoriel tout ce qui peut
l'être.

## 4. Épaisseur minimale des traits

Le Ghent Workgroup ne fixe un minimum qu'aux traits **blancs** (réservés dans un fond) et aux traits faits de
**plusieurs encres** : ce sont eux qu'un léger décalage entre les couleurs abîme. Ces minimums donnent un
avertissement, pas une erreur [2] [5] :

| Procédé | Trait blanc ou de plusieurs encres |
|---|---|
| Offset feuille, presse, journal (GWG2015 et GWG2022) | 0,25 pt (0,09 mm) |
| Impression numérique (GWG2022) | 0,25 pt |
| Grand format (GWG2022, traits de plusieurs encres) | 0,15 pt |
| Carton plié (GWG2022, traits de plusieurs encres) | 1,5 pt |

Pour un trait d'une seule encre (noir pur par exemple), aucun minimum chez le Ghent Workgroup. Efko demande
0,1 mm au moins sur les cartes [12]. **À vérifier auprès de l'imprimeur.** Le script de vérification ne mesure
pas les traits : les regarder sur une planche agrandie.

## 5. Taille minimale du texte

Même logique : le Ghent Workgroup ne vise que le texte **blanc** et le texte fait de **plusieurs encres** ; ces
minimums donnent un avertissement [2] [5] :

| Procédé | Texte blanc ou de plusieurs encres |
|---|---|
| Offset feuille (SheetCmyk) | 8 pt |
| Presse et magazine | 9 pt |
| Journal | 10 pt |
| Impression numérique (GWG2022) | 5 pt |
| Carton plié (GWG2022, texte de plusieurs encres) | 14 pt |

Texte d'une seule encre : pas de minimum chez le Ghent Workgroup. Efko demande 6 pt au moins sur les cartes pour
un texte d'une couleur [12]. **À vérifier auprès de l'imprimeur.**

Ces chiffres disent ce qui s'imprime proprement, pas ce qui se lit confortablement. La lisibilité dépend de la
distance de lecture (voir supports.md) et relève du jugement visuel (/impeccable).

## 6. Couleurs : RVB, CMJN, conditions d'impression

- **RVB** (rouge, vert, bleu) : les couleurs de l'écran. **CMJN** (cyan, magenta, jaune, noir) : les encres de
  l'imprimerie. Un document d'Adobe hébergé par l'ICC, le consortium des profils de couleur : « en général, un
  espace CMJN d'appareil représente des couleurs moins saturées et moins nombreuses qu'un espace RVB » [8]. Un rose
  vif à l'écran peut donc sortir plus terne.
- **Chrome écrit toutes ses couleurs en RVB** (constaté : ses PDF ne contiennent que des couleurs RVB). La
  conversion en CMJN se fait ailleurs : chez l'imprimeur, ou avec un autre outil.
- **Une condition d'impression** décrit un couple procédé et papier, mesuré. C'est elle qui fixe à quoi ressemblera
  une valeur CMJN. Exemples du registre de l'ICC [7] :

| Nom | Ce qu'elle décrit | Encrage total maximal |
|---|---|---|
| FOGRA39 | offset selon ISO 12647-2:2004/Amd 1, papier couché brillant ou mat (types 1 et 2) | non indiqué |
| FOGRA51 | offset selon ISO 12647-2:2013, papier couché premium (PS1) | non indiqué |
| GRACoL2013 (CRPC6) | condition de référence CGATS.21-2, d'usage nord-américain | 320 % |
| SWOP2013 (CRPC5) | condition de référence CGATS.21-2 | 300 % |

  Panda Game Manufacturing demande FOGRA39 [10] ; LongPack, le profil ISO Coated v2 [11] ; Efko, de n'ajouter
  aucun profil, ou à la rigueur Fogra 39 [12].
- **Encrage total** : la somme des quatre encres en un point. Le Ghent Workgroup avertit au-delà de 320 % en offset
  feuille (moyenne sur un carré de 15 mm) [2]. Efko plafonne à 270 % en un point, 280 % pour les cartes [12].

Tout ceci se décide avec l'imprimeur : les questions sont dans imprimeur.md.

## 7. PDF/X

PDF/X est une famille de normes ISO (ISO 15930) pour l'échange de fichiers d'impression [6] [9] :

| Version | Norme | En bref |
|---|---|---|
| PDF/X-1a:2001 et 2003 | ISO 15930-1 et -4 | CMJN, niveaux de gris et tons directs seulement ; pas de RVB [9] |
| PDF/X-3:2002 et 2003 | ISO 15930-3 et -6 | admet des couleurs gérées par profil, dont le RVB avec profil ICC [9] |
| PDF/X-4 (2010) | ISO 15930-7 | admet la transparence et les calques, interdits avant elle [9] |

Règles communes à toutes les versions [4] :

- polices intégrées ;
- une condition d'impression de sortie (« Output Intent »), donnée par un profil ICC, dès que le fichier contient
  des couleurs ;
- si un débord est défini, la zone de débord doit être à l'extérieur de la zone de coupe.

Le Ghent Workgroup exige PDF/X-4 dans toutes ses variantes [2] [5], avec un profil de sortie CMJN (§4.30).

Un PDF se **déclare** PDF/X par une condition de sortie de type GTS_PDFX [1], et `pdfinfo` affiche alors une ligne
« PDF subtype ». Se déclarer n'est pas être conforme : seul un contrôle en amont (par exemple le contrôle PDF/X
d'Acrobat) le vérifie. Chrome ne produit pas de PDF/X (constaté : aucun des PDF testés ne se déclare PDF/X). Faut-il
en livrer un ? **À vérifier auprès de l'imprimeur** : parmi les fabricants cités, seul Efko le demande (PDF/X-1a, X-3 ou X-4 ; PDF 1.3 ou 1.4 pour les cartes) [12] ; Panda
et LongPack demandent un PDF compatible Acrobat 7 (PDF 1.6) [10] [11], et The Game Crafter des PNG ou JPG en RVB [13].

## 8. Ce que la norme ne dit pas

Aucune source qui fait autorité n'a été trouvée pour : la taille du débord, la marge de sécurité, le minimum d'un
trait ou d'un texte d'une seule encre, l'admission des polices de type 3 en PDF/X. Ces valeurs se demandent à
l'imprimeur et se notent dans sa fiche (imprimeur.md).

## Sources

Consultées le 8 octobre 2026. Les sites d'Adobe, de l'ISO et de la PDF Association refusent les lectures
automatisées : leurs pages ont été lues sur les copies d'archive.org, dont la date est indiquée.

1. ISO 32000-1:2008, *Document management - Portable document format - Part 1: PDF 1.7*, §14.11.2 « Page
   Boundaries » (p. 628) et §14.11.5 « Output Intents ». Copie publiée par Adobe, `PDF32000_2008.pdf` :
   https://web.archive.org/web/2020/https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf
2. Ghent Workgroup, *GWG2015 Specification*, version de publication du 17 novembre 2015 (§4.3, 4.4, 4.16, 4.17,
   4.22, 4.26, 4.27, 4.30 et tableau de la variante SheetCmyk) :
   https://gwg.org/wp-content/uploads/2026/05/GWG2015-Specification_Release.pdf
3. Adobe, « Photoshop image size and resolution », copie archive.org du 15 mars 2025 :
   https://web.archive.org/web/20250315085701/https://helpx.adobe.com/hk_en/photoshop/using/image-size-resolution.html
4. PDF Association, « PDF/X – the key facts », copie archive.org de novembre 2025 :
   https://pdfa.org/pdfx-the-key-facts/
5. Ghent Workgroup, *GWG2022 Specifications*, tableur public (onglet Variants, règles R0016 à R0019, R0031,
   R0032) : https://tinyurl.com/gwg2022. La page de présentation dit aujourd'hui ces spécifications réservées aux
   membres.
6. ISO, fiches des normes ISO 15930-1:2001, -3:2002, -4:2003, -6:2003 et -7:2010 :
   https://www.iso.org/standard/29061.html, /34941.html, /39938.html, /39940.html, /55843.html
7. ICC, registre des données de caractérisation et des profils : https://registry.color.org/cmyk-registry/fogra39,
   https://registry.color.org/cmyk-registry/fogra51, https://registry.color.org/profile-registry/GRACoL2013_CRPC6,
   https://registry.color.org/profile-registry/SWOP2013C3_CRPC5
8. James C. King, *Why Color Management?*, Adobe Systems, 1er octobre 2001, hébergé par l'ICC :
   https://archive.color.org/files/whycolormanagement.pdf
9. PDF Association, « Technical side and requirements of PDF/X » et tableau « ISO 15930 (PDF/X) », copies
   archive.org : https://pdfa.org/technical-side-and-requirements-of-pdfx/ et https://pdfa.org/resource/iso-15930-pdfx/

Exemples d'imprimeurs (ce qu'ils demandent, pas une norme) :

10. Panda Game Manufacturing, *Graphic Design Guidebook V4* (septembre 2022) :
    https://pandagm.com/wp-content/uploads/2022/10/PandaGM-GraphicDesignGuidebook-V4-0922.pdf
11. LongPack Games, centre d'aide (articles 50, 51, 52, 58, 59, 61, 66) : https://help.longpackgames.com/
12. Efko, *Manual for artworks* : https://www.efko.cz/en/for-partners/download/5
13. The Game Crafter, articles d'aide 33 et 39 : https://help.thegamecrafter.com/article/33-dpi-dots-per-inch et
    https://help.thegamecrafter.com/article/39-templates
14. MakePlayingCards, page produit des cartes au format poker :
    https://www.makeplayingcards.com/design/custom-poker-white-traditional-size.html
15. PrintNinja, guide des plateaux : https://printninja.com/game-board-setup-guides/
16. Vistaprint, préparation des cartes de visite : https://www.vistaprint.com/hub/business-card-file-prep/
