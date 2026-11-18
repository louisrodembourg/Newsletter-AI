# Exploitation — Signal IA

Notes d'exploitation de la routine quotidienne (déplacées depuis l'ancien README).

## Organisation du dépôt

```
config/
  editorial.md      Ligne éditoriale : rubriques, périmètre, règles de rédaction
  sources.yaml      49 sources de référence, notées par niveau de confiance
  delivery.md       Destinataire, horaire, comportement en cas de panne
prompts/
  daily-brief.md    Le prompt exécuté chaque matin par la routine
templates/
  email.html        Gabarit email de référence (tables, CSS inline)
scripts/
  registry.py       Mémoire : acteurs déjà traités, sources sur-utilisées, sujets récents
  check_edition.py  Contrôle qualité bloquant, à passer avant tout envoi
  render_email.py   Markdown d'édition → HTML email-safe
editions/
  AAAA-MM-JJ.md     Archive de chaque édition
```

## Fonctionnement quotidien

1. Une **Routine** planifiée réveille une session Claude Code fraîche.
2. La session lit `prompts/daily-brief.md` et charge la ligne éditoriale, les
   sources et les trois dernières éditions (pour éviter les répétitions).
3. Elle lance au minimum **six recherches web**, une par angle éditorial.
4. Elle **vérifie** : remontée à la source primaire, corroboration de chaque
   chiffre, traitement explicite des contradictions. Un fait non corroboré
   n'entre pas dans l'édition.
5. Elle rédige l'édition en Markdown, puis **`check_edition.py` la valide** :
   tant qu'une règle bloquante est violée, l'édition ne part pas.
6. Elle archive dans `editions/`.
6. `scripts/render_email.py` produit le HTML, diffusé en cascade : email
   Gmail, sinon artifact privé, sinon notification push.

**Routine active :** `Signal IA — newsletter quotidienne 08h30`
(`trig_01LRYDtrATKzYzWqXrNptHrj`), cron `29 6 * * *` UTC, 7j/7 — arrive à 08h29 heure de Paris.

**État de l'email :** en attente de deux autorisations — voir
[`config/delivery.md`](config/delivery.md). En attendant, l'édition est livrée
par artifact privé et notification push, et toujours archivée dans le dépôt.

## Contrainte d'environnement importante

L'egress réseau de cet environnement est **fermé**. `curl`, les flux RSS et
`WebFetch` échouent tous (403 / `EGRESS_BLOCKED`). **`WebSearch` est le seul
canal de collecte disponible** — il s'exécute côté serveur Anthropic et n'est
pas soumis au proxy.

Les 49 sources de `config/sources.yaml` servent donc de **filtre de confiance**
(`allowed_domains` des recherches) et de référence éditoriale, et non de flux
directement aspirés.

> Si l'egress est ouvert plus tard sur les domaines de news, la collecte peut
> passer en mode RSS — plus exhaustive et plus fidèle aux sources. C'est une
> évolution, **pas un prérequis** : la newsletter fonctionne sans.
>
> Pour l'ouvrir : claude.ai/code → environnement « Newsletter IA » → niveau
> d'accès réseau → **Custom**, en y collant
> [`config/egress-allowlist.txt`](config/egress-allowlist.txt) (53 domaines,
> déjà prêt).

Trois domaines (`reuters.com`, `lesechos.fr`, `zdnet.com`) refusent par
ailleurs le crawler et sont marqués `crawler_blocked: true` : ne jamais les
passer en `allowed_domains`, la recherche échouerait.

## Les trois outils

```bash
# Mémoire : qui a déjà eu sa fiche, quelles sources sont épuisées
python3 scripts/registry.py

# Contrôle qualité — sort en code 1 si une règle bloquante est violée
python3 scripts/check_edition.py editions/2026-09-15.md

# Aperçu du rendu email
python3 scripts/render_email.py editions/2026-09-15.md --out /tmp/apercu.html
```

`check_edition.py` encode les règles de `config/editorial.md` : rubriques
présentes, chaque item sourcé, aucune URL répétée, deux items maximum par
domaine, deux puces techniques minimum dans le brief, chiffre du jour non
déjà servi, proximité avec les sujets des sept derniers jours.

Appliqué rétroactivement, il rejetait les trois premières éditions — items
sans source, même média cité trois fois, chiffre du jour déjà présent dans le
brief. Les règles écrites ne suffisaient pas : il fallait les rendre
exécutables.

## Modifier la newsletter

| Pour changer… | Éditer… |
|---------------|---------|
| les rubriques, leur poids, le ton | `config/editorial.md` |
| les sources suivies | `config/sources.yaml` |
| le destinataire ou l'heure d'envoi | `config/delivery.md` |
| la méthode de collecte ou de vérification | `prompts/daily-brief.md` |
| l'apparence de l'email | `scripts/render_email.py` |

Aucun de ces changements ne demande de toucher à la Routine planifiée.
