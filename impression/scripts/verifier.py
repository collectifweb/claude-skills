#!/usr/bin/env python3
"""Vérifie qu'un PDF est prêt à imprimer : format et zones, polices, images, texte trop près de la coupe.

Usage :
  verifier.py fichier.pdf [--format 63x88mm] [--debord 3mm] [--surete 3mm] [--resolution 300]
                          [--polices Montserrat,Lora] [--comparer ancienne-version.pdf]

Sans option, le script décrit le fichier et ne signale que ce qui pose problème quel que soit l'imprimeur : police
non intégrée, police de type 3, page sans zone de coupe distincte. Les seuils (débord, marge de sécurité,
résolution) dépendent de l'imprimeur : on les passe en option. Unités : mm, cm, in (ou po), pt.

--comparer compte les mots de chaque page dans les deux versions : une ligne perdue en route se voit tout de suite.

Demande poppler-utils (pdfinfo, pdffonts, pdfimages, pdftotext). Sortie : 0 sans alerte, 1 avec au moins une alerte.
"""
import argparse, difflib, html, re, shutil, subprocess, sys

UNITES = {'mm': 72 / 25.4, 'cm': 720 / 25.4, 'in': 72, 'po': 72, 'pt': 1}
NOMBRE, UNITE = r'(\d+(?:[.,]\d+)?)', r'\s*(mm|cm|in|po|pt)'
TYPES_DE_POLICE = (r'CID Type 0C \(OT\)|CID Type 0C|CID Type 0|CID TrueType \(OT\)|CID TrueType|Type 1C \(OT\)|'
                   r'Type 1C|Type 1|Type 3|TrueType \(OT\)|TrueType|unknown')
alertes, erreurs_de_lecture = [], {}


def longueur(texte):
    """'3mm', '0,125 in', '9pt' → points."""
    m = re.fullmatch(rf'\s*{NOMBRE}{UNITE}\s*', texte)
    if not m:
        raise argparse.ArgumentTypeError(f'longueur illisible : {texte} (exemples : 3mm, 0.125in, 9pt)')
    return float(m.group(1).replace(',', '.')) * UNITES[m.group(2)]


def format_(texte):
    """'63x88mm', '20 x 16 in' → (largeur, hauteur) en points."""
    m = re.fullmatch(rf'\s*{NOMBRE}\s*[x×]\s*{NOMBRE}{UNITE}\s*', texte)
    if not m:
        raise argparse.ArgumentTypeError(f'format illisible : {texte} (exemples : 63x88mm, 20x16in)')
    u = UNITES[m.group(3)]
    return float(m.group(1).replace(',', '.')) * u, float(m.group(2).replace(',', '.')) * u


def mm(pt, decimales=2):
    return f'{pt * 25.4 / 72:.{decimales}f}'.replace('.', ',')


def dimensions(l, h):
    return f'{mm(l)} × {mm(h)} mm ({l / 72:.3f} × {h / 72:.3f} po)'.replace('.', ',')


def alerte(texte):
    alertes.append(texte)
    print(f'  ⚠ {texte}')


def lancer(*commande):
    """Sortie d'un outil poppler. Ses plaintes sur la structure du fichier sont gardées pour le bilan : un PDF abîmé
    se lit quand même, mais avec du texte ou des polices en moins, sans autre signe."""
    resultat = subprocess.run(commande, capture_output=True, text=True, errors='replace')
    if resultat.returncode:
        sys.exit(f'{commande[0]} a échoué : {resultat.stderr.strip()}')
    fichier = next((c for c in commande if c.lower().endswith('.pdf')), '')
    for ligne in resultat.stderr.splitlines():
        if 'Error' in ligne:
            erreurs_de_lecture[f'{fichier} : {ligne}'] = 1
    return resultat.stdout


def plages(numeros):
    """[1, 2, 3, 7] → '1-3, 7'"""
    morceaux, debut = [], None
    for i, n in enumerate(numeros):
        if debut is None:
            debut = n
        if i + 1 == len(numeros) or numeros[i + 1] != n + 1:
            morceaux.append(str(debut) if debut == n else f'{debut}-{n}')
            debut = None
    return ', '.join(morceaux)


# ---------- lecture du PDF
def nombre_de_pages(pdf):
    return int(re.search(r'^Pages:\s+(\d+)', lancer('pdfinfo', pdf), re.M).group(1))


