# L'imprimeur : les questions à poser, la fiche à remplir

Presque tout ce qui rend un fichier bon à imprimer dépend de l'imprimeur : son procédé, son papier, ses machines,
son logiciel de contrôle. Les fabricants se contredisent d'ailleurs entre eux : CMJN chez les uns, RVB chez un autre ;
PDF/X chez l'un, simple PDF chez les autres (notions.md). D'où cette règle : **une valeur ne devient définitive
que lorsqu'elle est écrite dans la fiche de l'imprimeur choisi, avec d'où elle vient.**

La fiche remplie vit dans le dossier du projet (par exemple `Imprimerie/<imprimeur>.md`), jamais dans le skill : elle
peut contenir des prix, des noms et des adresses.

## Les questions

Toutes ne servent pas à chaque projet : garder celles qui concernent les supports commandés. Beaucoup ont leur
réponse dans la fiche technique ou les gabarits de l'imprimeur : les lire d'abord, ne demander que ce qui manque.

**Format et découpe**
1. Quel format fini exact, en mm ou en pouces ? (63 × 88 mm et 2,5 × 3,5 po ne sont pas le même format.)
2. Quel débord, par côté ? Et pour les pièces rabattues (boîte, plateau) ?
3. Quelle marge de sécurité, à partir de la coupe ? À partir des plis ?
4. Fournissez-vous des gabarits (cartes, boîte, plateau) ? Dans quel format ?
5. Comment livrer les lignes de découpe et de pli : dans un calque à part, dans un fichier à part ou pas du tout ?
6. Faut-il des traits de coupe et des repères dans le fichier, ou les ajoutez-vous ?
7. Quelle est votre tolérance de coupe ? Et de décalage entre recto et verso ?

**Fichiers**
8. Quel format de fichier : PDF, PDF/X (lequel : X-1a, X-3, X-4), PNG, autre ?
9. Quelle version de PDF au minimum ?
10. Comment organiser les pages : un fichier par pièce, recto puis verso, une page par exemplaire ou par modèle ?
11. La zone de coupe (TrimBox) et la zone de débord (BleedBox) doivent-elles être déclarées dans le PDF ?

**Couleurs**
12. CMJN ou RVB ? Si le fichier arrive en RVB, faites-vous la conversion, et avec quel profil ?
13. Quelle condition d'impression ou quel profil viser (FOGRA39, FOGRA51, GRACoL 2013, ISO Coated v2, le vôtre) ?
14. Quel encrage total maximal ?
15. Le texte noir doit-il être en noir pur (encre noire seule) ? Comment convertissez-vous le noir RVB ?
16. Un noir de fond (aplat) doit-il être en noir enrichi ? Avec quelles valeurs ?
17. Tons directs (Pantone) possibles ? À quel prix ?

**Texte et traits**
18. Polices intégrées, ou converties en tracés ?
19. Les polices de type 3 sont-elles acceptées ?
20. Taille minimale du texte : d'une seule encre, de plusieurs encres, en blanc sur un fond ?
21. Épaisseur minimale d'un trait : d'une seule encre, de plusieurs encres, en blanc ?

**Images**
22. Résolution minimale à la taille imprimée ? Et pour les images au trait ?
23. Transparences : à aplatir, ou acceptées telles quelles ?

**Épreuve et finition**
24. Quelle épreuve avant le tirage : PDF, épreuve couleur papier, prototype ? À quel prix ?
25. Quel papier, quel grammage, quelle finition (pelliculage, vernis, texture) ?
26. Quels contrôles faites-vous à réception du fichier, et que se passe-t-il si un fichier est refusé ?

Le message qui part vers l'imprimeur est un texte envoyé à un tiers : le relire comme tel (/humanize s'il est
disponible).

## La fiche à remplir

Copier ce modèle dans le dossier du projet. Chaque valeur porte sa source : sans source, elle reste une hypothèse.

```markdown
# <Imprimeur> : exigences pour <projet>

Contact : <nom, courriel> · Dernière mise à jour : <date>

| Sujet | Valeur | Source (document, courriel, date) |
|---|---|---|
| Format fini : cartes | | |
| Format fini : plateau | | |
| Format fini : livret | | |
| Gabarit de la boîte | <fichier> | |
| Débord (par côté) | | |
| Débord des pièces rabattues | | |
| Marge de sécurité | | |
| Lignes de découpe et de pli | <calque à part, fichier à part, aucune> | |
| Traits de coupe et repères | <dans le fichier, ajoutés par l'imprimeur> | |
| Format de fichier | <PDF, PDF/X-…, PNG> | |
| Version de PDF minimale | | |
| Organisation des pages | | |
| Couleurs | <CMJN, RVB, converties par l'imprimeur> | |
| Profil ou condition d'impression | | |
| Encrage total maximal | | |
| Noir du texte | | |
| Polices | <intégrées, vectorisées> | |
| Polices de type 3 | <acceptées, refusées> | |
| Texte minimal | | |
| Trait minimal | | |
| Résolution minimale des images | | |
| Transparences | | |
| Épreuve | | |
| Papier et finition | | |

## Commande de vérification pour cet imprimeur

verifier.py fichier.pdf --format <…> --debord <…> --surete <…> --resolution <…> --polices <…>

## Questions encore ouvertes

-
```

Une fois remplie, la ligne « Commande de vérification » donne les options de `verifier.py` à utiliser pour cet
imprimeur, sans avoir à les chercher.
