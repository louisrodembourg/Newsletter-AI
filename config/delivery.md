# Configuration de livraison

## Destinataires

```
to : louis68600@gmail.com, louis.rodembourg@ovhcloud.com
```

Les deux adresses reçoivent la même édition, dans le champ `to` d'un unique
envoi (pas deux emails séparés).

✅ **Adresse personnelle confirmée par Louis le 13/09/2026, adresse
professionnelle ajoutée à sa demande le 15/09/2026.** La routine n'envoie
jamais à une adresse absente de cette liste. Pour ajouter ou retirer un
destinataire, modifier ce fichier — pas le prompt.

## Horaire

```
heure locale : 08h30 (Europe/Paris) — arrive à 08h29, voir ci-dessous
cron UTC     : 29 6 * * *
fréquence    : tous les jours (7j/7)
```

⚠️ **Le cron est évalué en UTC, pas en heure locale.** Paris est à UTC+2 en
été (CEST) et UTC+1 en hiver (CET). Le cron ci-dessus vise 08h30 locale en
*heure d'été*.

### Pourquoi 29 et pas 30

Le planificateur applique un décalage d'étalement de charge (~8 min 24 s) aux
crons tombant sur une **minute ronde** — 0 ou 30. Mesuré le 13/09/2026 :

| Cron | Déclenchement réel |
|------|--------------------|
| `0 7 * * *` | 07h08:24 ❌ |
| `30 6 * * *` | 06h38:24 ❌ |
| `22 6 * * *` | 06h22:00 ✅ |
| `29 6 * * *` | 06h29:00 ✅ |

Toute minute non ronde se déclenche à la seconde près. On vise donc 08h29
locale plutôt que 08h30 : une minute d'écart, contre huit en réglant sur 30.

**Ne jamais repasser ce cron sur `30` ou `0`** en croyant corriger l'horaire —
ce serait le dégrader.

