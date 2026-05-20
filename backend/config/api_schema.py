"""Schéma OpenAPI minimal (liste des endpoints principaux)."""
from django.http import JsonResponse


def api_schema(_request):
    return JsonResponse({
        'openapi': '3.0.3',
        'info': {
            'title': 'SIG Sols Togo API',
            'version': '1.0.0',
            'description': 'SIG-SOLS-TOGO-2026-01 — DISIA / DUSOL',
        },
        'paths': {
            '/api/v1/auth/token/': {'post': {'summary': 'JWT login'}},
            '/api/v1/auth/register/': {'post': {'summary': 'Inscription'}},
            '/api/v1/points/': {'get': {'summary': 'Liste points'}, 'post': {'summary': 'Créer point'}},
            '/api/v1/points/import_data/': {'post': {'summary': 'Import GeoJSON/CSV'}},
            '/api/v1/points/compare/': {'get': {'summary': 'Comparer deux points (a, b)'}},
            '/api/v1/spatial/parcel/zones/geojson/': {'get': {'summary': 'Parcelles GeoJSON (carte)'}},
            '/api/v1/spatial/parcel/live/': {'get': {'summary': 'Infos parcelle temps réel'}, 'post': {'summary': 'Infos parcelle (géométrie)'}},
            '/api/v1/nasa/ingest/': {'post': {'summary': 'Ingestion NASA (admin)'}},
            '/api/v1/points/?bbox=': {'get': {'summary': 'Liste filtrée par bbox'}},
            '/api/v1/spatial/proximity/': {'get': {'summary': 'Proximité GPS'}},
            '/api/v1/ml/predict/': {'post': {'summary': 'Prédiction fertilité'}},
            '/api/v1/ml/train/': {'post': {'summary': 'Réentraînement IA (admin)'}},
            '/api/v1/education/sheets/{id}/pdf/': {'get': {'summary': 'PDF fiche pédagogique (long)'}},
            '/api/v1/platform/admin/dashboard/': {'get': {'summary': 'Dashboard admin'}},
            '/api/v1/assistant/status/': {'get': {'summary': 'Statut assistant IA Gemini'}},
            '/api/v1/assistant/chat/': {'post': {'summary': 'Chat assistant IA'}},
            '/api/v1/dashboard/stats/': {'get': {'summary': 'KPIs sols'}},
        },
    })
