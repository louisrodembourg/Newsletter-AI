#!/usr/bin/env python3
"""
Contrôle qualité d'une édition avant envoi.

    python3 scripts/check_edition.py editions/2026-09-16.md

Sort en code 1 si une règle BLOQUANTE est violée : l'édition ne doit alors pas
partir en l'état. Les AVERTISSEMENTS n'empêchent pas l'envoi mais signalent une
dérive à corriger tant que c'est facile.

Les règles encodées ici sont celles de `config/editorial.md`. Ce script existe
parce que trois éditions écrites « en suivant les règles » les ont enfreintes
sans que personne ne s'en aperçoive : items sans source, même domaine cité
trois fois, sujet déjà traité l'avant-veille.
"""

import argparse
import glob
import os
import re
import sys
from collections import Counter
from datetime import date, timedelta
from urllib.parse import urlparse

RUBRIQUES_ATTENDUES = [
    "Le brief", "Tech & recherche", "Infra, cloud & outillage",
    "Les acteurs", "Produits & adoption", "Éco & investissement",
    "Signal faible", "Le chiffre du jour",
]
MOTS_MIN, MOTS_MAX = 1100, 1900
ITEMS_MIN, ITEMS_MAX = 10, 20
MAX_ITEMS_PAR_DOMAINE = 2
JOURS_ANTI_DOUBLON = 7

# Marqueurs d'une puce ou d'un item à dominante technique.
LEXIQUE_TECH = [
    "modèle", "benchmark", "paramètres", "contexte", "token", "open-weight",
    "poids ouverts", "licence", "architecture", "entraînement", "inférence",
    "gpu", "puce", "datacenter", "cloud", "serving", "agent", "api", "moe",
    "latence", "papers", "recherche", "score", "mixture", "quantization",
    "fine-tuning", "rag", "embedding", "multimodal", "compute",
]

MOTS_VIDES = set("""le la les un une des du de et ou à au aux en dans sur pour par
avec sans sous vers chez que qui quoi dont où son sa ses leur leurs ce cet cette
ces il elle ils elles on nous vous se est sont a ont été être avoir plus moins
très bien tout tous toute toutes son the a of to in for and""".split())


class Rapport:
    def __init__(self):
        self.erreurs, self.avertissements, self.ok = [], [], []

    def erreur(self, m): self.erreurs.append(m)
    def avertir(self, m): self.avertissements.append(m)
    def valide(self, m): self.ok.append(m)

    def afficher(self, chemin):
        print(f"\n\033[1mContrôle qualité — {chemin}\033[0m")
        print("─" * 68)
        for m in self.ok: print(f"  \033[32m✓\033[0m {m}")
        for m in self.avertissements: print(f"  \033[33m!\033[0m {m}")
        for m in self.erreurs: print(f"  \033[31m✗\033[0m {m}")
        print("─" * 68)
        if self.erreurs:
            print(f"\033[31m{len(self.erreurs)} règle(s) bloquante(s) violée(s) — "
                  f"ne pas envoyer cette édition.\033[0m\n")
        elif self.avertissements:
            print(f"\033[33mAucun blocage, {len(self.avertissements)} point(s) "
                  f"de vigilance.\033[0m\n")
        else:
            print("\033[32mÉdition conforme.\033[0m\n")


def decouper(texte):
    """Retourne (front_matter, {rubrique: [blocs]}) ."""
    meta = {}
    if texte.startswith("---"):
        fin = texte.find("\n---", 3)
        for ligne in texte[3:fin].strip().splitlines():
            if ":" in ligne:
                k, _, v = ligne.partition(":")
                meta[k.strip()] = v.strip().strip('"').strip("'")
        texte = texte[fin + 4:]
    rubriques, courante = {}, None
    for bloc in re.split(r"\n\s*\n", texte):
        bloc = bloc.strip()
        if not bloc or bloc == "---":
            continue
        if bloc.startswith("## "):
            courante = bloc[3:].strip()
            rubriques[courante] = []
        elif courante:
            rubriques[courante].append(bloc)
    return meta, rubriques


def items_de(rubriques):
    """Items rédactionnels : titre en gras + corps."""
    out = []
    for nom, blocs in rubriques.items():
        if "brief" in nom.lower():
            continue
        for b in blocs:
            if b.startswith("**") and "\n" in b:
                out.append((nom, b))
            elif b.startswith("**") and ("signal" in nom.lower() or "chiffre" in nom.lower()):
                out.append((nom, b))
    return out


def mots_signifiants(texte):
    mots = re.findall(r"[A-Za-zÀ-ÿ0-9.-]{3,}", texte.lower())
    return {m for m in mots if m not in MOTS_VIDES}