def zones(pdf):
    """Les zones de chaque page, en points : {page: {'MediaBox': (x0, y0, x1, y1), ..., 'rot': 0}}.
    poppler donne à une zone absente sa valeur par défaut (la CropBox pour BleedBox, TrimBox et ArtBox)."""
    sortie = lancer('pdfinfo', '-box', '-f', '1', '-l', str(nombre_de_pages(pdf)), pdf)
    pages = {}
    for p, nom, valeurs in re.findall(r'^Page\s+(\d+) (MediaBox|CropBox|BleedBox|TrimBox|ArtBox):\s+(.+)$', sortie, re.M):
        pages.setdefault(int(p), {})[nom] = tuple(float(v) for v in valeurs.split())
    for p, rot in re.findall(r'^Page\s+(\d+) rot:\s+(\d+)', sortie, re.M):
        pages[int(p)]['rot'] = int(rot)
    return pages


def polices(pdf, page=None):
    """[(nom sans préfixe de sous-ensemble, type, intégrée)] tels que les liste pdffonts."""
    options = ['-f', str(page), '-l', str(page)] if page else []
    trouvees = []
    for ligne in lancer('pdffonts', *options, pdf).splitlines()[2:]:
        m = re.match(rf'(.*?)\s+({TYPES_DE_POLICE})\s+\S+\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$', ligne)
        if m:
            trouvees.append((re.sub(r'^[A-Z]{6}\+', '', m.group(1)), m.group(2), m.group(3) == 'yes'))
    return trouvees


def images(pdf):
    """Les images de pdfimages -list : page, type, largeur, hauteur, couleur, résolution horizontale et verticale."""
    trouvees = []
    for ligne in lancer('pdfimages', '-list', pdf).splitlines()[2:]:
        c = ligne.split()
        if len(c) >= 14:
            trouvees.append({'page': int(c[0]), 'type': c[2], 'l': int(c[3]), 'h': int(c[4]), 'couleur': c[5],
                             'ppi': min(float(c[12]), float(c[13]))})
    return trouvees


