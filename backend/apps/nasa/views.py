from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdministrator

from .ingestion import ingest_all
from .models import NasaLayerCatalog
from .serializers import NasaLayerSerializer


class NasaLayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NasaLayerCatalog.objects.filter(is_active=True)
    serializer_class = NasaLayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['product']


class NasaIngestTriggerView(APIView):
    permission_classes = [IsAdministrator]

    def post(self, request):
        from .ingestion import enrich_soil_points_from_rasters
        result = ingest_all()
        if request.data.get('enrich_points', True):
            result['soil_points_enriched'] = enrich_soil_points_from_rasters()
        return Response({'ingested': result})


class NasaEnrichPointsView(APIView):
    """Extract NDVI/SMAP from cached rasters onto soil points (rasterio)."""
    permission_classes = [IsAdministrator]

    def post(self, request):
        from .ingestion import enrich_soil_points_from_rasters
        limit = int(request.data.get('limit', 200))
        n = enrich_soil_points_from_rasters(limit=limit)
        return Response({'updated': n})


class NasaTilePlaceholderView(APIView):
    """1x1 transparent PNG for layer toggle demo without real tiles."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, product, date_str, z, x, y):
        # Minimal valid PNG (1x1 transparent)
        png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        return HttpResponse(png, content_type='image/png')


class NasaCatalogSummaryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        from django.db.models import Count
        summary = (
            NasaLayerCatalog.objects.values('product')
            .annotate(count=Count('id'))
            .order_by('product')
        )
        return Response({
            'total_layers': NasaLayerCatalog.objects.count(),
            'by_product': list(summary),
            'products': [c[0] for c in NasaLayerCatalog.Product.choices],
        })
