# L1 — Spécifications fonctionnelles (synthèse)

**Projet** : SIG-SOLS-TOGO-2026-01  
**Version** : 3.0 — Mai 2026

## Cas d'utilisation principaux

| ID | Acteur | Cas d'utilisation |
|----|--------|-------------------|
| UC01 | Agent | Consulter carte des points de sol |
| UC02 | Agent | Saisir / importer point terrain |
| UC03 | Agent | Recherche proximité (100 m – 10 km) |
| UC04 | Chercheur | Export GeoJSON / CSV |
| UC05 | Tous | Superposer couches NASA |
| UC06 | Agriculteur | Prédire fertilité (IA) |
| UC07 | Étudiant | Quiz et badges |
| UC08 | Admin | Gestion utilisateurs, ingestion NASA |
| UC09 | Admin | Déclencher réentraînement IA |

## Règles de gestion

- RG01 : pH ∈ [3,5 ; 9,5]
- RG02 : Coordonnées pilote dans bbox Région Maritime
- RG03 : JWT expire après 1 h
- RG04 : Rôle Agent requis pour import
- RG05 : Crédit NASA obligatoire sur publications

## Objectifs de service

- Affichage 500 points &lt; 2 s
- API spatiale &lt; 2 s
- Inférence IA &lt; 300 ms
- Disponibilité cible 99 %
