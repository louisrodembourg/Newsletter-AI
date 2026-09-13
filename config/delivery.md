# Configuration de livraison

## Destinataire

```
email : louis68600@gmail.com
```

⚠️ **À confirmer avant la première vraie diffusion.** La routine n'envoie
jamais à une autre adresse que celle inscrite ici. Pour changer de
destinataire, modifier ce fichier — pas le prompt.

## Horaire

```
heure locale : 07h00 (Europe/Paris)
cron UTC     : 0 5 * * *
fréquence    : tous les jours
```

⚠️ **Le cron est évalué en UTC, pas en heure locale.** Paris est à UTC+2 en
été (CEST) et UTC+1 en hiver (CET). Le cron ci-dessus vise 07h00 en *heure
d'été*.

**Conséquence à connaître :** au passage à l'heure d'hiver (dernier dimanche
d'octobre), l'édition arrivera à 06h00 locale au lieu de 07h00. Pour rétablir,
passer le cron à `0 6 * * *`. Inversement au retour de l'heure d'été (dernier
dimanche de mars), revenir à `0 5 * * *`.

| Période | Heure locale visée | Cron UTC |
|---------|--------------------|----------|
| Heure d'été (fin mars → fin octobre) | 07h00 CEST | `0 5 * * *` |
| Heure d'hiver (fin octobre → fin mars) | 07h00 CET | `0 6 * * *` |

## Objet de l'email

```
Signal IA — <jour> <date> · <accroche>
```

Exemple : `Signal IA — dimanche 13 septembre · L'Europe met 3 milliards sur la table`

L'accroche fait 4 à 6 mots et reprend le sujet dominant du jour. Elle doit
donner envie d'ouvrir sans surpromettre.

## Comportement en cas de problème

| Situation | Comportement attendu |
|-----------|----------------------|
| `WebSearch` échoue totalement | Email court signalant la panne. Jamais d'édition vide. |
| Collecte pauvre (< 8 items solides) | Édition courte assumée. Pas de remplissage. |
| Échec de l'envoi Gmail | L'édition est tout de même commitée dans `editions/`, et la panne est signalée. |
| Un fait majeur non corroboré | Il passe en « signal faible » avec sa mention d'incertitude, ou il est écarté. |
