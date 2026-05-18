"""
Banque de 100 questions par niveau — sols Togo, NASA, SIG, agriculture.
Utilisé par seed_quiz_questions et seed_demo_data.
"""
from __future__ import annotations

QUESTIONS_PER_LEVEL = 100


def _q(text, choices, correct_index, explanation, is_nasa=False):
    return {
        'text': text,
        'choices': list(choices),
        'correct_index': correct_index,
        'explanation': explanation,
        'is_nasa_topic': is_nasa,
    }


# ─── Facile (100) ───────────────────────────────────────────────────────────

def _facile_static():
    return [
        _q('Quel indice NASA mesure la végétation ?', ['NDVI', 'pH', 'SRTM', 'GPM'], 0,
           'Le NDVI (Normalized Difference Vegetation Index) quantifie la vigueur végétale.', True),
        _q('Un pH de 7 correspond à un sol :', ['Neutre', 'Acide', 'Très acide', 'Salin'], 0,
           'pH 7 = neutre ; en dessous = acide, au-dessus = basique.'),
        _q('Un pH inférieur à 5,5 indique généralement un sol :', ['Acide', 'Basique', 'Neutre', 'Salé'], 0,
           'Les sols ferrugineux tropicaux du Togo sont souvent acides.'),
        _q('Le Togo se situe en Afrique :', ['de l\'Ouest', 'du Nord', 'de l\'Est', 'Centrale'], 0,
           'Le Togo est un pays côtier d\'Afrique de l\'Ouest.'),
        _q('La région Maritime du Togo est connue pour :', ['Agriculture et côte', 'Désert', 'Haute montagne', 'Toundra'], 0,
           'La Maritime abrite Lomé et des zones agricoles importantes.'),
        _q('Un sol argileux retient généralement :', ['Plus d\'eau', 'Moins d\'eau', 'Aucune eau', 'Uniquement l\'air'], 0,
           'Les argiles ont une forte capacité de rétention.'),
        _q('Un sol sableux se caractérise par :', ['Un drainage rapide', 'Une forte rétention', 'Une couleur bleue', 'Un pH toujours basique'], 0,
           'Le sable laisse passer l\'eau rapidement.'),
        _q('Le compost améliore surtout :', ['La matière organique', 'L\'altitude', 'La salinité', 'Le vent'], 0,
           'Le compost enrichit la structure et la fertilité.'),
        _q('L\'érosion concerne principalement :', ['La perte de sol', 'L\'augmentation du pH', 'La hausse du NDVI', 'La baisse de population'], 0,
           'L\'érosion emporte la couche arable.'),
        _q('PostGIS est utilisé pour :', ['Données géographiques', 'Courriels', 'Vidéos', 'Factures'], 0,
           'PostGIS étend PostgreSQL pour le spatial.'),
        _q('SIG signifie :', ['Système d\'Information Géographique', 'Service International du Grain', 'Sol Individuel Génétique', 'Satellite Infrarouge Global'], 0,
           'Le SIG associe données, cartes et analyse spatiale.'),
        _q('La couleur verte sur une carte NDVI indique :', ['Végétation vigoureuse', 'Eau profonde', 'Sol nu', 'Neige'], 0,
           'NDVI élevé = forte activité photosynthétique.', True),
        _q('SMAP (NASA) mesure :', ['L\'humidité du sol', 'Les précipitations uniquement', 'La population', 'Le pH'], 0,
           'Soil Moisture Active Passive = humidité superficielle.', True),
        _q('GPM (NASA) concerne :', ['Les précipitations', 'Le pH', 'Les types de sol', 'Les routes'], 0,
           'Global Precipitation Measurement.', True),
        _q('Un sol limoneux est intermédiaire entre :', ['Sable et argile', 'Eau et air', 'Roche et métal', 'Sel et sucre'], 0,
           'Texture intermédiaire, bon compromis agronomique.'),
        _q('La chaux agricole sert surtout à :', ['Corriger l\'acidité', 'Augmenter l\'acidité', 'Sécher le sol', 'Colorer les cartes'], 0,
           'Chaulage = hausse du pH sur sols acides.'),
        _q('La rotation des cultures aide à :', ['Préserver la fertilité', 'Augmenter l\'érosion', 'Saliniser le sol', 'Réduire la biodiversité'], 0,
           'Alterner les cultures limite l\'épuisement.'),
        _q('Le maïs est une culture :', ['Céréalière', 'Aquatique', 'Forestière', 'Pétrolière'], 0,
           'Culture vivrière majeure au Togo.'),
        _q('Le manioc est adapté aux sols :', ['Tropicaux variés', 'Glaciaires', 'Volcaniques froids', 'Salins marins'], 0,
           'Culture racinaire résistante, très présente au Togo.'),
        _q('La matière organique améliore :', ['Structure et fertilité', 'Seulement la couleur', 'Uniquement le vent', 'La salinité'], 0,
           'MO = humus, rétention d\'eau et nutriments.'),
    ]


