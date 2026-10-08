# impression

A skill for **Claude Code and Codex CLI** that prepares and checks files meant for a print shop: board games (board,
cards, box), booklets, leaflets, posters. Written in French.

It complements a visual design skill such as impeccable rather than replacing it: the design skill judges how things
look, `impression` takes care of what makes a file printable.

## Why

A file can look right on screen and still be wrong for print: the trim size is off by a fraction of a millimetre, no
bleed is declared, a font was silently swapped for Times New Roman, a transparency was rasterized, a line of text
went missing between two versions. None of this shows up until the proofs come back.

Print "rules" also travel without sources. This skill keeps every figure tied to an authoritative source (the PDF
specification, ISO 15930, Ghent Workgroup specifications, the ICC registry, Adobe documentation) or marks it as
something to confirm with the printer. Printer spec sheets (Panda, LongPack, Efko, The Game Crafter…) are quoted as
examples of what each one asks for, never as norms. They disagree with each other, which is the point.

## How it works

1. **Before designing**: pick the product sheet (board, cards, booklet, box, leaflet, poster), get the printer's
   values (or provisional ones, flagged as such), and write the frame into the project: trim size, bleed, safe margin.
2. **While building**: when the PDF comes from an HTML page printed by Chrome, `scripts/fabriquer.py` prints it on an
   oversized page, crops it to the exact size and declares the TrimBox and BleedBox. The reference sheet
   `chrome-pdf.md` documents eight Chrome pitfalls, each reproduced with Chrome 151 and paired with a check and a fix.
3. **Before sending**: `scripts/verifier.py` reports page boxes, fonts, images and their effective resolution, words
   closer to the trim than the safe margin, files that poppler cannot read cleanly, and with `--comparer`, which
   words changed on which page between two versions. `scripts/planche.py` builds side-by-side contact sheets
   (before/after, trim vs bleed, or a magnified detail). A checklist and a list of questions for the printer close
   the loop.

## Files

```
SKILL.md                    the workflow and the pre-flight checklist
references/notions.md       bleed, trim, safe margin, fonts, resolution, line and text minimums, colour, PDF/X, with sources
references/supports.md      one sheet per product: board, cards, booklet, box, leaflet, poster
references/chrome-pdf.md    HTML → PDF with Chrome: pitfalls, checks, fixes
references/imprimeur.md     questions for the printer and a spec sheet template
scripts/verifier.py         PDF report
scripts/planche.py          contact sheet
scripts/fabriquer.py        HTML → print-ready PDF through Chrome
```

## Requirements

- **Claude Code** or **Codex CLI**
- **Python 3** and **poppler-utils** (`pdfinfo`, `pdffonts`, `pdfimages`, `pdftotext`, `pdftoppm`)
- **ImageMagick** (`montage`) for contact sheets
- For `fabriquer.py` only: **pypdf** (`pip install pypdf`) and a Chrome or Chromium (the one Playwright installs works)

## Installation

**Linux / macOS**

```bash
git clone https://github.com/collectifweb/claude-skills.git
ln -s "$(pwd)/claude-skills/impression" ~/.claude/skills/impression
ln -s "$(pwd)/claude-skills/impression" ~/.codex/skills/impression   # Codex CLI
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\impression" -Target "$PWD\claude-skills\impression"
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.codex\skills\impression" -Target "$PWD\claude-skills\impression"
```

## License

MIT
