from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdministrator

from .models import FertilityModelRun, FertilityPredictionLog
from .pipeline import predict_fertility, train_and_save


class PredictFertilityView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        features = request.data
        if 'ph' not in features:
            return Response({'error': 'ph requis'}, status=400)
        result = predict_fertility(features)
        FertilityPredictionLog.objects.create(
            input_features=features,
            predicted_class=result['predicted_class'],
            predicted_score=result['confidence'],
            recommendation=result['recommendation'],
            inference_ms=result['inference_ms'],
        )
        return Response(result)


class TrainModelView(APIView):
    permission_classes = [IsAdministrator]

    def post(self, request):
        algo = request.data.get('algorithm', 'RandomForest')
        metrics = train_and_save(algorithm=algo)
        return Response(metrics, status=status.HTTP_201_CREATED)


def _batch_predict(request):
    ids = request.data.get('point_ids', [])
    if not ids:
        return None, Response({'error': 'point_ids requis'}, status=400)
    from soils.models import SoilPoint
    results = []
    for point in SoilPoint.objects.filter(pk__in=ids, is_validated=True)[:200]:
        result = predict_fertility({
            'ph': point.ph,
            'humidity_pct': point.humidity_pct,
            'soil_type': point.soil_type,
            'ndvi_3m_avg': point.ndvi_3m_avg,
            'smap_moisture_avg': point.smap_moisture_avg,
        })
        results.append({
            'point_id': point.id,
            'lon': point.location.x,
            'lat': point.location.y,
            **result,
        })
    return results, Response({'count': len(results), 'predictions': results})


class BatchPredictView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        results, resp = _batch_predict(request)
        if results is None:
            return resp
        return resp


class BatchPredictExportView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        import csv
        from django.http import HttpResponse
        results, resp = _batch_predict(request)
        if results is None:
            return resp
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="predictions.csv"'
        writer = csv.writer(response)
        writer.writerow(['point_id', 'lat', 'lon', 'predicted_class', 'confidence'])
        for row in results:
            writer.writerow([
                row['point_id'], row['lat'], row['lon'],
                row['predicted_class'], row['confidence'],
            ])
        return response


class ModelMetricsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        run = FertilityModelRun.objects.filter(is_active=True).first()
        if not run:
            return Response({'message': 'Aucun modèle actif — entraînement requis.'})
        return Response({
            'algorithm': run.algorithm,
            'sample_count': run.sample_count,
            'f1_macro': run.f1_macro,
            'auc_roc': run.auc_roc,
            'feature_importance': run.feature_importance,
            'confusion_matrix': run.confusion_matrix,
            'trained_at': run.trained_at,
        })