def _facile_generated():
    qs = []
    soils = [
        ('argileux', 'Argileux', 'retient bien l\'eau et les nutriments'),
        ('sableux', 'Sableux', 'draine rapidement l\'eau'),
        ('limoneux', 'Limoneux', 'offre un bon compromis de texture'),
        ('ferrugineux', 'Ferrugineux tropical', 'est typique du Togo'),
        ('hydromorphe', 'Hydromorphe', 'est souvent saturé en eau'),
    ]
    for i, (code, name, trait) in enumerate(soils):
        for j in range(4):
            n = i * 4 + j + 1
            qs.append(_q(
                f'[F{n}] Un sol {name.lower()} au Togo :',
                [trait, 'ne contient jamais d\'eau', 'est toujours salin', 'n\'existe pas en Afrique'],
                0,
                f'Les sols {name.lower()}s : {trait}.',
            ))
    ph_vals = [(4.5, 'très acide'), (5.5, 'acide'), (6.5, 'légèrement acide'), (7.0, 'neutre'), (8.0, 'basique')]
    for i, (val, label) in enumerate(ph_vals):
        for j in range(4):
            n = 20 + i * 4 + j + 1
            qs.append(_q(
                f'[F{n}] Un pH de {val} correspond à un sol :',
                [label.capitalize(), 'salin', 'sans vie', 'volcanique'],
                0,
                f'pH {val} = sol {label}.',
            ))
    nasa = [
        ('MODIS', 'observations de surface terrestre', True),
        ('Landsat', 'imagerie optique multispectrale', True),
        ('Sentinel-2', 'données européennes gratuites', True),
        ('Earthdata', 'portail d\'accès NASA', True),
        ('NDVI', 'indice de végétation', True),
    ]
    for i, (prod, desc, nasa_flag) in enumerate(nasa):
        for j in range(4):
            n = 40 + i * 4 + j + 1
            qs.append(_q(
                f'[F{n}] {prod} fournit principalement des :',
                [desc, 'factures agricoles', 'codes postaux', 'permis de conduire'],
                0,
                f'{prod} : {desc}.',
                nasa_flag,
            ))
    practices = [
        ('couvert végétal', 'protège le sol de l\'érosion'),
        ('bandes enherbées', 'ralentissent le ruissellement'),
        ('terrassement', 'stabilise les pentes'),
        ('agroforesterie', 'combine arbres et cultures'),
        ('fumure organique', 'recycle les nutriments'),
    ]
    for i, (prac, effet) in enumerate(practices):
        for j in range(4):
            n = 60 + i * 4 + j + 1
            qs.append(_q(
                f'[F{n}] La pratique « {prac} » :',
                [effet, 'augmente l\'érosion', 'salinise toujours le sol', 'empêche toute culture'],
                0,
                f'{prac.capitalize()} : {effet}.',
            ))
    crops = ['maïs', 'manioc', 'igname', 'arachide', 'coton', 'riz', 'soja', 'tomate', 'piment', 'banane plantain']
    for i, crop in enumerate(crops):
        qs.append(_q(
            f'[F{80+i+1}] La culture du {crop} au Togo :',
            ['contribue à l\'agriculture locale', 'est impossible en Afrique', 'ne nécessite jamais de sol', 'se fait uniquement en mer'],
            0,
            f'Le {crop} est une culture importante ou courante au Togo.',
        ))
    return qs


def build_facile():
    all_q = _facile_static() + _facile_generated()
    return all_q[:QUESTIONS_PER_LEVEL]


# ─── Moyen (100) ────────────────────────────────────────────────────────────

