#!/usr/bin/env python3
"""audit-secu : relevé des failles connues, des fins de support et des modèles d'IA
périmés dans chaque projet d'un dossier de travail.

Lecture seule : rien n'est modifié, installé ni commité dans les projets. Seuls des noms
de paquets et des numéros de version partent vers les bases publiques (npm, Packagist,
GitHub, OSV, WPVulnerability, endoflife.date), jamais de code.

Usage : audit.py [--base DIR] [--projet NOM ...] [--sortie DIR] [--lister]
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from pathlib import Path

POUBELLE = 'ZZ-POUBELLE'
# Dossiers jamais parcourus : dépendances installées, sorties de build, copies et sauvegardes.
ELAGUER = {
    'node_modules', 'vendor', '.git', 'dist', 'build', '.next', '.nuxt', '.output', '.svelte-kit',
    'storage', 'cache', '.cache', 'uploads', '.venv', 'venv', '__pycache__', 'coverage',
    'vendor-prefixed', '.claude', '.trash', 'trash', 'backup', 'backups', 'sauvegarde', 'sauvegardes', POUBELLE,
}
TABLE_MODELES = Path.home() / '.claude/skills/maj-modeles/model-map.json'
FICHIER_IGNORER = '.audit-secu-ignorer'
# Sélection faite sur le panneau d'audit (page claude.ai), écrite par le skill avant chaque passage
FICHIER_SELECTION = '.audit-secu-projets.json'
RAISONS = {'abandonne': 'abandonné', 'mandat': 'pas de mandat', 'autre-dev': 'autre développeur', 'suspendu': 'suspendu'}

GRAVITE = {'critical': 4, 'high': 3, 'moderate': 2, 'medium': 2, 'low': 1, 'info': 0,
           'c': 4, 'h': 3, 'm': 2, 'l': 1, 'n': 0}
NOM_GRAVITE = {4: 'critique', 3: 'élevée', 2: 'moyenne', 1: 'faible', 0: 'inconnue'}

# Paquets suivis par endoflife.date (nom du paquet -> produit).
PRODUITS_NPM = {'react': 'react', 'vue': 'vue', 'next': 'nextjs', 'nuxt': 'nuxt',
                '@angular/core': 'angular', 'express': 'express', 'jquery': 'jquery',
                'tailwindcss': 'tailwind-css'}
PRODUITS_COMPOSER = {'laravel/framework': 'laravel', 'symfony/http-kernel': 'symfony'}

EXT_MODELES = {'.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.vue', '.svelte', '.php', '.py',
               '.rb', '.go', '.json', '.yml', '.yaml', '.toml', '.ini', '.sh', '.env'}
RE_MODELE = re.compile(
    r'''(?:^|(?<=["'`=:/\s]))('''
    r'''claude-[a-z0-9][a-z0-9.\-]*[a-z0-9]|gpt-\d[a-z0-9.\-]*[a-z0-9]|gpt-\d'''
    r'''|gemini-\d[a-z0-9.\-]*[a-z0-9]|chatgpt-4o-latest|text-davinci-\d+|dall-e-[23])'''
    r'''(?=["'`\s,;)]|$)'''
    # Les modèles « o1 », « o3 »… ne comptent qu'entre guillemets : trop de faux positifs sinon.
    r'''|(?<=["'`])(o[134](?:-mini|-pro|-preview)?(?:-\d{4}-\d{2}-\d{2})?)(?=["'`])''', re.M)

_cache, _verrou = {}, threading.Lock()


def http_json(url):
    """GET JSON avec cache partagé entre les projets. Renvoie {'_erreur': ...} en cas d'échec."""
    with _verrou:
        if url in _cache:
            return _cache[url]
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'audit-secu/1.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            val = json.load(r)
    except urllib.error.HTTPError as e:
        val = {'_erreur': e.code}
    except Exception as e:  # réseau, JSON illisible
        val = {'_erreur': str(e)}
    with _verrou:
        _cache[url] = val
    return val


def lancer(cmd, cwd=None, timeout=180):
    env = dict(os.environ)
    if cmd[0] != 'gh':  # les outils de paquets n'ont pas à voir les jetons et les clés
        env = {k: v for k, v in env.items() if not re.search(r'TOKEN|SECRET|PASSWORD|_KEY', k, re.I)}
    env |= {'COMPOSER_NO_INTERACTION': '1', 'NO_COLOR': '1', 'COREPACK_ENABLE_STRICT': '0',
            'npm_config_manage_package_manager_versions': 'false'}
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -1, '', 'délai dépassé'
    except FileNotFoundError:
        return -1, '', f'{cmd[0]} absent de la machine'


@contextmanager
def copie(dossier, fichiers):
    """Les audits tournent sur une copie des seuls manifestes : aucune config ni crochet du projet n'est chargé."""
    with tempfile.TemporaryDirectory(prefix='audit-secu-') as tmp:
        for f in fichiers:
            if (dossier / f).is_file():
                shutil.copy2(dossier / f, tmp)
        yield Path(tmp)


def num(v):
    """'v6.4.1-beta' -> [6, 4, 1, 0] pour comparer des versions."""
    n = [int(x) for x in re.findall(r'\d+', str(v or ''))][:4]
    return n + [0] * (4 - len(n))


