# Contenus longs pour fiches PDF (français) — génération ≥ ~22 pages par thème via répétition structurée.
# Sigur que chaque thème a des titres de chapitres et un corps pédagogique cohérent.

INTRO_PARAS = {
    'importance': (
        'Ce document complet rassemble les notions essentielles sur l’importance des sols pour '
        'l’agriculture togolaise, la sécurité alimentaire et les services écosystémiques. Il s’adresse '
        'aux agents de terrain, aux enseignants, aux agronomes et aux passionnés désireux d’approfondir '
        'la compréhension du patrimoine pédologique de la région Maritime et au-delà.',
        'Les sols ne sont pas qu’un « support » passif : ils filtrent l’eau, stockent le carbone, '
        'recyclent les nutriments et abritent une biodiversité microscopique indispensable à la fertilité. '
        'Sans leur bonne gestion, les investissements en semences, engrais et irrigation perdent une partie '
        'de leur efficacité.',
    ),
    'types': (
        'Cette fiche détaillée présente les grands types de sols observés au Togo, leurs processus de '
        'formation, leurs contraintes agronomiques et les stratégies d’aménagement les plus courantes. '
        'Les exemples illustrent des situations fréquentes en zone maritime et plateaux.',
        'La classification pédologique aide à communiquer entre scientifiques, mais sur le terrain il '
        'faut aussi décrire la texture, la couleur, la profondeur effective racinaire, la stagnation '
        'd’eau et la présence de horizons limitants pour prendre des décisions praticables.',
    ),
    'practices': (
        'Les bonnes pratiques agricoles (BPAs) visent à maintenir ou améliorer la matière organique, '
        'la structure du sol et la biodiversité utile tout en stabilisant les rendements face au climat. '
        'Ce guide les organise en chapitres thématiques avec rappels scientifiques et pistes d’action.',
        'Aucune technique n’est universelle : la combinaison « labour zéro + couverture + rotation » '
        'fonctionne différemment sur un sol sableux drainant qu’sur un sol argileux collant. L’observation '
        'locale (eau, adventices, micro-relief) reste prioritaire.',
    ),
    'nasa': (
        'L’observation de la Terre par satellite fournit des indicateurs continus sur la végétation, '
        'l’humidité des sols en surface ou les précipitations. La NASA et ses partenaires mettent à '
        'disposition des produits gratuits (MODIS, SMAP, GPM, etc.) exploitables après formation de base.',
        'Ce document explique la chaîne « capteur → produit → extraction locale → interprétation agronomique » '
        'sans remplacer les mesures terrain, qui restent nécessaires pour calibrer le regard et valider '
        'les anomalies détectées sur une image.',
    ),
    'erosion': (
        'L’érosion hydrique et éolienne menace les horizons fertiles, creuse des ravines, charge les '
        'cours d’eau en sédiments et peut dégrader les infrastructures. La prévention est souvent moins '
        'coûteuse que la curative ; ce texte développe diagnostics, seuils d’alerte et techniques de '
        'conservation des sols.',
        'Les pentes longues, les pluies courtes et intenses et l’absence de couverture végétale '
        'combinent les facteurs de risque : les chapitres suivants détaillent comment réduire l’énergie '
        'des ruissellements et protéger le sol nu des gouttes de pluie.',
    ),
    'geomatics': (
        'La géomatique regroupe les sciences et techniques qui mesurent, représentent et analysent '
        'la surface terrestre et son occupation. Elle nourrit la cartographie, l’aménagement du territoire, '
        'la gestion des risques et le suivi environnemental ; au Togo, elle soutient l’agriculture, '
        'l’hydraulique rurale et la planification communale.',
        'Ce document explique pourquoi des coordonnées fiables, des modèles numériques de terrain '
        'et des images aériennes ou satellitaires ne sont pas un luxe mais un outil de dialogue entre '
        'techniciens, décideurs et habitants.',
    ),
    'sig': (
        'Un système d’information géographique (SIG) organise des données géolocalisées en couches '
        'consultables, interrogeables et partageables. Il permet de superposer sols, parcelles, routes, '
        'hydrographie et indicateurs satellites pour comprendre un territoire dans son ensemble.',
        'Ce guide développe les concepts de base (couches, attributs, échelle, projection) et montre '
        'comment les SIG renforcent la gestion des sols, la vulgarisation et la redevabilité des projets '
        'publics en région Maritime.',
    ),
}