def _moyen_static():
    return [
        _q('La relation entre NDVI et stress hydrique est souvent :', ['Inverse en saison sèche', 'Toujours positive', 'Sans lien', 'Aléatoire uniquement'], 0,
           'Stress hydrique → baisse de végétation → NDVI baisse.', True),
        _q('SMAP a une résolution spatiale d\'environ :', ['36 km', '1 m', '10 cm', '500 km'], 0,
           'SMAP = résolution grossière, adaptée aux tendances régionales.', True),
        _q('Un sol avec CEC faible :', ['Retient moins les cations', 'Retient plus les cations', 'Est toujours basique', 'N\'a pas de texture'], 0,
           'CEC = capacité d\'échange cationique.'),
        _q('Le zonage de vulnérabilité combine typiquement :', ['Pente, NDVI, humidité', 'pH seul', 'Email et téléphone', 'Couleur des bâtiments'], 0,
           'Approche multicritère spatiale.'),
        _q('La régression logistique en ML peut prédire :', ['Classes de fertilité', 'La météo exacte à 1 an', 'Les numéros de téléphone', 'Les couleurs préférées'], 0,
           'Classification binaire ou multiclasse.'),
        _q('GeoJSON est un format :', ['Géospatial JSON', 'Audio', 'Vidéo', 'Binaire propriétaire'], 0,
           'Standard web pour géométries et attributs.'),
        _q('Un buffer spatial autour d\'un point sert à :', ['Analyser un voisinage', 'Supprimer des données', 'Chiffrer des mots de passe', 'Envoyer des SMS'], 0,
           'Zone d\'influence autour d\'une entité.'),
        _q('La télédétection passive utilise :', ['Rayonnement solaire réfléchi', 'Radar actif uniquement', 'Sonar', 'Courant électrique'], 0,
           'Capteurs optiques = passifs (Landsat, MODIS).', True),
        _q('L\'interpolation spatiale du pH permet de :', ['Estimer entre points mesurés', 'Supprimer le pH', 'Mesurer la population', 'Cartographier les routes'], 0,
           'IDW, krigeage, etc. entre échantillons.'),
        _q('Une carte de chaleur (heatmap) du pH montre :', ['Zones de concentration des valeurs', 'Uniquement les routes', 'Les frontières politiques', 'Les nuages'], 0,
           'Visualisation de densité ou intensité.'),
    ]


def _moyen_generated():
    qs = []
    indicators = [
        ('NDVI', 'végétation', True),
        ('LST', 'température de surface', True),
        ('SMAP', 'humidité du sol', True),
        ('GPM', 'précipitations', True),
        ('pH', 'acidité du sol', False),
        ('CEC', 'rétention des nutriments', False),
        ('MO', 'matière organique', False),
        ('conductivité', 'salinité', False),
    ]
    for i, (ind, role, nasa) in enumerate(indicators):
        for j in range(6):
            n = i * 6 + j + 1
            qs.append(_q(
                f'[M{n}] L\'indicateur {ind} renseigne principalement sur :',
                [role, 'les prix du marché', 'les langues parlées', 'les permis de pêche'],
                0,
                f'{ind} mesure ou estime : {role}.',
                nasa,
            ))
    ml_terms = [
        ('train/test split', 'évaluer sans sur-apprentissage'),
        ('F1-score', 'équilibrer précision et rappel'),
        ('matrice de confusion', 'visualiser erreurs de classification'),
        ('feature scaling', 'normaliser les variables numériques'),
        ('cross-validation', 'valider sur plusieurs sous-échantillons'),
    ]
    for i, (term, role) in enumerate(ml_terms):
        for j in range(6):
            n = 48 + i * 6 + j + 1
            qs.append(_q(
                f'[M{n}] En machine learning, « {term} » sert à :',
                [role, 'supprimer la base de données', 'colorer la carte en bleu', 'désactiver le GPS'],
                0,
                f'{term} : {role}.',
            ))
    spatial = [
        ('WGS84', 'système de coordonnées mondial GPS'),
        ('EPSG:4326', 'latitude/longitude décimales'),
        ('ST_Point', 'géométrie ponctuelle PostGIS'),
        ('ST_Within', 'test d\'inclusion spatiale'),
        ('ST_Distance', 'distance entre géométries'),
    ]
    for i, (term, role) in enumerate(spatial):
        for j in range(6):
            n = 78 + i * 6 + j + 1
            if n > 100:
                break
            qs.append(_q(
                f'[M{n}] En SIG, {term} correspond à :',
                [role, 'un type de sol uniquement', 'une culture vivrière', 'un badge quiz'],
                0,
                f'{term} : {role}.',
            ))
    return qs


def build_moyen():
    all_q = _moyen_static() + _moyen_generated()
    return all_q[:QUESTIONS_PER_LEVEL]


# ─── Difficile (100) ────────────────────────────────────────────────────────