def mots(pdf):
    """Les mots de chaque page avec leur boîte, en points depuis le coin haut gauche de la page."""
    pages = []
    for contenu in re.findall(r'<page [^>]*>(.*?)</page>', lancer('pdftotext', '-bbox', pdf, '-'), re.S):
        pages.append([(float(a), float(b), float(c), float(d), html.unescape(t)) for a, b, c, d, t in re.findall(
            r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', contenu)])
    return pages


# ---------- les contrôles
def controler_zones(pages, attendu, debord_min):
    print('\nFORMAT ET ZONES')
    groupes = {}
    for p, z in pages.items():
        cle = tuple(tuple(round(v, 2) for v in z[nom]) for nom in ('MediaBox', 'CropBox', 'BleedBox', 'TrimBox')) + (z['rot'],)
        groupes.setdefault(cle, []).append(p)
    for (media, crop, fond_perdu, coupe, rot), numeros in groupes.items():
        print(f'Page{"s" if len(numeros) > 1 else ""} {plages(numeros)} :')
        print(f'  page entière       {dimensions(media[2] - media[0], media[3] - media[1])}')
        l, h = coupe[2] - coupe[0], coupe[3] - coupe[1]
        print(f'  format fini        {dimensions(l, h)}  (zone de coupe, TrimBox)')
        cotes = {'gauche': coupe[0] - fond_perdu[0], 'droite': fond_perdu[2] - coupe[2],
                 'haut': fond_perdu[3] - coupe[3], 'bas': coupe[1] - fond_perdu[1]}
        print('  débord             ' + ', '.join(f'{mm(v)} mm {c}' for c, v in cotes.items()) + '  (BleedBox)')
        if crop != media:
            print('  zone visible       plus petite que la page (la CropBox diffère de la MediaBox)')
        if coupe == media:
            alerte('aucune zone de coupe distincte : la page entière est le format fini, sans débord. Acceptable '
                   'seulement si rien ne touche le bord et si l\'imprimeur l\'accepte.')
        elif debord_min is not None and min(cotes.values()) < debord_min - 0.01:
            alerte(f'débord plus petit que les {mm(debord_min)} mm demandés')
        if attendu is not None:
            ecart = max(abs(l - attendu[0]), abs(h - attendu[1]))
            if ecart > 0.06:  # 0,02 mm : la précision de pdfinfo est de 0,01 pt
                if max(abs(l - attendu[1]), abs(h - attendu[0])) <= 0.06:
                    alerte('format fini pivoté par rapport au format demandé (portrait et paysage inversés)')
                else:
                    alerte(f'format fini différent du format demandé, {dimensions(*attendu)} : écart de {mm(ecart)} mm')
        if rot:
            print(f'  rotation           {rot}° à l\'affichage')


def controler_polices(pdf, n, attendues):
    print('\nPOLICES')
    trouvees = polices(pdf)
    if not trouvees:
        print('  aucune police : pas de texte, ou texte dessiné en tracés')
        return
    for nom, genre, integree in sorted(set(trouvees)):
        print(f'  {nom:40s} {genre:18s} {"intégrée" if integree else "NON INTÉGRÉE"}')
    suspectes = {}
    for nom, genre, integree in set(trouvees):
        if not integree:
            suspectes[nom] = 'n\'est pas intégrée au fichier'
        elif genre == 'Type 3':
            suspectes[nom] = 'est en type 3 (avec Chrome, un gras simulé en produit)'
        elif attendues and not any(a in re.sub(r'[\s_-]', '', nom).lower() for a in attendues):
            suspectes[nom] = 'n\'est pas dans la liste attendue (avec Chrome : peut-être une police de remplacement)'
    if suspectes:  # où sont-elles ? une page à la fois
        ou = {nom: [p for p in range(1, n + 1) if any(f[0] == nom for f in polices(pdf, p))] for nom in suspectes}
        for nom, motif in suspectes.items():
            pages = ou[nom]
            alerte(f'{nom} {motif}, page{"s" if len(pages) > 1 else ""} {plages(pages[:20])}'
                   f'{"…" if len(pages) > 20 else ""}')


def controler_images(pdf, seuil):
    print('\nIMAGES')
    trouvees = images(pdf)
    dessins = [i for i in trouvees if i['type'] == 'image']
    if not dessins:
        print('  aucune image : tout est vectoriel')
        return
    couleurs = sorted({i['couleur'] for i in dessins})
    print(f'  {len(dessins)} image{"s" if len(dessins) > 1 else ""}, sur les pages '
          f'{plages(sorted({i["page"] for i in dessins}))}, en {", ".join(couleurs)}')
    masques = [i for i in trouvees if i['type'] in ('smask', 'mask')]
    if masques:
        print(f'  {len(masques)} masque{"s" if len(masques) > 1 else ""} de transparence (voir '
              'chrome-pdf.md, piège 7)')
    print(f'  résolution la plus basse : {min(i["ppi"] for i in dessins):.0f} ppi')
    if seuil:
        faibles = [i for i in dessins if i['ppi'] < seuil]
        for i in faibles[:15]:
            alerte(f'page {i["page"]} : image {i["l"]} × {i["h"]} px imprimée à {i["ppi"]:.0f} ppi, sous les {seuil} demandés')
        if len(faibles) > 15:
            alerte(f'… et {len(faibles) - 15} autres images sous {seuil} ppi')


def controler_surete(pdf, pages, surete):
    print(f'\nTEXTE À MOINS DE {mm(surete, 1)} MM DE LA COUPE')
    proches = []
    for p, liste in enumerate(mots(pdf), 1):
        z = pages[p]
        if z['rot']:
            print(f'  page {p} pivotée : non contrôlée')
            continue
        crop, coupe = z['CropBox'], z['TrimBox']
        # pdftotext compte depuis le coin haut gauche de la zone visible (CropBox)
        g, d, h, b = coupe[0] - crop[0], coupe[2] - crop[0], crop[3] - coupe[3], crop[3] - coupe[1]
        for x0, y0, x1, y1, mot in liste:
            ecarts = {'gauche': x0 - g, 'droit': d - x1, 'haut': y0 - h, 'bas': b - y1}
            cote = min(ecarts, key=ecarts.get)
            if ecarts[cote] < surete:
                proches.append((p, mot, ecarts[cote], cote))
    if not proches:
        print('  aucun mot (les mots dessinés en tracés ne sont pas vus)')
        return
    for p, mot, ecart, cote in proches[:20]:
        ou = 'au-delà de la coupe' if ecart < 0 else f'à {mm(ecart)} mm'
        alerte(f'page {p} : « {mot} » {ou}, bord {cote}')
    if len(proches) > 20:
        alerte(f'… et {len(proches) - 20} autres mots')
    print('  (la boîte d\'un mot inclut la hauteur de ligne de sa police : le dessin des lettres est un peu plus loin du bord)')


def comparer(pdf, ancien):
    print(f'\nCOMPARAISON AVEC {ancien}')
    textes = {f: lancer('pdftotext', f, '-').split('\f')[:nombre_de_pages(f)] for f in (ancien, pdf)}
    a, n = textes[ancien], textes[pdf]
    if len(a) != len(n):
        alerte(f'{len(a)} pages avant, {len(n)} maintenant')
    differentes = 0
    for p, (avant, apres) in enumerate(zip(a, n), 1):
        ma, mn = avant.split(), apres.split()
        if ma != mn:
            differentes += 1
            avant_apres = {'insert': lambda i0, i1, j0, j1: f'+ « {" ".join(mn[j0:j1])} »',
                           'delete': lambda i0, i1, j0, j1: f'− « {" ".join(ma[i0:i1])} »',
                           'replace': lambda i0, i1, j0, j1: f'« {" ".join(ma[i0:i1])} » → « {" ".join(mn[j0:j1])} »'}
            changes = [avant_apres[t](i0, i1, j0, j1)
                       for t, i0, i1, j0, j1 in difflib.SequenceMatcher(None, ma, mn).get_opcodes() if t != 'equal']
            print(f'  page {p} : {len(ma)} → {len(mn)} mots   ' + '  '.join(changes[:3])[:160])
    if not differentes:
        print(f'  mêmes mots sur les {min(len(a), len(n))} pages communes')
    elif len(a) == len(n):
        print('  (un changement voulu du texte apparaît aussi ici : à relire page par page)')


def main():
    parser = argparse.ArgumentParser(description='Vérifie qu\'un PDF est prêt à imprimer.')
    parser.add_argument('pdf')
    parser.add_argument('--format', type=format_, help='format fini attendu, ex. 63x88mm ou 20x16in')
    parser.add_argument('--debord', type=longueur, help='débord minimal demandé par l\'imprimeur, ex. 3mm')
    parser.add_argument('--surete', type=longueur, help='marge de sécurité : signale le texte plus près de la coupe')
    parser.add_argument('--resolution', type=int, help='résolution minimale des images, en ppi')
    parser.add_argument('--polices', help='polices attendues, séparées par des virgules (début du nom suffit)')
    parser.add_argument('--comparer', metavar='ANCIEN.pdf', help='version précédente du même fichier')
    args = parser.parse_args()
    manquants = [o for o in ('pdfinfo', 'pdffonts', 'pdfimages', 'pdftotext') if not shutil.which(o)]
    if manquants:
        sys.exit(f'Outils absents : {", ".join(manquants)} (paquet poppler-utils)')

    infos = lancer('pdfinfo', args.pdf)
    n = nombre_de_pages(args.pdf)
    version = re.search(r'^PDF version:\s+(.+)$', infos, re.M).group(1)
    norme = re.search(r'^PDF subtype:\s+(.+)$', infos, re.M)
    print(f'{args.pdf} : {n} page{"s" if n > 1 else ""}, PDF {version}, '
          + (f'se déclare {norme.group(1)}' if norme else 'ne se déclare pas PDF/X'))
    pages = zones(args.pdf)
    controler_zones(pages, args.format, args.debord)
    attendues = [re.sub(r'[\s_-]', '', a).lower() for a in args.polices.split(',')] if args.polices else None
    controler_polices(args.pdf, n, attendues)
    controler_images(args.pdf, args.resolution)
    if args.surete is not None:
        controler_surete(args.pdf, pages, args.surete)
    if args.comparer:
        comparer(args.pdf, args.comparer)
    if erreurs_de_lecture:
        print('\nSTRUCTURE DU FICHIER')
        alerte(f'poppler signale {len(erreurs_de_lecture)} erreur(s) en lisant le fichier : il est peut-être abîmé '
               '(copie incomplète, conversion ratée), et les résultats ci-dessus sont alors incomplets')
        for ligne in list(erreurs_de_lecture)[:5]:
            print(f'    {ligne}')

    print(f'\nBILAN : {len(alertes)} alerte{"s" if len(alertes) > 1 else ""}.' if alertes else '\nBILAN : aucune alerte.')
    print('Non vérifié ici : épaisseur des traits, couleurs des tracés et du texte (RVB ou CMJN), texte dessiné en '
          'tracés, rendu à l\'œil. Pour ça : une planche (planche.py) et les questions à l\'imprimeur.')
    sys.exit(1 if alertes else 0)


if __name__ == '__main__':
    main()