def majeure(v):
    n = num(v)
    return (0, n[1]) if n[0] == 0 else (n[0], 0)


def ghsa(texte):
    m = re.search(r'GHSA(?:-[0-9a-z]{4}){3}', str(texte or ''))
    return m.group(0) if m else None


def lire_json(chemin):
    try:
        return json.loads(Path(chemin).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def parcourir(racine, ignores):
    """Parcourt un projet en élaguant les dossiers inutiles. Renvoie (dossier, sous-dossiers, fichiers)."""
    for dp, dn, fn in os.walk(racine):
        dn[:] = [d for d in dn if d not in ELAGUER
                 and not any(os.path.join(dp, d) == i or os.path.join(dp, d).startswith(i + os.sep)
                             for i in ignores)]
        yield Path(dp), dn, fn


# --- Dépendances : npm, pnpm, composer --------------------------------------------------------

def audit_npm(dossier):
    lock = lire_json(dossier / 'package-lock.json')
    vues = {}
    for portee, extra in (('tout', []), ('prod', ['--omit=dev'])):
        with copie(dossier, ['package.json', 'package-lock.json']) as tmp:
            _, out, err = lancer(['npm', 'audit', '--json', '--package-lock-only', *extra], tmp)
        try:
            d = json.loads(out)
        except ValueError:
            return [], f'npm audit illisible ({err.strip()[:150]})'
        if 'error' in d:
            return [], f"npm audit : {d['error'].get('summary', d['error'])}"[:200]
        vues[portee] = d.get('vulnerabilities', {})
    failles = []
    for nom, v in vues['tout'].items():
        # toutes les copies installées, pas seulement la dernière lue
        version = ', '.join(sorted({lock.get('packages', {}).get(n, {}).get('version') for n in v.get('nodes', [])}
                                   - {None}, key=num)) or None
        # fixAvailable: true ne garantit pas que la branche installée ait un correctif : on ne le reprend pas
        npm_propose = v.get('fixAvailable')
        if isinstance(npm_propose, dict):
            npm_propose = f"npm propose {npm_propose.get('name')} {npm_propose.get('version')}" + \
                (' (version majeure)' if npm_propose.get('isSemVerMajor') else '')
        else:
            npm_propose = None
        for a in v.get('via', []):
            if not isinstance(a, dict):
                continue  # faille héritée : elle est comptée sur le paquet d'origine
            failles.append({
                'source': 'npm audit', 'ecosysteme': 'npm', 'paquet': nom, 'version': version,
                'gravite': a.get('severity'), 'titre': a.get('title'), 'id': ghsa(a.get('url')),
                'lien': a.get('url'), 'plage': a.get('range'), 'direct': v.get('isDirect'),
                'dev': nom not in vues['prod'],
                'correctif': ' · '.join(filter(None, [borne_npm(a.get('range')), npm_propose])) or None,
            })
    return failles, None


def borne_npm(plage):
    """'<7.1.6' -> '≥ 7.1.6' : première version hors de la plage vulnérable, lue dans l'avis lui-même."""
    bornes = re.findall(r'(?:^|\s)<([0-9][^\s|]*)', plage or '')
    return ' ou '.join(f'≥ {b}' for b in bornes) or None


def audit_pnpm(dossier):
    vues = {}
    for portee, extra in (('tout', []), ('prod', ['--prod'])):
        with copie(dossier, ['package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml']) as tmp:
            _, out, err = lancer(['pnpm', 'audit', '--json', *extra], tmp)
        try:
            vues[portee] = json.loads(out).get('advisories', {})
        except ValueError:
            return [], f'pnpm audit illisible ({err.strip()[:150]})'
    failles = []
    for cle, a in vues['tout'].items():
        failles.append({
            'source': 'pnpm audit', 'ecosysteme': 'npm', 'paquet': a.get('module_name'),
            'version': ', '.join(sorted({f.get('version', '') for f in a.get('findings', [])})),
            'gravite': a.get('severity'), 'titre': a.get('title'),
            'id': a.get('github_advisory_id') or ghsa(a.get('url')), 'lien': a.get('url'),
            'plage': a.get('vulnerable_versions'), 'dev': cle not in vues['prod'],
            'correctif': a.get('patched_versions'),
        })
    return failles, None


def _composer(dossier, *args):
    with copie(dossier, ['composer.json', 'composer.lock']) as tmp:
        _, out, err = lancer(['composer', *args, '--locked', '--format=json', '--no-plugins', '--no-scripts'], tmp)
    try:
        return json.loads(out), None
    except ValueError:
        return None, f"composer {args[0]} illisible ({err.strip()[:150]})"


def audit_composer(dossier):
    lock = lire_json(dossier / 'composer.lock')
    versions = {p['name']: p.get('version') for p in lock.get('packages', []) + lock.get('packages-dev', [])}
    tout, err = _composer(dossier, 'audit')
    if err:
        return [], [], err
    prod, _ = _composer(dossier, 'audit', '--no-dev')
    avis = tout.get('advisories') or {}
    avis_prod = (prod or {}).get('advisories') or {}
    failles = []
    for paquet, liste in (avis.items() if isinstance(avis, dict) else []):
        for a in liste:
            ids = [s.get('remoteId') for s in a.get('sources', [])]
            failles.append({
                'source': 'composer audit', 'ecosysteme': 'composer', 'paquet': paquet,
                'version': versions.get(paquet), 'gravite': a.get('severity'), 'titre': a.get('title'),
                'id': next((i for i in ids if ghsa(i)), None) or a.get('cve') or a.get('advisoryId'),
                'cve': a.get('cve'), 'lien': a.get('link'), 'plage': a.get('affectedVersions'),
                'dev': paquet not in avis_prod,
            })
    retards = []
    abandonnes = tout.get('abandoned') or {}
    for paquet, remplacant in (abandonnes.items() if isinstance(abandonnes, dict) else []):
        retards.append({'paquet': paquet, 'version': versions.get(paquet), 'abandonne': True,
                        'remplacant': remplacant or None})
    vieux, _ = _composer(dossier, 'outdated', '--direct', '--major-only')
    for p in (vieux or {}).get('locked', []):
        retards.append({'paquet': p['name'], 'version': p.get('version'), 'derniere': p.get('latest')})
    return failles, retards, None


def retards_npm(dossier):
    """Dépendances directes en retard d'au moins une version majeure."""
    pkg, lock = lire_json(dossier / 'package.json'), lire_json(dossier / 'package-lock.json')
    retards = []
    for nom in {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}:
        version = lock.get('packages', {}).get(f'node_modules/{nom}', {}).get('version')
        if not version:
            continue
        derniere = http_json(f'https://registry.npmjs.org/{nom}/latest').get('version')
        if derniere and majeure(version) < majeure(derniere):
            retards.append({'paquet': nom, 'version': version, 'derniere': derniere})
    return retards


def audit_python(fichier):
    """requirements.txt : seules les versions figées (==) peuvent être vérifiées."""
    paquets, non_figes = [], 0
    for ligne in fichier.read_text(encoding='utf-8', errors='replace').splitlines():
        ligne = ligne.split('#')[0].strip()
        if not ligne or ligne.startswith('-'):
            continue
        m = re.match(r'([A-Za-z0-9_.\-\[\]]+)\s*==\s*([\w.\-+]+)$', ligne)
        if m:
            paquets.append((re.sub(r'\[.*\]', '', m.group(1)), m.group(2)))
        else:
            non_figes += 1
    failles = []
    for nom, version in paquets:
        req = urllib.request.Request(
            'https://api.osv.dev/v1/query', method='POST',
            data=json.dumps({'package': {'name': nom, 'ecosystem': 'PyPI'}, 'version': version}).encode())
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                vulns = json.load(r).get('vulns', [])
        except Exception as e:
            return failles, non_figes, f'OSV injoignable ({e})'
        for v in vulns:
            gravite = (v.get('database_specific') or {}).get('severity', '')
            failles.append({
                'source': 'OSV', 'ecosysteme': 'pip', 'paquet': nom, 'version': version,
                'gravite': gravite.lower(), 'titre': v.get('summary') or v.get('id'),
                'id': next((a for a in v.get('aliases', []) if a.startswith('GHSA')), v.get('id')),
                'lien': f"https://osv.dev/vulnerability/{v.get('id')}",
            })
    return failles, non_figes, None


# --- GitHub ---------------------------------------------------------------------------------

def depot_github(projet):
    _, out, _ = lancer(['git', '-C', str(projet), 'remote', 'get-url', 'origin'])
    m = re.search(r'github\.com[:/](.+?)(?:\.git)?/?$', out.strip())
    return m.group(1) if m else None


def erreur_gh(out, err):
    m = re.search(r'"message"\s*:\s*"([^"]+)"', out + err)
    return f"erreur ({m.group(1) if m else (out or err).strip().splitlines()[-1][:150]})"


def audit_github(depot):
    res = {'depot': depot}
    code, out, err = lancer(['gh', 'api', '--paginate', '--jq', '.[] | tojson',
                             f'repos/{depot}/dependabot/alerts?state=open&per_page=100'])
    failles = []
    if code:
        res['dependabot'] = 'désactivé' if 'disabled' in (out + err) else erreur_gh(out, err)
    else:
        res['dependabot'] = 'actif'
        for ligne in out.splitlines():
            a = json.loads(ligne)
            dep, avis, vuln = a['dependency'], a['security_advisory'], a['security_vulnerability']
            failles.append({
                'source': 'Dependabot', 'ecosysteme': dep['package']['ecosystem'],
                'paquet': dep['package']['name'], 'gravite': avis.get('severity'),
                'titre': avis.get('summary'), 'id': avis.get('ghsa_id'), 'cve': avis.get('cve_id'),
                'lien': a.get('html_url'), 'plage': vuln.get('vulnerable_version_range'),
                'correctif': (vuln.get('first_patched_version') or {}).get('identifier'),
                'fichier': dep.get('manifest_path'), 'dev': dep.get('scope') == 'development',
            })
    for cle, chemin in (('analyse_code', 'code-scanning'), ('secrets', 'secret-scanning')):
        code, out, err = lancer(['gh', 'api', '--paginate', '--jq', '.[] | tojson',
                                 f'repos/{depot}/{chemin}/alerts?state=open&per_page=100'])
        if code:
            res[cle] = 'non activé' if re.search(r'not enabled|disabled|no analysis', out + err, re.I) \
                else erreur_gh(out, err)
        else:
            alertes = [json.loads(x) for x in out.splitlines()]
            res[cle] = len(alertes)
            for a in alertes:
                regle = a.get('rule') or {}
                failles.append({
                    'source': f'GitHub {chemin}', 'ecosysteme': 'code',
                    'paquet': a.get('secret_type_display_name') or regle.get('id'),
                    'gravite': regle.get('security_severity_level') or regle.get('severity') or 'high',
                    'titre': regle.get('description') or a.get('secret_type_display_name'),
                    'id': f"{chemin}#{a.get('number')}", 'lien': a.get('html_url'),
                    'fichier': ((a.get('most_recent_instance') or {}).get('location') or {}).get('path'),
                })
    return res, failles


# --- WordPress ------------------------------------------------------------------------------

def entete(fichier, champ):
    try:
        with open(fichier, encoding='utf-8', errors='replace') as f:
            texte = f.read(8192)
    except OSError:
        return None
    m = re.search(rf'^[\s*#@/]*{champ}\s*:\s*(.+)$', texte, re.M | re.I)
    return m.group(1).strip() if m else None


def composants_wp(wp_content):
    """[(type, slug, version)] des extensions et thèmes d'un wp-content."""
    res = []
    plugins = wp_content / 'plugins'
    for e in sorted(plugins.iterdir()) if plugins.is_dir() else []:
        if e.is_dir():
            principal = next((f for f in sorted(e.glob('*.php')) if entete(f, 'Plugin Name')), None)
            if principal:
                res.append(('plugin', e.name, entete(principal, 'Version')))
        elif e.suffix == '.php' and entete(e, 'Plugin Name'):
            res.append(('plugin', e.stem, entete(e, 'Version')))
    themes = wp_content / 'themes'
    for e in sorted(themes.iterdir()) if themes.is_dir() else []:
        if (e / 'style.css').is_file():
            res.append(('theme', e.name, entete(e / 'style.css', 'Version')))
    return res


def s_applique(version, op):
    if not op:
        return True
    v = num(version)

    def test(o, ref):
        if not o or not ref:
            return True
        r = num(ref)
        return {'lt': v < r, 'le': v <= r, 'gt': v > r, 'ge': v >= r, 'eq': v == r}.get(o, True)
    return test(op.get('min_operator'), op.get('min_version')) and \
        test(op.get('max_operator'), op.get('max_version'))


def resume_vulns(vulns, version):
    """Résumé des failles WPVulnerability qui touchent une version."""
    touchees = [v for v in vulns if version and s_applique(version, v.get('operator'))]
    if not touchees:
        return None
    graves = [GRAVITE.get(((v.get('impact') or {}).get('cvss') or {}).get('severity', ''), 0) for v in touchees]
    corrige = [v['operator']['max_version'] for v in touchees
               if (v.get('operator') or {}).get('max_operator') == 'lt' and v['operator'].get('max_version')]
    ids = [s['id'] for v in touchees for s in v.get('source', []) if s.get('id', '').startswith('CVE')]
    return {
        'nombre': len(touchees), 'gravite_max': max(graves),
        'par_gravite': {NOM_GRAVITE[g]: graves.count(g) for g in sorted(set(graves), reverse=True)},
        'sans_correctif': sum(1 for v in touchees if (v.get('operator') or {}).get('unfixed') == '1'),
        'corrige_en': max(corrige, key=num) if corrige else None,
        'cve': sorted(set(ids))[:10],
    }


def audit_wordpress(racine, wp_content):
    inst = {'chemin': str(racine), 'coeur': None, 'composants': [], 'inconnus': [], 'fermes': []}
    version_php = racine / 'wp-includes' / 'version.php'
    if version_php.is_file():
        m = re.search(r"\$wp_version\s*=\s*'([^']+)'", version_php.read_text(errors='replace'))
        if m:
            d = http_json(f'https://www.wpvulnerability.net/core/{m.group(1)}/')
            inst['coeur'] = {'version': m.group(1),
                             'failles': resume_vulns((d.get('data') or {}).get('vulnerability') or [], m.group(1))}
    tiers = set()
    for genre, slug, version in composants_wp(wp_content):
        d = (http_json(f'https://www.wpvulnerability.net/{genre}/{urllib.parse.quote(slug)}/').get('data') or {})
        if not d.get('name'):
            inst['inconnus'].append(f'{genre}:{slug}')
            continue
        tiers.add(wp_content / ('plugins' if genre == 'plugin' else 'themes') / slug)
        if d.get('closed'):
            inst['fermes'].append({'slug': slug, 'raison': d.get('closed_reason')})
        failles = resume_vulns(d.get('vulnerability') or [], version)
        if failles or not version:
            inst['composants'].append({'type': genre, 'slug': slug, 'version': version, 'failles': failles})
    return inst, tiers


# --- Fins de support ------------------------------------------------------------------------

def fin_support(produit, version):
    d = http_json(f'https://endoflife.date/api/v1/products/{produit}/')
    versions = (d.get('result') or {}).get('releases') or []
    n = num(version)
    for cycle in (f'{n[0]}.{n[1]}', f'{n[0]}'):
        r = next((r for r in versions if r.get('name') == cycle), None)
        if r:
            return {'produit': produit, 'version': version, 'cycle': cycle, 'fin_depassee': r.get('isEol'),
                    'fin_le': r.get('eolFrom'), 'derniere_du_cycle': (r.get('latest') or {}).get('name'),
                    'dernier_cycle': versions[0].get('name') if versions else None}
    return None


# --- Modèles d'IA ---------------------------------------------------------------------------

def charger_table():
    t = lire_json(TABLE_MODELES)
    garder, remplacer = set(), {}
    for fournisseur in ('anthropic', 'openai', 'gemini'):
        garder |= set(t.get(fournisseur, {}).get('garder', []))
        remplacer |= t.get(fournisseur, {}).get('remplacer', {})
    return garder, remplacer, t.get('_maj')


def modeles(projet, exclus, ignores, table):
    garder, remplacer, _ = table
    trouves = []
    for dp, dn, fn in parcourir(projet, ignores):
        dn[:] = [d for d in dn if dp / d not in exclus and d != 'docs']  # docs : notes et données, pas du code
        for f in fn:
            chemin = dp / f
            ext = '.env' if f.startswith('.env') else chemin.suffix
            if ext not in EXT_MODELES or f.endswith(('.min.js', '-lock.json', '.lock')) or f == 'package.json':
                continue
            try:
                if chemin.stat().st_size > 512_000:
                    continue
                texte = chemin.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            for m in RE_MODELE.finditer(texte):
                ident = m.group(1) or m.group(2)
                if ident in garder or ident.startswith('claude-code'):
                    continue
                if re.fullmatch(r'o\d', ident):  # « o1 » nu : retenu seulement si la ligne parle de modèle
                    debut = texte.rfind('\n', 0, m.start()) + 1
                    if 'model' not in texte[debut:texte.find('\n', m.end()) % (len(texte) + 1)].lower():
                        continue
                trouves.append({
                    'fichier': str(chemin.relative_to(projet)), 'ligne': texte.count('\n', 0, m.start()) + 1,
                    'identifiant': ident, 'statut': 'ancien selon la table' if ident in remplacer else 'hors table',
                    'cible': remplacer.get(ident),
                })
    return trouves


# --- Un projet ------------------------------------------------------------------------------

def auditer(projet, ignores, table):
    r = {'projet': projet.name, 'chemin': str(projet), 'technos': set(), 'failles': [], 'retards': [],
         'fins_support': [], 'wordpress': [], 'modeles': [], 'angles_morts': [], 'github': None}
    tiers_wp = set()
    verrous = {}  # dossier -> fichiers présents
    for dp, dn, fn in parcourir(projet, ignores):
        if 'wp-content' in dn:
            wp = dp / 'wp-content'
            inst, tiers = audit_wordpress(dp, wp)
            r['wordpress'].append(inst)
            r['technos'].add('WordPress')
            tiers_wp |= tiers
            if inst['coeur']:
                fs = fin_support('wordpress', inst['coeur']['version'])
                if fs:
                    r['fins_support'].append(fs | {'fichier': str(dp.relative_to(projet))})
            dn.remove('wp-content')
        presents = set(fn) & {'package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock',
                              'composer.json', 'composer.lock', 'requirements.txt', 'pyproject.toml',
                              '.nvmrc', '.node-version', 'artisan'}
        if presents:
            verrous[dp] = presents

    for dossier, presents in sorted(verrous.items()):
        rel = str(dossier.relative_to(projet)) or '.'
        parents_verrouilles = any(dossier != d and dossier.is_relative_to(d) and
                                  {'package-lock.json', 'pnpm-lock.yaml'} & p for d, p in verrous.items())

        def ajouter(failles, erreur):
            for f in failles:
                f.setdefault('fichier', rel)
            r['failles'].extend(failles)
            if erreur:
                r['angles_morts'].append(f'{rel} : {erreur}')

        if 'package-lock.json' in presents:
            r['technos'].add('Node')
            ajouter(*audit_npm(dossier))
            r['retards'] += [x | {'fichier': rel} for x in retards_npm(dossier)]
        elif 'pnpm-lock.yaml' in presents:
            r['technos'].add('Node')
            ajouter(*audit_pnpm(dossier))
        elif 'yarn.lock' in presents:
            r['angles_morts'].append(f'{rel} : yarn.lock non analysé (yarn absent de la machine)')
        elif 'package.json' in presents and not parents_verrouilles:
            r['angles_morts'].append(f'{rel} : package.json sans fichier de verrouillage, versions non figées')

        if 'composer.lock' in presents:
            r['technos'].add('PHP')
            failles, retards, erreur = audit_composer(dossier)
            ajouter(failles, erreur)
            r['retards'] += [x | {'fichier': rel} for x in retards]
        elif 'composer.json' in presents:
            r['angles_morts'].append(f'{rel} : composer.json sans composer.lock, versions non figées')

        if 'requirements.txt' in presents:
            r['technos'].add('Python')
            failles, non_figes, erreur = audit_python(dossier / 'requirements.txt')
            ajouter(failles, erreur)
            if non_figes:
                r['angles_morts'].append(f'{rel}/requirements.txt : {non_figes} paquet(s) sans version figée')
        elif 'pyproject.toml' in presents:
            r['technos'].add('Python')
            r['angles_morts'].append(f'{rel} : pyproject.toml sans fichier de verrouillage lisible, non analysé')

        if 'artisan' in presents:
            r['technos'].add('Laravel')
        # Fins de support des cadres détectés.
        lock = lire_json(dossier / 'package-lock.json')
        for nom, produit in PRODUITS_NPM.items():
            v = lock.get('packages', {}).get(f'node_modules/{nom}', {}).get('version')
            if v and (fs := fin_support(produit, v)):
                r['fins_support'].append(fs | {'fichier': rel})
        clock = lire_json(dossier / 'composer.lock')
        for p in clock.get('packages', []):
            if p['name'] in PRODUITS_COMPOSER and (fs := fin_support(PRODUITS_COMPOSER[p['name']], p['version'])):
                r['fins_support'].append(fs | {'fichier': rel})
        php = lire_json(dossier / 'composer.json').get('config', {}).get('platform', {}).get('php')
        if php and (fs := fin_support('php', php)):
            r['fins_support'].append(fs | {'fichier': rel, 'note': 'version déclarée dans composer.json'})
        for f in ('.nvmrc', '.node-version'):
            if f in presents:
                v = (dossier / f).read_text(errors='replace').strip().lstrip('v')
                if re.match(r'\d', v) and (fs := fin_support('nodejs', v)):
                    r['fins_support'].append(fs | {'fichier': f'{rel}/{f}'})

    depot = depot_github(projet)
    ecartees = 0
    if depot:
        r['github'], failles = audit_github(depot)
        # Même règle que pour l'audit local : les dépendances internes aux extensions tierces sont écartées.
        tiers = [str(t.relative_to(projet)) + '/' for t in tiers_wp]
        gardees = [f for f in failles if not any((f.get('fichier') or '').startswith(t) for t in tiers)]
        ecartees = len(failles) - len(gardees)
        r['failles'] += gardees
        if r['github']['dependabot'] != 'actif':
            r['angles_morts'].append(f"alertes Dependabot de {depot} : {r['github']['dependabot']}")
    elif (projet / '.git').exists():
        r['angles_morts'].append('dépôt git sans dépôt GitHub : pas d\'alertes GitHub')
    else:
        r['angles_morts'].append('pas de dépôt git : pas d\'alertes GitHub')
    if r['wordpress']:
        r['angles_morts'].append('fichiers de dépendances internes aux extensions et thèmes WordPress tiers ignorés'
                                 + (f' ({ecartees} alertes Dependabot écartées)' if ecartees else '')
                                 + ' : ils relèvent de leurs auteurs, les extensions sont vérifiées par leur version')

    r['modeles'] = modeles(projet, tiers_wp, ignores, table)
    r['failles'] = fusionner(r['failles'])
    r['technos'] = sorted(r['technos'])
    return r


def fusionner(failles):
    """Une même faille vue par npm audit et Dependabot ne compte qu'une fois, avec ses deux sources."""
    groupes = {}
    for f in failles:
        cle = ((f.get('paquet') or '').lower(), f.get('id') or f.get('titre'))
        g = groupes.setdefault(cle, {**f, 'sources': [], 'fichiers': []})
        g['sources'] = sorted(set(g['sources']) | {f['source']})
        g['fichiers'] = sorted(set(g['fichiers']) | {f.get('fichier') or '.'})
        if GRAVITE.get(str(f.get('gravite')).lower(), 0) > GRAVITE.get(str(g.get('gravite')).lower(), 0):
            g['gravite'] = f.get('gravite')
        g['dev'] = bool(g.get('dev')) and bool(f.get('dev'))
        for champ in ('version', 'cve'):
            g[champ] = g.get(champ) or f.get(champ)
        # une faille sur deux branches a deux correctifs (≥ 1.1.16 ou ≥ 5.0.7) : garder les deux
        c = f.get('correctif')
        if c and c.lstrip('≥ ') not in (g.get('correctif') or ''):
            g['correctif'] = f"{g['correctif']} ou {c}" if g.get('correctif') else c
        if f.get('plage') and f['plage'] not in (g.get('plage') or ''):
            g['plage'] = f"{g['plage']} ; {f['plage']}" if g.get('plage') else f['plage']
    res = []
    for g in groupes.values():
        g.pop('source', None)
        g.pop('fichier', None)
        g['niveau'] = GRAVITE.get(str(g.get('gravite')).lower(), 0)
        g['gravite'] = NOM_GRAVITE[g['niveau']]
        res.append(g)
    return sorted(res, key=lambda g: (-g['niveau'], g['dev'], g.get('paquet') or ''))


# --- Rapport --------------------------------------------------------------------------------

PASTILLE = {4: '🔴', 3: '🟠', 2: '🟡', 1: '⚪', 0: '⚪'}


def score(p):
    n = [0] * 5
    for f in p['failles']:
        n[f['niveau']] += 1
    for inst in p['wordpress']:
        for c in [inst['coeur'] or {}] + inst['composants']:
            if (c or {}).get('failles'):
                n[c['failles']['gravite_max']] += 1
    return n


def rapport_md(res, table_maj):
    lignes = [f"# Relevé brut audit-secu — {res['date']}", '',
              "Constats de l'outil, **non triés** : une faille listée ici n'est pas forcément exploitable.",
              "Sources : copie locale (npm, composer, WordPress, modèles d'IA) et GitHub (branche poussée).",
              "**La production n'est pas couverte** : une copie locale peut différer du site en ligne.", '',
              *([f"Exclus par la sélection ({len(res['exclus'])}) : " + ', '.join(
                  f"{n} ({RAISONS.get(r, r)})" if r else n for n, r in sorted(res['exclus'].items())), '']
                if res.get('exclus') else []),
              f"Table des modèles d'IA : `/maj-modeles`, mise à jour {table_maj or 'inconnue'}.", '',
              '## Vue d\'ensemble', '',
              '| Projet | 🔴 | 🟠 | 🟡 | ⚪ | Fin de support | Modèles | Angles morts |',
              '|---|---|---|---|---|---|---|---|']
    projets = sorted(res['projets'], key=lambda p: [-x for x in reversed(score(p))])
    calmes = []
    for p in projets:
        n = score(p)
        eol = sum(1 for f in p['fins_support'] if f.get('fin_depassee'))
        if not any(n[1:]) and not eol and not p['modeles'] and not p['retards']:
            calmes.append(p)
            continue
        lignes.append(f"| {p['projet']} | {n[4]} | {n[3]} | {n[2]} | {n[1]} | {eol} | {len(p['modeles'])} "
                      f"| {len(p['angles_morts'])} |")
    for p in projets:
        if p in calmes:
            continue
        lignes += ['', f"## {p['projet']}", '', f"Technologies : {', '.join(p['technos']) or '—'}"]
        if p['failles']:
            lignes += ['', '### Failles des dépendances', '']
            for f in p['failles'][:20]:
                lignes.append(
                    f"- {PASTILLE[f['niveau']]} {f['gravite']} · {f['ecosysteme']} · `{f['paquet']}` "
                    f"{f.get('version') or ''}{' · **devDependencies seulement**' if f['dev'] else ''} · {f.get('titre') or ''} "
                    f"· {f.get('id') or ''} · corrigé : {f.get('correctif') or '?'} · {', '.join(f['sources'])} "
                    f"· {', '.join(f['fichiers'])}")
            if len(p['failles']) > 20:
                lignes.append(f"- … et {len(p['failles']) - 20} autres (voir brut.json)")
        for inst in p['wordpress']:
            lignes += ['', f"### WordPress — copie locale `{Path(inst['chemin']).relative_to(p['chemin']) or '.'}`", '']
            c = inst['coeur']
            if c:
                f = c['failles']
                lignes.append(f"- Cœur {c['version']} : " + (
                    f"{f['nombre']} failles connues ({', '.join(f'{v} {k}' for k, v in f['par_gravite'].items())})"
                    if f else 'aucune faille connue'))
            else:
                lignes.append('- Cœur absent de la copie : version non vérifiable')
            for comp in sorted(inst['composants'], key=lambda c: -((c['failles'] or {}).get('gravite_max', -1))):
                f = comp['failles']
                if not f:
                    lignes.append(f"- {comp['type']} `{comp['slug']}` : version illisible, non vérifiable")
                    continue
                lignes.append(
                    f"- {PASTILLE[f['gravite_max']]} {comp['type']} `{comp['slug']}` {comp['version']} : "
                    f"{f['nombre']} faille(s), pire {NOM_GRAVITE[f['gravite_max']]}, corrigé en ≥ {f['corrige_en'] or '?'}"
                    + (f", {f['sans_correctif']} sans correctif" if f['sans_correctif'] else ''))
            for fe in inst['fermes']:
                lignes.append(f"- ⚠️ `{fe['slug']}` retiré de wordpress.org ({fe['raison'] or 'raison non donnée'})")
            if inst['inconnus']:
                lignes.append(f"- Inconnus de la base (maison ou payants) : {', '.join(inst['inconnus'])}")
        eols = [f for f in p['fins_support'] if f.get('fin_depassee') or
                (f.get('fin_le') and f['fin_le'] <= (dt.date.today() + dt.timedelta(days=180)).isoformat())]
        if eols:
            lignes += ['', '### Fins de support', '']
            for f in eols:
                etat = 'support terminé' if f['fin_depassee'] else f"fin du support le {f['fin_le']}"
                lignes.append(f"- {f['produit']} {f['version']} (cycle {f['cycle']}) : {etat} · dernier cycle "
                              f"{f['dernier_cycle']} · {f['fichier']}")
        if p['retards']:
            lignes += ['', '### En retard d\'une version majeure ou abandonnés', '']
            for x in p['retards']:
                lignes.append(f"- `{x['paquet']}` {x.get('version') or ''} → " + (
                    f"abandonné, remplaçant : {x.get('remplacant') or 'aucun'}" if x.get('abandonne')
                    else x.get('derniere', '')) + f" · {x['fichier']}")
        if p['modeles']:
            lignes += ['', '### Modèles d\'IA', '']
            for m in p['modeles']:
                lignes.append(f"- `{m['identifiant']}` · {m['statut']}"
                              + (f" → `{m['cible']}`" if m['cible'] else '') + f" · {m['fichier']}:{m['ligne']}")
        if p['angles_morts']:
            lignes += ['', '### Angles morts', ''] + [f'- {a}' for a in p['angles_morts']]
    if calmes:
        lignes += ['', '## Sans constat', '',
                   ', '.join(f"{p['projet']}{' (' + str(len(p['angles_morts'])) + ' angle(s) mort(s))' if p['angles_morts'] else ''}"
                             for p in calmes)]
    return '\n'.join(lignes) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--base', default=str(Path.home() / 'Apps-coding'))
    ap.add_argument('--projet', action='append', help='limiter à ce projet (répétable)')
    ap.add_argument('--sortie', help='dossier du rapport (défaut : <base>/.audit-secu-rapports/<date>)')
    ap.add_argument('--lister', action='store_true', help='afficher les projets en JSON, sans rien scanner')
    a = ap.parse_args()
    base = Path(a.base).resolve()
    ignores = []
    if (base / FICHIER_IGNORER).is_file():
        for ligne in (base / FICHIER_IGNORER).read_text().splitlines():
            if ligne.strip() and not ligne.startswith('#'):
                ignores.append(str(base / ligne.strip().rstrip('/')))
    tous = [d for d in sorted(base.iterdir())
            if d.is_dir() and not d.name.startswith('.') and d.name != POUBELLE and str(d) not in ignores]
    if a.lister:
        print(json.dumps([d.name for d in tous], ensure_ascii=False))
        return
    # un projet nommé avec --projet passe même s'il est exclu par la sélection
    exclus = {}
    if not a.projet and (base / FICHIER_SELECTION).is_file():
        exclus = json.loads((base / FICHIER_SELECTION).read_text()).get('exclus', {})
    projets = [d for d in tous if (d.name in a.projet if a.projet else d.name not in exclus)]
    if exclus:
        print(f'{len(exclus)} projet(s) exclu(s) par la sélection : {", ".join(sorted(exclus))}', file=sys.stderr)
    if a.projet and len(projets) != len(set(a.projet)):
        sys.exit(f"Projet introuvable parmi : {', '.join(a.projet)}")
    table = charger_table()
    maintenant = dt.datetime.now()
    sortie = Path(a.sortie) if a.sortie else base / '.audit-secu-rapports' / maintenant.strftime('%Y-%m-%d')
    sortie.mkdir(parents=True, exist_ok=True)

    resultats = []
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        futurs = {pool.submit(auditer, p, ignores, table): p for p in projets}
        for i, fut in enumerate(cf.as_completed(futurs), 1):
            p = futurs[fut]
            try:
                resultats.append(fut.result())
            except Exception as e:  # un projet en échec ne bloque pas les autres
                resultats.append({'projet': p.name, 'chemin': str(p), 'technos': [], 'failles': [], 'retards': [],
                                  'fins_support': [], 'wordpress': [], 'modeles': [], 'github': None,
                                  'angles_morts': [f'audit interrompu : {type(e).__name__}: {e}']})
            print(f'[{i}/{len(projets)}] {p.name}', file=sys.stderr)

    res = {'date': maintenant.strftime('%Y-%m-%d %H:%M'), 'base': str(base), 'ignores': ignores, 'exclus': exclus,
           'table_modeles': table[2], 'projets': sorted(resultats, key=lambda r: r['projet'])}
    (sortie / 'brut.json').write_text(json.dumps(res, ensure_ascii=False, indent=1))
    (sortie / 'rapport-brut.md').write_text(rapport_md(res, table[2]))
    ecrire_extraits(res, sortie)
    print(sortie)


def ecrire_extraits(res, sortie):
    """Un fichier par projet à trier (étape 3 du skill), et les modèles d'IA à classer (étape 2)."""
    extraits = sortie / 'extraits'
    extraits.mkdir(exist_ok=True)
    lots, modeles_ia = {'complet': [], 'dev_seulement': []}, []
    for p in res['projets']:
        modeles_ia += [m | {'projet': p['projet'], 'chemin': p['chemin']} for m in p['modeles']]
        # gravité inconnue = non cotée par la source, pas « faible » : elle part au tri
        failles = [f for f in p['failles'] if f['niveau'] >= 2 or (f['niveau'] == 0 and not f['dev'])]
        wp = [c | {'installation': i['chemin']} for i in p['wordpress']
              for c in ([i['coeur'] | {'type': 'core', 'slug': 'wordpress'}] if i['coeur'] else []) + i['composants']
              if (c['failles'] or {}).get('gravite_max', 0) >= 3]
        if not failles and not wp:
            continue
        lots['complet' if wp or any(not f['dev'] for f in failles) else 'dev_seulement'].append(p['projet'])
        (extraits / f"{p['projet']}.json").write_text(json.dumps(
            {'projet': p['projet'], 'chemin': p['chemin'], 'failles': failles, 'wordpress': wp},
            ensure_ascii=False, indent=1))
    (extraits / '_modeles.json').write_text(json.dumps(modeles_ia, ensure_ascii=False, indent=1))
    (sortie / 'a-trier.json').write_text(json.dumps(lots, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
