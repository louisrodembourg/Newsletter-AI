#!/usr/bin/env python3
"""
Mémoire de la newsletter, dérivée des éditions archivées.

    python3 scripts/registry.py            # résumé à lire avant de rédiger
    python3 scripts/registry.py --acteurs  # seulement la carte des acteurs

Rien n'est maintenu à la main : tout est recalculé depuis `editions/*.md`, donc
le registre ne peut pas se désynchroniser des éditions réellement publiées.

À lancer au début de chaque édition. Il répond à trois questions que le
rédacteur ne peut pas trancher de mémoire :
  - quels acteurs ont déjà eu leur fiche (ne pas les refaire) ;
  - quelles sources sont sur-utilisées (aller en chercher d'autres) ;
  - quels sujets sont chauds en ce moment (assurer le suivi, pas la répétition).
"""

import argparse
import glob
import os
import re
from collections import Counter, defaultdict
from urllib.parse import urlparse


def charger():
    editions = {}
    for f in sorted(glob.glob("editions/*.md")):
        jour = os.path.basename(f).replace(".md", "")
        editions[jour] = open(f, encoding="utf-8").read()
    return editions


def rubriques_de(texte):
    out, courante = defaultdict(list), None
    for bloc in re.split(r"\n\s*\n", texte):
        bloc = bloc.strip()
        if bloc.startswith("## "):
            courante = bloc[3:].strip()
        elif courante and bloc and bloc != "---":
            out[courante].append(bloc)
    return out


def acteurs(editions):
    """Nom d'entreprise = ce qui précède le tiret dans le titre de fiche."""
    vus = {}
    for jour, texte in editions.items():
        for nom_rub, blocs in rubriques_de(texte).items():
            if "acteur" not in nom_rub.lower():
                continue
            for b in blocs:
                titre = b.split("\n")[0].strip("*").strip()
                nom = re.split(r"\s[—–-]\s", titre)[0].strip()
                if nom:
                    vus[nom] = jour
    return vus


def sources(editions):
    par_jour, total = {}, Counter()
    for jour, texte in editions.items():
        doms = [urlparse(u).netloc.replace("www.", "")
                for u in re.findall(r"\]\((https?://[^)]+)\)", texte)]
        par_jour[jour] = Counter(doms)
        total.update(doms)
    return par_jour, total


def sujets_recents(editions, n=3):
    """Titres d'items des n dernières éditions, pour le suivi et l'anti-doublon."""
    out = []
    for jour in sorted(editions)[-n:]:
        for nom_rub, blocs in rubriques_de(editions[jour]).items():
            if "brief" in nom_rub.lower():
                continue
            for b in blocs:
                if b.startswith("**"):
                    out.append((jour, nom_rub, b.split("\n")[0].strip("*")))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--acteurs", action="store_true")
    args = ap.parse_args()

    ed = charger()
    if not ed:
        print("Aucune édition archivée pour l'instant.")
        return

    vus = acteurs(ed)
    print("=" * 68)
    print(f"MÉMOIRE — {len(ed)} éditions, du {min(ed)} au {max(ed)}")
    print("=" * 68)

    print(f"\n🏢 ACTEURS DÉJÀ TRAITÉS ({len(vus)}) — ne pas refaire leur fiche")
    if vus:
        for nom, jour in sorted(vus.items(), key=lambda x: x[1], reverse=True):
            print(f"   {jour}  {nom}")
    else:
        print("   (aucun — la rubrique est récente)")

    if args.acteurs:
        return

    par_jour, total = sources(ed)
    print(f"\n📰 SOURCES — {len(total)} domaines utilisés au total")
    print("   Les plus sollicités (à délaisser au profit d'autres) :")
    for d, c in total.most_common(6):
        print(f"      {c}x  {d}")

    try:
        import yaml
        cat = yaml.safe_load(open("config/sources.yaml", encoding="utf-8"))
        tous = {s["domain"] for v in cat.values() for s in v
                if not s.get("crawler_blocked")}
        jamais = sorted(tous - set(total))
        print(f"\n   Jamais utilisés, pourtant au catalogue ({len(jamais)}/"
              f"{len(tous)}) — piocher ici en priorité :")
        for i in range(0, min(len(jamais), 21), 3):
            print("      " + "  ".join(f"{d:<26}" for d in jamais[i:i+3]))
    except Exception as e:
        print(f"   (catalogue illisible : {e})")

    recents = sujets_recents(ed)
    print(f"\n🔁 SUJETS DES 3 DERNIÈRES ÉDITIONS ({len(recents)}) — "
          "suivre leur évolution, ne pas les répéter")
    for jour, rub, titre in recents:
        print(f"   {jour} [{rub[:22]:<22}] {titre[:52]}")

    print("\n" + "=" * 68)
    print("Rappel : une fiche d'acteur déjà publiée ne se refait pas, un sujet")
    print("déjà traité ne revient que s'il a RÉELLEMENT évolué — et alors on")
    print("l'écrit comme une suite, pas comme une nouvelle.")
    print("=" * 68)


if __name__ == "__main__":
    main()