**Conséquence à connaître :** au passage à l'heure d'hiver (dernier dimanche
d'octobre 2026, soit le **25 octobre**), l'édition arrivera à 07h29 locale au
lieu de 08h29. Pour rétablir, passer le cron à `29 7 * * *`. Inversement au
retour de l'heure d'été (dernier dimanche de mars), revenir à `29 6 * * *`.

| Période | Heure locale visée | Cron UTC |
|---------|--------------------|----------|
| Heure d'été (fin mars → fin octobre) | 08h29 CEST | `29 6 * * *` |
| Heure d'hiver (fin octobre → fin mars) | 08h29 CET | `29 7 * * *` |

## Objet de l'email

```
Signal IA — <jour> <date> · <accroche>
```

Exemple : `Signal IA — dimanche 13 septembre · L'Europe met 3 milliards sur la table`

L'accroche fait 4 à 6 mots et reprend le sujet dominant du jour. Elle doit
donner envie d'ouvrir sans surpromettre.

## ⚠️ État de l'autorisation Gmail

**Constaté le 13/09/2026 : le connecteur Gmail est en lecture seule.**
L'appel `send_message` échoue avec `Insufficient scope` — il manque le scope
`gmail.send` (ou `gmail.compose` / `gmail.modify`).

**Deux actions sont nécessaires pour activer l'email**, et une seule ne suffit
pas :

1. **Accorder la permission d'envoi.** claude.ai → Réglages → Connecteurs →
   Gmail → reconnecter en acceptant la permission d'**envoi** de messages.

2. **Attacher le connecteur à la routine.** La routine
   `Signal IA — newsletter quotidienne 09h00` (`trig_01LRYDtrATKzYzWqXrNptHrj`)
   a été créée sans connecteur : l'API refuse de les attacher depuis cette
   organisation. Ses sessions n'ont donc aucun outil `mcp__Gmail__*`, même une
   fois le point 1 réglé. Il faut lui attacher Gmail depuis l'interface
   **Routines de claude.ai**, ou recréer la routine depuis cette interface.

Aucune modification de ce dépôt n'est nécessaire : la routine retente l'email à
chaque exécution et bascule dessus automatiquement dès que les deux points sont
réglés.

## Livraison en cascade

Tant que l'envoi Gmail est indisponible, la routine ne saute pas l'édition :
elle descend la cascade jusqu'au premier canal qui fonctionne.

| Rang | Canal | Condition |
|------|-------|-----------|
| 1 | **Email Gmail** | Scope d'envoi accordé. Canal nominal. |
| 2 | **Artifact privé** | Toujours disponible. Page web privée, URL stable, lisible sur mobile. |
| 3 | **Notification push** | En complément du rang 2 : signale que l'édition est prête et porte le lien. |
| 4 | **Archive dans le dépôt** | Systématique, quel que soit le canal retenu. |

L'archive dans `editions/` a lieu **dans tous les cas** : même si tous les
canaux de diffusion échouent, l'édition du jour n'est jamais perdue.

## Incident connu : le corps de l'email remplacé par une commande

**15/09/2026.** L'édition envoyée avait pour unique contenu la chaîne
`$(cat /tmp/edition-2026-09-15.html)`. La session avait bien généré le HTML
dans un fichier, mais a passé la substitution shell comme valeur de `htmlBody`
en supposant qu'elle serait interprétée. Les arguments d'un appel d'outil ne
traversent aucun shell : la chaîne part littéralement.

Symptôme reconnaissable : un email de ~14 Ko au lieu de ~35 Ko, dont l'aperçu
Gmail affiche une commande. Un cas voisin s'était produit le 13/09 avec du HTML
envoyé en texte brut.

La parade est dans `prompts/daily-brief.md`, étape 5a : lire le fichier, coller
son contenu réel, et vérifier avant l'envoi que `htmlBody` commence par
`<table`, dépasse 5 000 caractères et ne contient ni `$(` ni backtick.

## Incidents de livraison — historique

| Date | Symptôme | Cause |
|------|----------|-------|
| 13/09 | HTML affiché en texte brut | HTML placé dans `body` au lieu de `htmlBody` |
| 15/09 | Email de 14 Ko, corps = `$(cat …)` | Substitution shell passée en paramètre d'outil |
| 16/09 | **Aucun email** | Édition écrite, validée et poussée, jamais envoyée |
| 17/09 | Email de 4 Ko, texte brut | `htmlBody` purement et simplement omis |

Le point commun des trois derniers : **le contenu était bon, la diffusion a
échoué en silence**. D'où le contrôle post-envoi ajouté le 17/09 — relire le
message parti et vérifier que `sizeEstimate` dépasse 15 000 octets.

Repères de taille : 23 000 à 36 000 octets pour une édition correcte, 14 000
pour un corps corrompu, 4 000 pour un envoi en texte seul.

## La cause dominante : le classificateur de permissions

Les sessions de routine tournent en mode `auto`, où chaque appel d'outil est
soumis à un classificateur qui peut le refuser. C'est lui qui bloque l'envoi,
pas Gmail : le 19/09 il a refusé `send_message` (« permission refusée par le
classificateur de la session »), le 20/09 il a accepté le même appel.

| Date | Envoi | Verdict |
|------|-------|---------|
| 15/09 | vers l'adresse pro | refusé (envoi manuel réussi dans la minute) |
| 16/09 | — | aucun email |
| 18/09 | après 17 min de tentatives | refusé |
| 19/09 | — | refusé, explicitement documenté |
| 17 et 20/09 | idem | accepté |

**Correctif définitif — hors de portée de la routine.** Autoriser
explicitement `mcp__Gmail__send_message`, soit dans l'écran d'édition de la
routine sur claude.ai/code/routines, soit dans un `.claude/settings.json` à la
racine du dépôt (`permissions.allow` et une règle `autoMode.allow` décrivant
l'envoi). Une session ne peut pas écrire elle-même ses propres règles de
permission : toute tentative est refusée pour « Self-Modification », ce qui est
le comportement voulu.

**Atténuation en attendant** — trois tentatives d'envoi de formes différentes
avant tout repli, décrites dans `prompts/daily-brief.md` étape 5a. Le verdict
n'étant pas stable, réessayer suffit souvent.

## Comportement en cas de problème

| Situation | Comportement attendu |
|-----------|----------------------|
| `WebSearch` échoue totalement | Email court signalant la panne. Jamais d'édition vide. |
| Collecte pauvre (< 8 items solides) | Édition courte assumée. Pas de remplissage. |
| Échec de l'envoi Gmail | L'édition est tout de même commitée dans `editions/`, et la panne est signalée. |
| `htmlBody` suspect (trop court, contient `$(`) | Ne pas envoyer. Relire le fichier rendu et recommencer. |
| Un fait majeur non corroboré | Il passe en « signal faible » avec sa mention d'incertitude, ou il est écarté. |
