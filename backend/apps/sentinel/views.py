from django.conf import settings
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdministrator

from .client import (
    SentinelHubError,
    clip_bbox_to_region,
    has_secret,
    is_configured,
    ndvi_mean_for_bbox,
    process_image,
    tile_xyz_to_bbox,
)
from .evalscripts import LAYER_PRESETS


def _parse_bbox_param(raw: str) -> tuple[float, float, float, float]:
    parts = [float(p.strip()) for p in raw.split(',')]
    if len(parts) != 4:
        raise ValueError('bbox attendu : min_lon,min_lat,max_lon,max_lat')
    return parts[0], parts[1], parts[2], parts[3]


class SentinelStatusView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        if not has_secret():
            return Response({
                'configured': False,
                'ok': False,
                'message': (
                    'Ajoutez SENTINEL_HUB_CLIENT_SECRET (ou SENTINEL_HUB_API_KEY) dans .env'
                ),
            })
        if not is_configured():
            return Response({
                'configured': False,
                'ok': False,
                'has_secret': True,
                'user_id': getattr(settings, 'SENTINEL_HUB_USER_ID', '') or None,
                'account_id': getattr(settings, 'SENTINEL_HUB_ACCOUNT_ID', '') or None,
                'message': (
                    'Secret OAuth OK, mais SENTINEL_HUB_CLIENT_ID manquant. '
                    'Dans apps.sentinel-hub.com → User settings → OAuth clients, '
                    'copiez la colonne « Client ID » du client lié au secret PLAK… '
                    '(ce n’est ni l’ID utilisateur ni l’ID compte).'
                ),
            })
        try:
            from .client import get_access_token
            get_access_token()
            return Response({
                'configured': True,
                'ok': True,
                'message': 'Connexion Sentinel Hub OK',
                'layers': list(LAYER_PRESETS.keys()),
            })
        except SentinelHubError as exc:
            return Response({
                'configured': True,
                'ok': False,
                'message': str(exc),
            })


class SentinelLayersView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        layers = [
            {'id': lid, **meta}
            for lid, meta in LAYER_PRESETS.items()
        ]
        return Response({
            'configured': is_configured(),
            'layers': layers,
            'tile_url_template': '/api/v1/sentinel/tiles/{layer}/{z}/{x}/{y}.png',
        })


class SentinelAnalyzeView(APIView):
    """NDVI moyen sur une bbox (région Maritime par défaut)."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        bbox_raw = request.data.get('bbox') or request.query_params.get('bbox')
        if not bbox_raw:
            bbox = settings.REGION_MARITIME_BBOX
        else:
            try:
                bbox = _parse_bbox_param(str(bbox_raw))
            except ValueError as exc:
                return Response({'detail': str(exc)}, status=400)

        clipped = clip_bbox_to_region(bbox, settings.REGION_MARITIME_BBOX)
        if clipped is None:
            return Response(
                {'detail': 'BBox hors zone pilote Maritime Togo.'},
                status=400,
            )
        days_back = int(request.data.get('days_back', 60))
        try:
            stats = ndvi_mean_for_bbox(clipped, days_back=days_back)
        except SentinelHubError as exc:
            return Response({'detail': str(exc)}, status=502)
        return Response({'bbox': clipped, **stats})


class SentinelTileView(APIView):
    """Tuile PNG Sentinel Hub pour Leaflet (Process API)."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, layer, z, x, y):
        try:
            zi, xi, yi = int(z), int(x), int(y)
        except (TypeError, ValueError):
            return Response({'detail': 'Coordonnées tuile invalides.'}, status=400)

        tile_bbox = tile_xyz_to_bbox(zi, xi, yi)
        clipped = clip_bbox_to_region(tile_bbox, settings.REGION_MARITIME_BBOX)
        if clipped is None:
            return HttpResponse(status=204)

        try:
            png = process_image(layer, clipped, width=256, height=256)
        except SentinelHubError as exc:
            return Response({'detail': str(exc)}, status=502)
        return HttpResponse(png, content_type='image/png')


class SentinelPreviewView(APIView):
    """Aperçu PNG pour une bbox (outil admin / parcelle)."""

    permission_classes = [IsAdministrator]

    def get(self, request):
        layer = request.query_params.get('layer', 'ndvi')
        bbox_raw = request.query_params.get('bbox')
        if not bbox_raw:
            return Response({'detail': 'Paramètre bbox requis.'}, status=400)
        try:
            bbox = _parse_bbox_param(bbox_raw)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        clipped = clip_bbox_to_region(bbox, settings.REGION_MARITIME_BBOX)
        if clipped is None:
            return Response({'detail': 'BBox hors zone pilote.'}, status=400)
        try:
            png = process_image(layer, clipped, width=512, height=512)
        except SentinelHubError as exc:
            return Response({'detail': str(exc)}, status=502)
        return HttpResponse(png, content_type='image/png')
