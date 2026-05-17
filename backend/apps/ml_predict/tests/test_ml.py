import pytest


@pytest.mark.django_db
def test_train_and_predict():
    from django.contrib.gis.geos import Point
    from soils.models import SoilPoint
    from ml_predict.pipeline import predict_fertility, train_and_save

    for i in range(50):
        SoilPoint.objects.create(
            location=Point(1.1 + i * 0.01, 6.2, srid=4326),
            ph=5.5 + (i % 10) * 0.2,
            humidity_pct=30 + i,
            soil_type='limoneux',
            collected_at='2025-01-15',
            is_validated=True,
            ndvi_3m_avg=0.4,
            fertility_class='moyenne',
        )
    metrics = train_and_save()
    assert metrics['f1_macro'] >= 0
    result = predict_fertility({'ph': 6.5, 'humidity_pct': 40, 'soil_type': 'limoneux'})
    assert result['predicted_class'] in ('faible', 'moyenne', 'elevee')
    assert result['inference_ms'] < 3000
