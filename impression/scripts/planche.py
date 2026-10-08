#!/usr/bin/env python3
"""Planche de comparaison : les pages d'un ou plusieurs PDF côte à côte, chacune étiquetée.

Usage :
  planche.py avant.pdf après.pdf -o planche.jpg [--etiquettes "V1,V2"] [--pages 1-12,20]
             [--vue coupe|debord|page[,…]] [--dpi 60] [--colonnes 6] [--zone X,Y,L,H]

- Pour chaque page, une case par fichier et par vue, dans cet ordre : la même page de chaque version se suit.
- --vue : coupe montre le format fini (zone de coupe), debord la zone de débord, page la page entière.
  Avec un seul PDF et --vue coupe,debord, on voit d'un coup ce que la coupe retirera.
- --zone X,Y,L,H : un gros plan, en mm depuis le coin haut gauche du format fini, par exemple 100,50,60,40 avec
  --dpi 200 pour comparer des traits fins.

Demande poppler-utils (pdfinfo, pdftoppm) et ImageMagick (montage).
"""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

from verifier import nombre_de_pages, zones

POINTS_PAR_MM = 72 / 25.4
BOITE = {'coupe': 'TrimBox', 'debord': 'BleedBox', 'page': 'MediaBox'}


def liste_de_pages(texte, n):
    """'1-3,7' → [1, 2, 3, 7]"""
    pages = []
    for morceau in texte.split(','):
        debut, _, fin = morceau.partition('-')
        pages += range(int(debut), int(fin or debut) + 1)
    return [p for p in pages if 1 <= p <= n]


def rectangle(z, vue, zone):
    """Le rectangle à rendre, en points depuis le coin haut gauche de la page (MediaBox), comme l'attend pdftoppm."""
    media = z['MediaBox']
    if zone:
        x, y, l, h = (v * POINTS_PAR_MM for v in zone)
        coupe = z['TrimBox']
        return coupe[0] - media[0] + x, media[3] - coupe[3] + y, l, h
    b = z[BOITE[vue]]
    return b[0] - media[0], media[3] - b[3], b[2] - b[0], b[3] - b[1]


def rendre(pdf, page, rect, dpi, sortie):
    x, y, l, h = (round(v * dpi / 72) for v in rect)
    subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-r', str(dpi), '-x', str(x), '-y', str(y),
                    '-W', str(l), '-H', str(h), '-png', '-singlefile', pdf, str(sortie.with_suffix(''))],
                   check=True, capture_output=True)
    return sortie


def main():
    parser = argparse.ArgumentParser(description='Planche de comparaison de PDF, page à page.')
    parser.add_argument('pdf', nargs='+')
    parser.add_argument('-o', '--sortie', required=True, help='image à produire (.jpg ou .png)')
    parser.add_argument('--etiquettes', help='un nom par PDF, séparés par des virgules (par défaut : le nom du fichier)')
    parser.add_argument('--pages', help='ex. 1-12,20 (par défaut : toutes)')
    parser.add_argument('--vue', default='coupe', help='coupe, debord ou page, ou plusieurs séparées par des virgules')
    parser.add_argument('--dpi', type=int, default=60)
    parser.add_argument('--colonnes', type=int)
    parser.add_argument('--zone', help='gros plan X,Y,L,H en mm depuis le coin haut gauche du format fini')
    args = parser.parse_args()
    manquants = [o for o in ('pdfinfo', 'pdftoppm', 'montage') if not shutil.which(o)]
    if manquants:
        sys.exit(f'Outils absents : {", ".join(manquants)} (paquets poppler-utils et imagemagick)')
    vues = args.vue.split(',')
    if any(v not in BOITE for v in vues):
        sys.exit('--vue : coupe, debord ou page')
    zone = [float(v.replace(',', '.')) for v in args.zone.split(',')] if args.zone else None
    if zone and len(zone) != 4:
        sys.exit('--zone : quatre valeurs X,Y,L,H en mm')
    noms = args.etiquettes.split(',') if args.etiquettes else [Path(p).stem for p in args.pdf]
    if len(noms) != len(args.pdf):
        sys.exit('--etiquettes : un nom par PDF')

    toutes = {pdf: zones(pdf) for pdf in args.pdf}
    if zone:
        for pdf, pages_du_pdf in toutes.items():
            x0, y0, x1, y1 = pages_du_pdf[1]['TrimBox']
            l, h = (x1 - x0) / POINTS_PAR_MM, (y1 - y0) / POINTS_PAR_MM
            if zone[0] + zone[2] > l + 0.01 or zone[1] + zone[3] > h + 0.01:
                sys.exit(f'--zone sort du format fini de {pdf} ({l:.1f} × {h:.1f} mm)')
    n = max(nombre_de_pages(pdf) for pdf in args.pdf)
    pages = liste_de_pages(args.pages, n) if args.pages else list(range(1, n + 1))
    groupe = len(args.pdf) * (1 if zone else len(vues))
    colonnes = args.colonnes or groupe * max(1, 6 // groupe)

    with tempfile.TemporaryDirectory() as dossier:
        cases = []
        for p in pages:
            for pdf, nom in zip(args.pdf, noms):
                for vue in ([None] if zone else vues):
                    etiquette = f'{nom} p.{p}' + (f' ({vue})' if len(vues) > 1 and not zone else '')
                    if p not in toutes[pdf]:
                        cases += ['-label', f'{etiquette} : absente', 'xc:#bbbbbb']
                        continue
                    image = rendre(pdf, p, rectangle(toutes[pdf][p], vue, zone), args.dpi,
                                   Path(dossier) / f'{len(cases):05d}.png')
                    cases += ['-label', etiquette, str(image)]
        # une case absente prend la taille de la première image rendue
        taille = next((c for c in cases if c.endswith('.png')), None)
        if taille:
            l, h = subprocess.run(['identify', '-format', '%w %h', taille], capture_output=True, text=True).stdout.split()
            cases = [f'xc:#bbbbbb[{l}x{h}!]' if c == 'xc:#bbbbbb' else c for c in cases]
        colonnes = min(colonnes, len(cases) // 3)
        subprocess.run(['montage', *cases, '-tile', f'{colonnes}x', '-geometry', '+6+6', '-background', '#8a8a8a',
                        '-pointsize', '13', '-fill', '#111111', '-quality', '88', args.sortie], check=True)
    print(f'{args.sortie} : {len(pages)} page(s), {len(cases) // 3} case(s), {colonnes} par ligne')


if __name__ == '__main__':
    main()
