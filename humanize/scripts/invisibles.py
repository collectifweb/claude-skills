#!/usr/bin/env python3
"""Passe anti-filigrane : retire les caractères invisibles d'un texte.

    invisibles.py [FICHIER]      (sans fichier : lit l'entrée standard)

Texte nettoyé sur la sortie standard, rapport sur la sortie d'erreur.
Ne modifie jamais le fichier source.

Conservés exprès : l'espace insécable (U+00A0) et l'espace fine insécable (U+202F)
de la typographie française, et les liants d'émojis (U+200D, U+FE0F) collés à un émoji.
"""
import sys
import unicodedata
from collections import Counter

RETIRER = {
    0x200B: "espace sans chasse",
    0x200C: "antiliant sans chasse",
    0x200D: "liant sans chasse",
    0xFEFF: "indicateur d'ordre des octets (BOM)",
    0x2060: "gluon de mots",
    0x00AD: "trait d'union conditionnel",
    0x034F: "gluon de graphèmes",
    0x061C: "marque de lettre arabe",
    0x180E: "séparateur de voyelles mongol",
    0x17B4: "voyelle inhérente khmère",
    0x17B5: "voyelle inhérente khmère",
    0x115F: "remplissage hangûl",
    0x1160: "remplissage hangûl",
    0x3164: "remplissage hangûl",
    0xFFA0: "remplissage hangûl",
    0x2800: "motif braille vide",
    0x200E: "marque de direction",
    0x200F: "marque de direction",
}
for c in range(0x2061, 0x2065):
    RETIRER[c] = "opérateur mathématique invisible"
for c in [*range(0x202A, 0x202F), *range(0x2066, 0x206A)]:
    RETIRER[c] = "commande de direction du texte"
for c in range(0x206A, 0x2070):
    RETIRER[c] = "commande de mise en forme obsolète"
for c in range(0xFE00, 0xFE10):
    RETIRER[c] = "sélecteur de variante"
for c in range(0xE0100, 0xE01F0):
    RETIRER[c] = "sélecteur de variante"
for c in range(0xE0000, 0xE0080):
    RETIRER[c] = "caractère d'étiquette"

# Ils séparent des mots : les supprimer collerait les mots entre eux.
EN_ESPACE = {c: "espace typographique" for c in [*range(0x2000, 0x200B), 0x205F, 0x3000]}
EN_LIGNE = {0x2028: "séparateur de ligne", 0x2029: "séparateur de paragraphe"}

TIRETS = {0x2014: "—", 0x2E3A: "⸺", 0x2E3B: "⸻"}


def colle_a_un_emoji(texte, i):
    voisins = texte[i - 1:i] + texte[i + 1:i + 2]
    return any(unicodedata.category(v) in ("So", "Sk", "Me") for v in voisins)


def nettoyer(texte):
    sortie, retires = [], Counter()
    for i, car in enumerate(texte):
        c = ord(car)
        if c in (0x200D, 0xFE0F) and colle_a_un_emoji(texte, i):
            sortie.append(car)
        elif c in RETIRER:
            retires[(c, RETIRER[c])] += 1
        elif c in EN_ESPACE:
            retires[(c, EN_ESPACE[c] + " → espace normale")] += 1
            sortie.append(" ")
        elif c in EN_LIGNE:
            retires[(c, EN_LIGNE[c] + " → saut de ligne")] += 1
            sortie.append("\n")
        else:
            sortie.append(car)
    return "".join(sortie), retires


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            texte = f.read()
    else:
        texte = sys.stdin.read()

    propre, retires = nettoyer(texte)
    sys.stdout.write(propre)

    if retires:
        print(f"Caractères invisibles retirés : {sum(retires.values())}", file=sys.stderr)
        for (c, nom), n in sorted(retires.items()):
            print(f"  U+{c:04X}  {nom}  ×{n}", file=sys.stderr)
    else:
        print("Aucun caractère invisible.", file=sys.stderr)

    tirets = Counter(car for car in propre if ord(car) in TIRETS)
    if tirets:
        detail = ", ".join(f"{car} ×{n}" for car, n in tirets.items())
        print(f"Tirets cadratins encore présents (à réécrire) : {detail}", file=sys.stderr)


if __name__ == "__main__":
    main()
