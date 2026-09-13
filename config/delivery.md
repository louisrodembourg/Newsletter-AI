# Configuration de livraison

## Destinataire

```
email : louis68600@gmail.com
```

✅ **Confirmé par Louis le 13/09/2026.** La routine n'envoie
jamais à une autre adresse que celle inscrite ici. Pour changer de
destinataire, modifier ce fichier — pas le prompt.

## Horaire

```
heure locale : 09h00 (Europe/Paris)
cron UTC     : 0 7 * * *
fréquence    : tous les jours (7j/7)
```

⚠️ **Le cron est évalué en UTC, pas en heure locale.** Paris est à UTC+2 en
été (CEST) et UTC+1 en hiver (CET). Le cron ci-dessus vise 09h00 locale en
*heure d'été*.

Choisir 09h00 donne à la collecte une couverture large : toute la nuit
américaine, plus les annonces asiatiques du matin — ce qui sert directement
la place donnée à la Chine dans la ligne éditoriale.

**Conséquence à connaître :** au passage à l'heure d'hiver (dernier dimanche
d'octobre 2026, soit le **25 octobre**), l'édition arrivera à 08h00 locale au
lieu de 09h00. Pour rétablir, passer le cron à `0 8 * * *`. Inversement au
retour de l'heure d'été (dernier dimanche de mars), revenir à `0 7 * * *`.

| Période | Heure locale visée | Cron UTC |
|---------|--------------------|----------|
| Heure d'été (fin mars → fin octobre) | 09h00 CEST | `0 7 * * *` |
| Heure d'hiver (fin octobre → fin mars) | 09h00 CET | `0 8 * * *` |

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

**Pour débloquer l'envoi :** claude.ai → Réglages → Connecteurs → Gmail →
reconnecter en acceptant la permission d'**envoi** de messages. Aucune
modification de ce dépôt n'est nécessaire ensuite : la routine retente l'email
à chaque exécution et bascule dessus automatiquement dès qu'il passe.

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

## Comportement en cas de problème

| Situation | Comportement attendu |
|-----------|----------------------|
| `WebSearch` échoue totalement | Email court signalant la panne. Jamais d'édition vide. |
| Collecte pauvre (< 8 items solides) | Édition courte assumée. Pas de remplissage. |
| Échec de l'envoi Gmail | L'édition est tout de même commitée dans `editions/`, et la panne est signalée. |
| Un fait majeur non corroboré | Il passe en « signal faible » avec sa mention d'incertitude, ou il est écarté. |