CHAPTER_TITLES = {
    'importance': [
        'Rôles multiples du sol dans le paysage agricole',
        'Cycles biogéochimiques : carbone, azote et phosphore',
        'Stockage et filtration de l’eau dans le profil',
        'Biodiversité du sol : vers de terre, bactéries, champignons',
        'Résilience face aux sécheresses et aux pluies intenses',
        'Liens entre fertilité chimique et vie microbiologique',
        'Indicateurs simples observables au champ',
        'Sols et sécurité alimentaire en Afrique de l’Ouest',
        'Urbanisation et artificialisation : enjeux pour les sols',
        'Restauration écologique et rehabilitation des terrains',
        'Données spatiales (NDVI, humidité) comme aide à la décision',
        'Collaboration communauté – recherche – vulgarisation',
        'Bonnes pratiques de prélèvement et d’analyse pédologique',
        'Cas pratiques : bas-fonds, versants, zones côtières',
        'Perspectives d’apprentissage continu',
        'Annexes mentales : glossaire et références',
    ],
    'types': [
        'Sol ferrugineux tropical lessivé : traits et cartographie',
        'Sols jeunes sur matériaux sableux littoraux',
        'Hydromorphes et vertisols : gestion de l’eau',
        'Anthrosols et sols anthropiques peri-urbains',
        'Texture, structure et porosité : lecture de la motte',
        'Capacité de rétention et risque de battance',
        'Profondeur racinaire : comment l’estimer au sondage',
        'Carences et toxicités liées au pH',
        'Cartes locales et données du SIG Sols Togo',
        'Associations sol – paysage – occupation du sol',
        'Météorisation et évolution des sols en zone tropicale',
        'Amendements organiques et minéraux selon le type',
        'Cultures adaptées : racines profondes vs superficielles',
        'Eau disponible : bilan simplifié en saison des pluies',
        'Synthèse pour choisir une stratégie par parcelle',
        'Pour aller plus loin : lectures et terrain',
    ],
    'practices': [
        'Rotation et successions de cultures',
        'Couvertures végétales et engrais verts',
        'Gestion des résidus de culture',
        'Labour réduit et semis direct',
        'Compostage et fumier : qualité et sécurité sanitaire',
        'Chaulage et correction du pH',
        'Fertilisation minérale raisonnée',
        'Gestion intégrée de la fertilité (GIF)',
        'Irrigation locale et efficience d’utilisation de l’eau',
        'Agroforesterie et haies sur courbes de niveau',
        'Lutte antiérosive intégrée aux cultures',
        'Calendrier cultural et fenêtres climatiques',
        'Approches participatives avec les producteurs',
        'Suivi simple des parcelles témoins',
        'Indicateurs économiques des BPAs',
        'Plan d’action pluriannuel par exploitation',
    ],
    'nasa': [
        'Principes de télédétection optique et micro-ondes',
        'MODIS NDVI : saisonnalité et stress végétatif',
        'SMAP : humidité des sols en surface et limites',
        'Précipitations GPM-IMERG : cumuls et événements',
        'Catalogues STAC et accès Earthdata',
        'Préparation des identifiants et bonnes pratiques de citation',
        'Extraire une série temporelle sur une parcelle',
        'Nuages et artefacts : interprétation prudente',
        'Combiner satellite et données terrain (pH, texture)',
        'NDVI bas : hydrique, nutritionnel ou sanitaire ?',
        'Cas d’usage : suivi post-sécheresse',
        'Intégration dans un tableau de bord SIG',
        'Formation des utilisateurs non spécialistes',
        'Éthique des données ouvertes et licences',
        'Perspectives : fusion multi-capteurs',
        'Synthèse et exercices d’auto-évaluation',
    ],
    'erosion': [
        'Facteurs USLE simplifiés en contexte local',
        'Ruissellement : vitesse, cisaillement, transport',
        'Ravine : cicatrisage et stabilisation',
        'Couverture végétale et coefficients de protection',
        'Bandes enherbées et zones tampons',
        'Terrasses et ouvrages de stockage',
        'Gestion du captage en tête de bassin',
        'Stone lines et techniques traditionnelles améliorées',
        'Plan communal de protection des sols',
        'Surveillance après fortes pluies',
        'Indicateurs précurseurs : mouchetures, racines exposées',
        'Coûts et bénéfices sur 5–10 ans',
        'Formation des équipes d’entretien',
        'Intégration elevage – parcours – cultures',
        'Liens avec la qualité de l’eau aval',
        'Conclusion et check-list terrain',
    ],
    'geomatics': [
        'Géomatique : définitions et champs d’application',
        'Géodésie et systèmes de coordonnées (WGS 84, UTM)',
        'Topographie et nivellement de précision',
        'Modèles numériques de terrain (MNT, SRTM)',
        'Photogrammétrie et images aériennes',
        'Télédétection : optique, radar, résolutions',
        'GPS / GNSS smartphone et récepteurs RTK',
        'Importance pour l’inventaire foncier et agricole',
        'Géomatique et gestion des risques (inondation, érosion)',
        'Lien géomatique – environnement – développement local',
        'Données ouvertes et métadonnées',
        'Qualité spatiale : précision, exactitude, résolution',
        'Éthique et vie privée (géolocalisation)',
        'Formation des agents DISIA / DUSOL',
        'Cas d’usage : région Maritime',
        'Perspectives drones et capteurs légers',
        'Annexes : glossaire géomatique',
    ],
    'sig': [
        'SIG : historique et principes',
        'Couches vectorielles et raster',
        'Attributs, tables et jointures',
        'Échelles cartographiques et généralisation',
        'Projections et déformations (UTM zone 31N)',
        'Symbologie et lisibilité des cartes',
        'Requêtes spatiales : sélection, buffer, intersection',
        'Importance pour la gestion des sols',
        'SIG et agriculture de précision',
        'Intégration données NASA dans un SIG',
        'Collecte participative et GeoJSON',
        'Web mapping (Leaflet, tuiles, WMS)',
        'Analyse multicritère simplifiée',
        'Communication cartographique aux décideurs',
        'Plateforme SIG Sols Togo : mode d’emploi',
        'Maintenance des bases et versions',
        'Annexes : bonnes pratiques SIG',
    ],
}

