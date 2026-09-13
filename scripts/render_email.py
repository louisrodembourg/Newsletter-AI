#!/usr/bin/env python3
"""
Convertit une édition Markdown de `editions/` en HTML email-safe.

Usage :
    python3 scripts/render_email.py editions/2026-09-13.md > /tmp/edition.html
    python3 scripts/render_email.py editions/2026-09-13.md --out edition.html

La structure attendue est celle imposée par `prompts/daily-brief.md` :
front-matter YAML, puis des sections `## <emoji> <titre>` contenant des items
de la forme `**Titre**\nCorps avec [source](url)`.

Aucune dépendance externe : le HTML produit doit rester lisible dans Gmail,
donc tables + CSS inline uniquement.
"""

import argparse
import html
import re
import sys
from pathlib import Path

# --- Palette (miroir de templates/email.html) ------------------------------
ENCRE = "#14161a"
TEXTE = "#2b2f36"
GRIS = "#8a8f98"
GRIS_CLAIR = "#9aa0a8"
GRIS_PIED = "#6b7079"
LIEN = "#0b63c5"
BORDURE = "#e6e6e2"
OR = "#c9a227"

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def parse_front_matter(texte):
    """Extrait le front-matter YAML sans dépendre de PyYAML."""
    meta = {}
    if not texte.startswith("---"):
        return meta, texte
    fin = texte.find("\n---", 3)
    if fin == -1:
        return meta, texte
    for ligne in texte[3:fin].strip().splitlines():
        if ":" in ligne:
            cle, _, val = ligne.partition(":")
            meta[cle.strip()] = val.strip().strip('"').strip("'")
    return meta, texte[fin + 4:]


def inline(texte):
    """Applique les conversions inline : liens, gras, italique."""
    texte = html.escape(texte, quote=False)

    def lien(m):
        libelle, url = m.group(1), m.group(2)
        libelle = libelle.replace("→", "&rarr;").replace("&amp;rarr;", "&rarr;")
        return (f'<a href="{html.escape(url, quote=True)}" '
                f'style="color:{LIEN};text-decoration:none;font-weight:600;">{libelle}</a>')

    texte = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lien, texte)
    texte = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", texte)
    texte = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)",
                   rf'<em style="color:{GRIS_PIED};">\1</em>', texte)
    return texte.replace(" · ", " &nbsp;·&nbsp; ")


def decouper_sections(corps):
    """Retourne [(titre_section, [blocs])] en suivant les `##`."""
    sections, courante = [], None
    for bloc in re.split(r"\n\s*\n", corps):
        bloc = bloc.strip()
        if not bloc or bloc == "---":
            continue
        if bloc.startswith("## "):
            courante = (bloc[3:].strip(), [])
            sections.append(courante)
        elif bloc.startswith("# "):
            if courante is not None:
                courante[1].append(bloc)
        elif courante is not None:
            courante[1].append(bloc)
    return sections


def rendre_brief(blocs):
    puces = []
    for bloc in blocs:
        for ligne in bloc.splitlines():
            ligne = ligne.strip()
            if ligne.startswith("- "):
                puces.append(
                    f'<li style="margin-bottom:7px;">{inline(ligne[2:])}</li>')
    if not puces:
        return ""
    return f"""
        <tr>
          <td style="padding:26px 32px 6px 32px;">
            <p style="margin:0 0 14px 0;font-size:15px;font-weight:700;color:{ENCRE};">&#9889; Le brief</p>
            <ul style="margin:0;padding:0 0 0 18px;color:{TEXTE};font-size:14.5px;line-height:1.65;">
              {''.join(puces)}
            </ul>
          </td>
        </tr>
        <tr><td style="padding:22px 32px 0 32px;"><div style="border-top:1px solid {BORDURE};"></div></td></tr>"""


def rendre_item(bloc):
    lignes = bloc.split("\n", 1)
    titre = lignes[0].strip()
    corps = lignes[1].strip() if len(lignes) > 1 else ""
    sortie = ""
    if titre.startswith("**") and titre.endswith("**"):
        sortie += (f'<p style="margin:0 0 5px 0;font-size:14.5px;font-weight:650;'
                   f'color:{ENCRE};line-height:1.4;">{inline(titre[2:-2])}</p>')
    else:
        corps = bloc.strip()
    if corps:
        sortie += (f'<p style="margin:0 0 18px 0;font-size:14px;line-height:1.65;'
                   f'color:{TEXTE};">{inline(corps)}</p>')
    return sortie


