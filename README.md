# Signal IA

Newsletter quotidienne sur l'intelligence artificielle, livrée par email chaque
matin. Générée automatiquement par Claude Code : collecte, vérification,
rédaction, envoi et archivage.

**~7 minutes de lecture · 15 à 20 items · français**

## Ce que couvre la newsletter

Priorité à la substance technique et industrielle, dans cet ordre :

| Rubrique | Poids |
|----------|-------|
| ⚡ Le brief — 5 puces, dont au moins 2 techniques | — |
| 🧠 Tech & recherche — modèles, papers, benchmarks, open-weights | ~34 % |
| 🏗️ Infra, cloud & outillage — puces et datacenters, mais aussi services cloud, serving, frameworks d'agents, MLOps | ~22 % |
| 🏢 Les acteurs — fiches d'entreprises : ce qu'elles font, leur stack, leur stade, où elles sont basées | ~12 % |
| 🚀 Produits & adoption — lancements, agents, déploiements réels | ~16 % |
| 💰 Éco & investissement — levées, valorisations, IPO, M&A | ~10 % |
| 👀 Signal faible + 📊 Le chiffre du jour | ~6 % |

La newsletter sert aussi un usage carrière : le lecteur doit en ressortir avec
des noms d'entreprises, de modèles et d'outils réutilisables en entretien.
D'où la rubrique **Les acteurs**, la moitié « outillage » de la rubrique infra,
et une rubrique éco volontairement réduite à la macro-finance la plus utile.

La rubrique Les acteurs dresse une **carte du marché** — quelles entreprises
existent, ce qu'elles valent techniquement, où elles sont. Elle ne relaie
jamais d'offres d'emploi ni de pages carrières.

Périmètre géographique : **USA / labos frontier**, **Chine**, **France / Europe**.

Le détail de la ligne éditoriale — y compris ce qu'on refuse de traiter — est
dans [`config/editorial.md`](config/editorial.md).

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
5. Elle rédige l'édition en Markdown et l'archive dans `editions/`.
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

## Vérifier une édition à la main

```bash
python3 scripts/render_email.py editions/2026-09-13.md --out /tmp/apercu.html
```

## Modifier la newsletter

| Pour changer… | Éditer… |
|---------------|---------|
| les rubriques, leur poids, le ton | `config/editorial.md` |
| les sources suivies | `config/sources.yaml` |
| le destinataire ou l'heure d'envoi | `config/delivery.md` |
| la méthode de collecte ou de vérification | `prompts/daily-brief.md` |
| l'apparence de l'email | `scripts/render_email.py` |

Aucun de ces changements ne demande de toucher à la Routine planifiée.