BODY_ROTATION = [
    'Les agriculteurs expérimentent souvent de petites parcelles témoins : une zone avec pratique '
    'améliorée et une zone témoin permettent de comparer rendement, couverture et labor sans risquer '
    'toute l’exploitation.',
    'Le suivi photographique (même avec un téléphone) des mêmes prises de vue avant/après saison '
    'documente l’évolution de la couverture et aide à convaincre le voisinage.',
    'Les analyses de laboratoire (pH, CEC, matière organique) complètent mais ne remplacent pas '
    'l’observation de la couleur de la poudre, de la réaction à l’acide dilué ou du test de mouillage.',
    'Une approche par « contraintes » résout les problèmes dans l’ordre : eau disponible, puis acaricide '
    'des racines, puis nutrition minérale ; ignorer la séquence peut gaspiller des intrants.',
    'Les cartes de potentiel érodible combinent pente longueur, occupation et intensité pluviométrique ; '
    'elles servent à prioriser les parcelles à protéger en premier.',
    'Les cultures pérennes (arbres fruitiers, boisements protecteurs) ancrent le sol sur plusieurs '
    'mètres de profondeur là où les annuelles ne protègent que la surface.',
    'Le paillage réduit l’impact des gouttes de pluie et réduit l’évaporation ; il doit être stable '
    'face au vent et ne pas constituer un foyer de ravageurs ; l’équilibre se règle localement.',
    'Quand le sol est battant après la première pluie, un passage léger ou une herse au bon moment '
    'recrée une « micro‑relief » favorable à la réaération ; les sols sensibles exigent des passages '
    'minimaux.',
    'Les indicateurs NASA comme le NDVI doivent être lus sur plusieurs dates : une image unique peut '
    'reflétter un nuage résiduel, un brûlage ou une jachère récente plutôt qu’une tendance de fond.',
    'L’humidité de surface SMAP réagit vite à la pluie : pour l’agronomie, on la croise avec la '
    'texture et le relief pour estimer si la zone racinaire profonde reste humide.',
    'Les formations courtes sur smartphone (capture d’écran, légende, échelle) améliorent la '
    'compréhension des producteurs qui n’ont pas accès aux logiciels SIG lourds.',
    'Les équipes projet doivent anticiper les périodes sans images utiles (nuages) en conservant '
    'plusieurs sources (optique + radar si disponible) ou en s’appuyant sur des indices composites.',
    'Les données ouvertes impliquent de citer la mission et le produit ; cela renforce la traçabilité '
    'des cartes communiquées aux institutions.',
    'Sur sol sableux, l’apport régulier de matière organique bien décomposée augmente la CEC '
    'apparente et la rétention des cations ; sans cela, les fertilisants lessivent plus vite.',
    'Sur sol argileux, le sur‑labour fragmente les agrégats ; les rotations avec légumineuses et '
    'engrais verts aident à reconstituer la structure.',
    'Les bas-fonds présentent souvent un redoximorphisme visible : zones grises = périodes de '
    'saturation ; choisir des variétés tolérantes ou améliorer le drainage de surface est crucial.',
    'Les parcelles en pente faible peuvent masquer un écoulement concentré : suivre les mouillères '
    'naturelles évite de placer des chemins d’eau involontaires.',
    'Une jauge pluviométrique communautaire coûte peu et améliore la corrélation entre cumuls locaux '
    'et anomalies NDVI/SMAP présentées sur la plateforme.',
    'Les agents de vulgarisation peuvent adapter ce contenu en fiches 2 pages par chapitre ; le PDF '
    'complet sert de manuel de référence.',
    'L’évaluation finale d’un programme sol devrait inclure rendement, profondeur de sol non érodée, '
    'richesse microbienne (tests simples si possible) et perception des agriculteurs.',
    'Les projets d’irrigation doivent dimensionner les volumes sur la texture réelle : un même volume '
    'mm d’eau pénètre différemment dans un limon qu’une argile compacte.',
    'Les plateformes SIG intègrent souvent des couches NASA dérivées : vérifier la date d’acquisition '
    'avant de comparer deux communes.',
    'Les politiques locales (interdiction brûlage, aménagement replat) soutiennent les techniques '
    'agricoles ; sans cadre, les investissements individuels sont fragiles.',
    'Les jeunes peuvent être formés à la télédétection légère avec outils en ligne et à la narration '
    'des cartes pour les comités villageois.',
    'Un risque sanitaire apparaît quand les fosses d’épandage sont trop proches des points d’eau : '
    'respecter les distances réglementaires et les périodes sans pluie forte.',
    'Les variétés à racines pivotantes profondes aident à stabiliser les versants modérés combinées '
    'à une couverture résiduelle permanente.',
    'Les cartes d’aléa érosion peuvent être croisées avec les données sociales (trafic bétail, '
    'coupe de bois) pour cibler les médiations.',
    'La pédogénèse explique pourquoi deux parcelles voisines diffèrent : micro‑relief, apports '
    'colluviaux, histoire culturale ; ne pas généraliser une observation unique.',
    'Les services écosystémiques du sol (pollinisation des cultures via habitats, filtration) '
    'justifient des paiements pour services environnementaux lorsqu’ils sont quantifiables.',
    'En conclusion de chapitre, il est recommandé de noter trois actions concrètes, un responsable '
    'et une date ; la mise en œuvre par étapes évite l’abandon.',
    'Annexe pratique : préparer une campagne de prélèvement (seaux propres, GPS, fiches terrain) '
    'améliore la qualité des données intégrées dans le SIG.',
    'En zones côtières, le sel et les intrusions salines compliquent le diagnostic : tester '
    'conductivité électrique ou symptômes foliaires avant d’accuser un déficit minéral classique.',
    'Les indicateurs « santé du sol » doivent rester interprétables : un score composite sans '
    'décomposition des facteurs peut masquer une acidification croissante.',
    'Les modèles numériques de terrain (MNT) aident à calculer la longueur de pente effective et à '
    'positionner les ouvrages ; des données gratuites SRTM existent mais la résolution locale peut '
    'manquer de finesse.',
    'Les associations paysannes peuvent mutualiser un appareil de mesure de pH pour réduire le coût '
    'par point et homogénéiser le protocole.',
]