def _difficile_static():
    return [
        _q('La corrélation entre SMAP et mesures terrain de humidité peut être évaluée par :', ['R² et RMSE', 'Uniquement la couleur', 'Le nombre d\'utilisateurs', 'La date du jour'], 0,
           'Métriques statistiques standard en validation.', True),
        _q('Un modèle Random Forest pour la fertilité utilise :', ['Ensembles d\'arbres de décision', 'Un seul neurone', 'Aucune variable', 'Uniquement le NDVI'], 0,
           'RF = agrégation de arbres avec bagging.'),
        _q('La krigeage ordinaire suppose souvent :', ['Stationnarité des résidus', 'Absence de spatialité', 'Données uniquement textuelles', 'Pas de variogramme'], 0,
           'Méthode géostatistique d\'interpolation.'),
        _q('L\'attribution NASA Earthdata requiert :', ['Crédit et licence des produits', 'Paiement obligatoire', 'Interdiction de citation', 'Aucune métadonnée'], 0,
           'Données libres avec conditions d\'usage.', True),
        _q('Un pipeline MLOps pour sols inclut typiquement :', ['Entraînement, validation, déploiement', 'Uniquement des emails', 'Suppression des métadonnées', 'Pas de versioning'], 0,
           'Cycle de vie du modèle prédictif.'),
        _q('La validation croisée spatiale évite :', ['Fuite d\'information géographique', 'Toute métrique', 'L\'usage de PostGIS', 'Les cartes'], 0,
           'Voisins spatiaux ne doivent pas fuiter train→test.'),
        _q('Un seuil NDVI < 0,3 en saison des pluies peut indiquer :', ['Stress végétatif ou sol nu', 'Forêt dense', 'Océan profond', 'Neige'], 0,
           'NDVI bas = peu de chlorophylle active.', True),
        _q('L\'intégration NASA + terrain dans SIG-SOLS vise à :', ['Croiser observation satellite et mesures sol', 'Remplacer toute mesure', 'Supprimer PostGIS', 'Ignorer le pH'], 0,
           'Approche multimodale spatiale.', True),
    ]


def _difficile_generated():
    qs = []
    scenarios = [
        ('pente forte + faible couvert', 'risque érosion élevé'),
        ('NDVI bas + SMAP bas', 'stress hydrique probable', True),
        ('pH acide + faible MO', 'besoin chaulage et compost'),
        ('texture sableuse + forte pluie', 'lessivage des nutriments'),
        ('zone humide + drainage insuffisant', 'asphyxie racinaire'),
        ('données NASA + points sol', 'calibration et validation', True),
        ('heatmap pH + clusters', 'identification zones homogènes'),
        ('modèle ML + nouvelles mesures', 'réentraînement périodique'),
    ]
    for i, (cond, interp) in enumerate(scenarios):
        nasa = len(cond) > 20 and 'NASA' in cond or 'NDVI' in cond or 'SMAP' in cond
        for j in range(8):
            n = i * 8 + j + 1
            qs.append(_q(
                f'[D{n}] Scénario : {cond}. Interprétation SIG :',
                [interp, 'aucune analyse possible', 'supprimer la couche', 'ignorer les métadonnées'],
                0,
                f'{cond} → {interp}.',
                nasa or 'NDVI' in cond or 'SMAP' in cond,
            ))
    advanced = [
        ('variogramme', 'modéliser la dépendance spatiale'),
        ('IDW', 'interpoler par distance inverse'),
        ('confusion matrix', 'analyser faux positifs/négatifs'),
        ('feature importance', 'identifier variables clés du modèle'),
        ('temporal composite', 'moyenner images sur une période', True),
        ('cloud mask', 'exclure pixels nuageux', True),
        ('atmospheric correction', 'corriger l\'atmosphère en télédétection', True),
        ('uncertainty map', 'cartographier l\'incertitude'),
    ]
    for i, (term, role) in enumerate(advanced):
        for j in range(5):
            n = 64 + i * 5 + j + 1
            if n > 100:
                break
            qs.append(_q(
                f'[D{n}] En analyse avancée, « {term} » :',
                [role, 'supprime la base PostGIS', 'désactive le quiz', 'mesure uniquement le vent'],
                0,
                f'{term} : {role}.',
                'NASA' in term or 'cloud' in term or 'atmospheric' in term or 'temporal' in term,
            ))
    return qs


def build_difficile():
    all_q = _difficile_static() + _difficile_generated()
    return all_q[:QUESTIONS_PER_LEVEL]


def build_all_questions():
    """Retourne {difficulty: [question_dict, ...]} avec 100 questions par niveau."""
    return {
        'facile': build_facile(),
        'moyen': build_moyen(),
        'difficile': build_difficile(),
    }


def question_count_by_level():
    banks = build_all_questions()
    return {k: len(v) for k, v in banks.items()}
