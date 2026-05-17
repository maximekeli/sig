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
