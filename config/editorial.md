# Ligne éditoriale — Signal IA

## Promesse

Une édition par matin, ~7 minutes de lecture, qui répond à une seule question :
**qu'est-ce qui a bougé dans l'IA depuis hier, et pourquoi ça compte ?**

Priorité assumée à la **substance technique et industrielle** plutôt qu'au bruit
médiatique. Un lancement de modèle avec ses benchmarks vaut dix tribunes sur
« l'IA va-t-elle nous remplacer ».

**Usage visé.** Louis lit cette newsletter pour suivre le domaine *et* pour sa
carrière. Le lecteur doit en ressortir avec des noms d'entreprises, des noms de
modèles, des techniques et des chiffres qu'il peut citer dans un entretien. Une
information qu'on ne peut ni réutiliser ni recouper n'a pas sa place ici.

## Hiérarchie des rubriques

L'ordre et le poids sont fixes. Ils reflètent les priorités définies avec Louis :
tech, infra et produits d'abord, éco ensuite.

| # | Rubrique | Poids cible | Items |
|---|----------|-------------|-------|
| 1 | ⚡ Le brief | 5 bullets | 5 |
| 2 | 🧠 Tech & recherche | ~34 % | 5-6 |
| 3 | 🏗️ Infra, cloud & outillage | ~22 % | 3-4 |
| 4 | 🏢 Les acteurs | ~12 % | 2-3 |
| 5 | 🚀 Produits & adoption | ~16 % | 2-3 |
| 6 | 💰 Éco & investissement | ~10 % | 2 |
| 7 | 👀 Signal faible + 📊 Le chiffre | ~6 % | 2 |

Volume cible : **1 300 à 1 700 mots**, 15 à 20 items au total.

### 1. ⚡ Le brief
Cinq puces d'une ligne. Ce sont les cinq choses à savoir si on ne lit rien
d'autre. Chaque puce renvoie à la rubrique qui la développe.

**Au moins deux puces sur cinq doivent être techniques** (modèle, recherche,
architecture, cloud, outillage). Un brief où quatre puces sur cinq parlent de
montants levés trahit la ligne éditoriale, même si chaque puce est juste
individuellement.

### 2. 🧠 Tech & recherche
Nouveaux modèles et poids ouverts, papers marquants, benchmarks et évaluations,
architectures, techniques d'entraînement et d'inférence, sécurité technique.
On donne les chiffres : taille, contexte, scores, coût au token.

### 3. 🏗️ Infra, cloud & outillage
Deux moitiés, à équilibrer :

**Le matériel** — puces et accélérateurs, datacenters, énergie, contraintes
d'approvisionnement, coûts d'inférence, réseaux et mémoire. La contrainte
physique de l'IA est un sujet en soi, pas une note de bas de page.

**Ce qu'on manipule** — services cloud IA (Bedrock, Vertex, Azure AI,
Together, Fireworks, Modal…), plateformes d'inférence et de serving (vLLM,
SGLang, TensorRT-LLM), frameworks d'agents et de RAG, outillage MLOps et
évaluation, bases vectorielles. C'est la moitié la plus directement utile au
lecteur : ce sont les outils qu'il devra savoir nommer et comparer.

Le capex des hyperscalers relève de la rubrique Éco, pas d'ici — sauf quand il
dit quelque chose de la capacité réellement disponible.

### 4. 🏢 Les acteurs
Deux à trois fiches courtes par édition. Objectif : constituer au fil des
semaines une carte mentale du marché — qui fait quoi, qui monte, qui embauche.

Chaque fiche, en 3 à 5 phrases :
- **Ce que fait l'entreprise**, techniquement et concrètement.
- **Sa stack ou son angle technique** quand il est documenté.
- **Son stade** : levée et valorisation, effectif, clients connus.
- **Pourquoi elle compte** : ce qu'elle menace ou débloque.
- **Ses signaux de croissance** quand ils sont publics : levée récente,
  ouverture de bureau, vagues de recrutement annoncées.

