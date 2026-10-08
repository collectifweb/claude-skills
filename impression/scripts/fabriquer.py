#!/usr/bin/env python3
"""Fait imprimer une page web en PDF par Chrome, au format exact, avec zone de coupe et zone de débord déclarées.

Usage :
  fabriquer.py page.html sortie.pdf --format 63x88mm --debord 3mm [--flux] [--chrome CHEMIN]

Deux façons d'écrire la page :
- pages fixes (cartes, plateau, boîte, affiche, faces d'un dépliant) : une <section class="page"> par page, et
  dedans une <div class="fini"> qui a exactement le format fini. Le fond de la section remplit le débord, et ce qui
  doit être coupé au ras du bord peut dépasser de .fini. Le script ajoute le style qui donne leur taille à ces deux
  boîtes : ne pas leur en donner une autre.
- --flux (livret, document long) : Chrome répartit lui-même le texte sur les pages. Le script fixe la taille de page
  (format fini plus débord) ; à la page de régler ses marges avec @page{margin:…}, débord compris.

Pourquoi ce détour (constaté avec Chrome 151, voir references/chrome-pdf.md) :
- Chrome arrondit le format de page. On imprime sur une page plus grande, puis on recadre au point près, à partir du
  coin haut gauche.
- Chrome cale chaque boîte sur un pixel CSS entier. Le format fini est donc posé à un nombre entier de pixels du
  bord, et le recadrage retire le surplus.
- Chrome coupe un texte centré par translateY(-50%) qui, avant ce décalage, dépasse le bas de la page, quand une
  autre page suit. La page imprimée a donc 60 mm de plus que nécessaire.

Demande pypdf (pip install pypdf) et un Chrome ou Chromium : --chrome, la variable CHROME, celui de Playwright
(~/.cache/ms-playwright) ou un chromium, google-chrome ou brave-browser du PATH.
"""
import argparse, math, os, shutil, subprocess, sys, tempfile
from pathlib import Path

from verifier import format_, longueur

try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import RectangleObject
except ImportError:
    sys.exit('pypdf est absent : pip install pypdf (de préférence dans un environnement virtuel)')

PX_PAR_PT = 4 / 3          # 1 px CSS = 0,75 pt
JEU_LARGEUR, JEU_HAUTEUR = 10, 60  # mm ajoutés à la page imprimée en mode pages fixes


def trouver_chrome(chemin):
    candidats = [chemin, os.environ.get('CHROME')]
    candidats += sorted(map(str, Path.home().glob('.cache/ms-playwright/chromium-*/chrome-linux*/chrome')), reverse=True)
    candidats += sorted(map(str, Path.home().glob('Library/Caches/ms-playwright/chromium-*/chrome-mac*/*.app/Contents/MacOS/*')), reverse=True)
    candidats += [shutil.which(n) for n in ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable', 'brave-browser')]
    trouve = next((c for c in candidats if c and Path(c).is_file()), None)
    if not trouve:
        sys.exit('Aucun Chrome trouvé : passer --chrome CHEMIN, ou définir la variable CHROME')
    return trouve


def style(largeur, hauteur, debord, flux):
    """Le style ajouté en tête de page, et le surplus à retirer en haut et à gauche au recadrage (en points)."""
    if flux:
        return f'@page{{size:{largeur + 2 * debord:.3f}pt {hauteur + 2 * debord:.3f}pt}}html,body{{margin:0}}', 0
    bord = math.ceil(debord * PX_PAR_PT - 1e-6)  # le débord arrondi au pixel entier supérieur
    return (f'@page{{size:{(largeur + 2 * bord * 0.75) / 72 * 25.4 + JEU_LARGEUR:.3f}mm '
            f'{(hauteur + 2 * bord * 0.75) / 72 * 25.4 + JEU_HAUTEUR:.3f}mm;margin:0}}'
            f'html,body{{margin:0}}'
            f'.page{{position:relative;overflow:hidden;break-after:page;'
            f'width:calc({largeur:.3f}pt + {2 * bord}px);height:calc({hauteur:.3f}pt + {2 * bord}px)}}'
            f'.page>.fini{{position:absolute;left:{bord}px;top:{bord}px;width:{largeur:.3f}pt;height:{hauteur:.3f}pt}}'
            ), bord * 0.75 - debord


def imprimer(html, chrome, css):
    """Copie la page avec le style en tête (et une base pour ses liens relatifs), puis la fait imprimer par Chrome."""
    source = Path(html).resolve()
    contenu = source.read_text()
    tete = f'<base href="{source.parent.as_uri()}/"><style>{css}</style>'
    contenu = contenu.replace('<head>', '<head>' + tete, 1) if '<head>' in contenu else tete + contenu
    dossier = Path(tempfile.mkdtemp())
    copie, brut = dossier / 'page.html', dossier / 'chrome.pdf'
    copie.write_text(contenu)
    subprocess.run([chrome, '--headless', '--disable-gpu', '--no-pdf-header-footer', '--allow-file-access-from-files',
                    '--virtual-time-budget=5000', f'--print-to-pdf={brut}', copie.as_uri()],
                   check=True, capture_output=True)
    return brut


def recadrer(brut, final, largeur, hauteur, debord, surplus):
    """Chaque page recadrée au point près depuis son coin haut gauche, avec zone de coupe et zone de débord."""
    l, h = largeur + 2 * debord, hauteur + 2 * debord
    ecrivain = PdfWriter()
    for page in PdfReader(brut).pages:
        gauche, haut = float(page.mediabox.left) + surplus, float(page.mediabox.top) - surplus
        page.mediabox = page.cropbox = page.bleedbox = RectangleObject([gauche, haut - h, gauche + l, haut])
        page.trimbox = RectangleObject([gauche + debord, haut - h + debord, gauche + l - debord, haut - debord])
        ecrivain.add_page(page)
    ecrivain.write(final)
    return len(ecrivain.pages)


def main():
    parser = argparse.ArgumentParser(description='Page web → PDF à imprimer, au format exact, par Chrome.')
    parser.add_argument('html')
    parser.add_argument('pdf')
    parser.add_argument('--format', type=format_, required=True, help='format fini, ex. 63x88mm ou 20x16in')
    parser.add_argument('--debord', type=longueur, required=True, help='débord de chaque côté, ex. 3mm ou 0.125in (0 : aucun)')
    parser.add_argument('--flux', action='store_true', help='texte réparti sur les pages par Chrome (livret)')
    parser.add_argument('--chrome', help='chemin du navigateur')
    args = parser.parse_args()
    (largeur, hauteur), debord = args.format, args.debord
    css, surplus = style(largeur, hauteur, debord, args.flux)
    brut = imprimer(args.html, trouver_chrome(args.chrome), css)
    n = recadrer(brut, args.pdf, largeur, hauteur, debord, surplus)
    shutil.rmtree(brut.parent)
    print(f'{args.pdf} : {n} page(s). Contrôle : verifier.py {args.pdf} --format … --debord …')


if __name__ == '__main__':
    main()