def controler(chemin, rapport):
    texte = open(chemin, encoding="utf-8").read()
    meta, rubriques = decouper(texte)

    # ---- Structure ------------------------------------------------------
    manquantes = [r for r in RUBRIQUES_ATTENDUES
                  if not any(r.lower() in nom.lower() for nom in rubriques)]
    if manquantes:
        rapport.erreur(f"Rubriques manquantes : {', '.join(manquantes)}")
    else:
        rapport.valide(f"Les {len(RUBRIQUES_ATTENDUES)} rubriques sont présentes")

    for champ in ("date", "accroche", "temps_lecture"):
        if champ not in meta:
            rapport.erreur(f"Front-matter : champ « {champ} » absent")

    # ---- Volume ---------------------------------------------------------
    nb_mots = len(re.sub(r"[#*\[\]()]", " ", texte).split())
    items = items_de(rubriques)
    if not (MOTS_MIN <= nb_mots <= MOTS_MAX):
        rapport.avertir(f"Volume hors cible : {nb_mots} mots "
                        f"(visé {MOTS_MIN}-{MOTS_MAX})")
    else:
        rapport.valide(f"Volume : {nb_mots} mots")
    if not (ITEMS_MIN <= len(items) <= ITEMS_MAX):
        rapport.avertir(f"Nombre d'items hors cible : {len(items)} "
                        f"(visé {ITEMS_MIN}-{ITEMS_MAX})")
    else:
        rapport.valide(f"{len(items)} items")

    # ---- Sourçage -------------------------------------------------------
    sans_source = [b.split("\n")[0].strip("*")[:52] for _, b in items
                   if "](http" not in b]
    if sans_source:
        rapport.erreur(f"{len(sans_source)} item(s) sans lien source : "
                       + " | ".join(sans_source))
    else:
        rapport.valide("Chaque item porte un lien source")

    urls = re.findall(r"\]\((https?://[^)]+)\)", texte)
    doublons = [u for u, c in Counter(urls).items() if c > 1]
    if doublons:
        rapport.erreur(f"{len(doublons)} URL citée(s) deux fois : "
                       + " | ".join(u[:56] for u in doublons))
    else:
        rapport.valide(f"{len(urls)} liens, tous distincts")

    # ---- Diversité des sources -----------------------------------------
    domaines = Counter(urlparse(u).netloc.replace("www.", "") for u in urls)
    trop = {d: c for d, c in domaines.items() if c > MAX_ITEMS_PAR_DOMAINE}
    if trop:
        rapport.erreur("Sur-concentration des sources (max "
                       f"{MAX_ITEMS_PAR_DOMAINE}/édition) : "
                       + ", ".join(f"{d} ×{c}" for d, c in trop.items()))
    else:
        rapport.valide(f"{len(domaines)} domaines distincts, aucun sur-cité")

    # ---- Le brief -------------------------------------------------------
    brief = next((b for n, b in rubriques.items() if "brief" in n.lower()), [])
    puces = [l.strip()[2:] for bloc in brief for l in bloc.splitlines()
             if l.strip().startswith("- ")]
    if len(puces) != 5:
        rapport.avertir(f"Le brief compte {len(puces)} puces au lieu de 5")
    techniques = [p for p in puces
                  if any(m in p.lower() for m in LEXIQUE_TECH)]
    if len(techniques) < 2:
        rapport.erreur(f"Le brief ne contient que {len(techniques)} puce(s) "
                       "technique(s) — le minimum est 2")
    else:
        rapport.valide(f"Brief : {len(techniques)}/{len(puces)} puces techniques")

    # ---- Redondance interne : le chiffre du jour --------------------
    chiffre_bloc = next((b for n, b in rubriques.items()
                         if "chiffre" in n.lower()), [])
    chiffre = next((b[2:].strip() for b in chiffre_bloc
                    if b.startswith("# ")), None)
    if chiffre:
        noyau = re.sub(r"[^\d,.]", "", chiffre)
        if noyau and any(noyau in p for p in puces):
            rapport.erreur(f"Le chiffre du jour ({chiffre}) figure déjà dans "
                           "le brief — choisir un angle non déjà couvert")
        else:
            rapport.valide(f"Chiffre du jour distinct du brief : {chiffre}")
    else:
        rapport.erreur("Aucun chiffre du jour (ligne « # <valeur> » attendue)")

    # ---- Redondance avec les éditions récentes -------------------------
    ce_jour = os.path.basename(chemin).replace(".md", "")
    try:
        d0 = date.fromisoformat(ce_jour)
        recentes = [f for f in sorted(glob.glob("editions/*.md"))
                    if f != chemin and (d0 - date.fromisoformat(
                        os.path.basename(f).replace(".md", ""))).days
                    <= JOURS_ANTI_DOUBLON]
    except ValueError:
        recentes = []

    titres_passes = []
    for f in recentes:
        t = open(f, encoding="utf-8").read()
        for b in re.split(r"\n\s*\n", t):
            b = b.strip()
            if b.startswith("**") and "\n" in b:
                titres_passes.append(
                    (os.path.basename(f)[:10], b.split("\n")[0].strip("*")))

    for _, bloc in items:
        titre = bloc.split("\n")[0].strip("*")
        mots_a = mots_signifiants(titre)
        for jour, ancien in titres_passes:
            mots_b = mots_signifiants(ancien)
            if not mots_a or not mots_b:
                continue
            j = len(mots_a & mots_b) / len(mots_a | mots_b)
            if j >= 0.45:
                rapport.avertir(
                    f"Sujet proche du {jour} ({int(j*100)} % de recouvrement) : "
                    f"« {titre[:46]} » ≈ « {ancien[:46]} »")
                break
    if recentes:
        rapport.valide(f"Comparaison faite avec {len(recentes)} édition(s) "
                       f"des {JOURS_ANTI_DOUBLON} derniers jours")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("edition")
    ap.add_argument("--strict", action="store_true",
                    help="traiter les avertissements comme bloquants")
    args = ap.parse_args()

    if not os.path.isfile(args.edition):
        sys.exit(f"Introuvable : {args.edition}")

    rapport = Rapport()
    controler(args.edition, rapport)
    rapport.afficher(args.edition)

    if rapport.erreurs or (args.strict and rapport.avertissements):
        sys.exit(1)


if __name__ == "__main__":
    main()