Priorité aux entreprises qu'on ne connaît pas encore : un nouvel entrant qui
lève 80 M$ sur l'inférence apprend davantage au lecteur qu'un énième point sur
OpenAI. Alterner les profils — labos, infra, outillage dev, applicatif
vertical — et les géographies, en incluant régulièrement des acteurs français
et européens, directement pertinents pour une candidature depuis la France.

Ne jamais inventer une information de recrutement. Si rien de public n'est
disponible sur ce point, la fiche s'arrête à ce que l'entreprise fait.

### 5. 🚀 Produits & adoption
Lancements produits, agents, outils de dev, intégrations, déploiements en
entreprise, chiffres d'usage réels, retours terrain. On privilégie ce qui est
disponible et mesurable sur ce qui est annoncé et lointain.

### 6. 💰 Éco & investissement
Levées, valorisations, revenus et ARR, M&A, IPO, pricing, résultats trimestriels,
mouvements de talents structurants. **Complément d'analyse, pas cœur de
l'édition** — rubrique volontairement réduite.

Retenir ce qui déplace un rapport de force ou change un prix, écarter la
macro-finance pure. Un chiffre de capex mondial ou de capital-risque agrégé ne
mérite une place que s'il est rattaché à une conséquence concrète : une
capacité qui change, un prix qui bouge, un acteur qui décroche. Deux items
suffisent.

### 7. 👀 Signal faible et 📊 Le chiffre du jour
Un signal sous-couvert qui pourrait compter dans six mois. Un chiffre marquant
remis en contexte. Deux items courts pour clore.

## Périmètre géographique

Trois zones suivies, dans cet ordre de volume :

1. **USA / labos frontier** — OpenAI, Anthropic, Google DeepMind, Meta, xAI,
   Nvidia, hyperscalers. Le cœur du flux.
2. **Chine** — DeepSeek, Qwen/Alibaba, Moonshot, ByteDance, Zhipu, contrôles à
   l'export, écosystème open-weights. Systématiquement sous-couvert par la
   presse francophone : on le traite comme un sujet de premier plan.
3. **France / Europe** — Mistral, AI Act et son application, écosystème startup,
   souveraineté, financements européens.

Le reste du monde (Golfe, Inde, Japon, Corée) n'est traité que lorsqu'il pèse
directement sur ces trois zones — typiquement un méga-deal datacenter qui
déplace l'allocation mondiale de compute.

## Ce qu'on ne traite pas

- Les tribunes d'opinion et les débats de société sans fait nouveau.
- Les annonces de partenariat sans contenu vérifiable ni calendrier.
- Les levées inférieures à 50 M$, sauf signal technique ou stratégique fort.
- Les classements et « top 10 des outils IA ».
- La régulation, sauf décision effective à impact direct (texte adopté,
  sanction prononcée, jugement rendu). Une ligne dans le brief suffit alors.

## Règles de rédaction

1. **Le fait d'abord, le commentaire ensuite.** Chaque item ouvre sur ce qui
   s'est passé, puis une phrase de « pourquoi ça compte ».
2. **Chiffré dès que possible.** Un montant, un score, un pourcentage, une date.
3. **Chaque item est sourcé** par un lien cliquable vers la source d'origine.
   Sans exception : un item sans lien est un item à retirer. Deux items ne
   doivent pas pointer vers la même URL — si deux faits viennent de la même
   page, ils forment un seul item.
4. **2 à 4 phrases par item.** Jamais plus. Si un sujet mérite davantage, il
   devient le signal faible du jour.
5. **Pas de superlatif non étayé.** Ni « révolutionnaire », ni « change tout ».
   On décrit, on quantifie, le lecteur juge.
6. **Incertitude signalée.** Une rumeur est présentée comme telle, avec sa
   source et son degré de fiabilité.
7. **Français, jargon technique conservé en anglais** quand c'est l'usage
   (open-weights, inference, context window, scaling). On ne traduit pas pour
   traduire.
8. **Pas de remplissage.** Une journée calme donne une édition courte. Mieux
   vaut 10 items solides que 18 dont 8 creux.