def rendre_section(titre, blocs):
    sous_titre = ""
    if " — " in titre:
        titre, _, sous_titre = titre.partition(" — ")
    items = "".join(rendre_item(b) for b in blocs)
    bloc_sous_titre = (f'<p style="margin:0 0 16px 0;font-size:12px;color:{GRIS_CLAIR};">'
                       f'{inline(sous_titre)}</p>' if sous_titre
                       else '<div style="height:12px;"></div>')
    return f"""
        <tr>
          <td style="padding:24px 32px 0 32px;">
            <p style="margin:0 0 4px 0;font-size:15px;font-weight:700;color:{ENCRE};">{inline(titre)}</p>
            {bloc_sous_titre}
            {items}
          </td>
        </tr>"""


def rendre_signal(blocs):
    corps = "".join(
        f'<p style="margin:0 0 10px 0;font-size:14px;line-height:1.65;color:{TEXTE};">'
        f'{inline(b)}</p>' for b in blocs)
    return f"""
        <tr>
          <td style="padding:14px 32px 0 32px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background-color:#f7f5ef;border-left:3px solid {OR};border-radius:0 6px 6px 0;">
              <tr>
                <td style="padding:16px 18px;">
                  <p style="margin:0 0 6px 0;font-size:13px;font-weight:700;color:{ENCRE};">&#128064; Signal faible</p>
                  {corps}
                </td>
              </tr>
            </table>
          </td>
        </tr>"""


def rendre_chiffre(blocs):
    chiffre, contexte = "", []
    for bloc in blocs:
        if bloc.startswith("# "):
            chiffre = bloc[2:].strip()
        else:
            contexte.append(inline(bloc))
    corps = " ".join(contexte)
    return f"""
        <tr>
          <td style="padding:18px 32px 6px 32px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background-color:{ENCRE};border-radius:6px;">
              <tr>
                <td style="padding:20px;" align="center">
                  <p style="margin:0 0 4px 0;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:{GRIS};font-weight:600;">&#128202; Le chiffre du jour</p>
                  <p style="margin:0 0 8px 0;font-size:34px;font-weight:700;color:#ffffff;line-height:1.1;">{html.escape(chiffre)}</p>
                  <p style="margin:0;font-size:13.5px;line-height:1.6;color:#c3c7cd;">{corps}</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""


def date_longue(iso):
    import datetime
    try:
        d = datetime.date.fromisoformat(iso)
    except ValueError:
        return iso
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month - 1]} {d.year}"


def rendre(chemin):
    meta, corps = parse_front_matter(Path(chemin).read_text(encoding="utf-8"))
    corps = re.sub(r"^# .*$", "", corps, count=1, flags=re.MULTILINE)

    sections = decouper_sections(corps)
    morceaux = []
    for titre, blocs in sections:
        if "brief" in titre.lower():
            morceaux.append(rendre_brief(blocs))
        elif "signal faible" in titre.lower():
            morceaux.append(rendre_signal(blocs))
        elif "chiffre du jour" in titre.lower():
            morceaux.append(rendre_chiffre(blocs))
        else:
            morceaux.append(rendre_section(titre, blocs))

    accroche = html.escape(meta.get("accroche", "Édition du jour"))
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f4f2;margin:0;padding:24px 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <tr>
    <td align="center">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:100%;background-color:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <tr>
          <td style="background-color:{ENCRE};padding:28px 32px 24px 32px;">
            <p style="margin:0 0 6px 0;font-size:11px;letter-spacing:2.5px;text-transform:uppercase;color:{GRIS};font-weight:600;">Signal IA</p>
            <h1 style="margin:0 0 10px 0;font-size:25px;line-height:1.25;color:#ffffff;font-weight:700;">{accroche}</h1>
            <p style="margin:0;font-size:13px;color:{GRIS};">{date_longue(meta.get('date', ''))} &nbsp;&middot;&nbsp; {html.escape(meta.get('temps_lecture', '7 min'))} de lecture</p>
          </td>
        </tr>
        {''.join(morceaux)}
        <tr>
          <td style="background-color:#fafaf8;padding:22px 32px;border-top:1px solid {BORDURE};">
            <p style="margin:0 0 6px 0;font-size:12px;line-height:1.6;color:{GRIS_PIED};">
              {html.escape(meta.get('sources_consultees', '?'))} sources consultées ce matin. Chaque information est
              recoupée avant publication ; les incertitudes sont signalées en italique.
            </p>
            <p style="margin:0;font-size:12px;color:{GRIS_CLAIR};">Signal IA — édition quotidienne générée par Claude Code.</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("edition", help="chemin du fichier Markdown de l'édition")
    ap.add_argument("--out", help="fichier de sortie (défaut : stdout)")
    args = ap.parse_args()

    if not Path(args.edition).is_file():
        sys.exit(f"Introuvable : {args.edition}")

    sortie = rendre(args.edition)
    if args.out:
        Path(args.out).write_text(sortie, encoding="utf-8")
        print(f"Écrit : {args.out} ({len(sortie)} octets)", file=sys.stderr)
    else:
        print(sortie)


if __name__ == "__main__":
    main()
