"""
Fertility classification pipeline — Random Forest / XGBoost.
Classes: faible (0), moyenne (1), elevee (2)
"""
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from soils.models import SoilPoint

ARTIFACT_DIR = Path(settings.ML_ARTIFACTS_DIR)
MODEL_FILE = ARTIFACT_DIR / 'fertility_pipeline.pkl'

NUMERIC_FEATURES = [
    'ph', 'humidity_pct', 'slope_pct', 'ndvi_3m_avg',
    'smap_moisture_avg', 'temperature', 'elevation_m',
]
CATEGORICAL_FEATURES = ['soil_type', 'season']

RECOMMENDATIONS = {
    'elevee': (
        'Fertilité élevée : entretien standard, rotation de cultures recommandée.'
    ),
    'moyenne': (
        'Fertilité moyenne : apport de matière organique, culture d\'engrais verts.'
    ),
    'faible': (
        'Fertilité faible : chaulage si acide, fertilisation ciblée, repos de la parcelle.'
    ),
}


def _season_from_month(month: int) -> str:
    return 'pluvieuse' if month in (4, 5, 6, 7, 8, 9, 10) else 'seche'


def build_training_dataframe():
    rows = []
    for p in SoilPoint.objects.filter(is_validated=True).iterator():
        month = p.collected_at.month if p.collected_at else 6
        label = p.fertility_class
        if not label:
            score = p.fertility_score
            if score is None:
                score = min(1.0, max(0.0, (p.ph - 4) / 4 * 0.4 + (p.ndvi_3m_avg or 0.4) * 0.6))
            if score < 0.4:
                label = 'faible'
            elif score < 0.7:
                label = 'moyenne'
            else:
                label = 'elevee'
        rows.append({
            'ph': p.ph,
            'humidity_pct': p.humidity_pct,
            'soil_type': p.soil_type,
            'slope_pct': p.slope_pct or 3.0,
            'ndvi_3m_avg': p.ndvi_3m_avg or 0.45,
            'smap_moisture_avg': p.smap_moisture_avg or 0.2,
            'temperature': 28.0,
            'elevation_m': p.elevation_m or 50.0,
            'season': _season_from_month(month),
            'fertility_class': label,
        })
    return pd.DataFrame(rows)


def train_and_save(algorithm: str = 'RandomForest') -> dict:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    df = build_training_dataframe()
    if len(df) < 30:
        df = _synthetic_augment(df, target=220)

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df['fertility_class']

    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])
    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore')),
    ])
    preprocessor = ColumnTransformer([
        ('num', numeric_transformer, NUMERIC_FEATURES),
        ('cat', categorical_transformer, CATEGORICAL_FEATURES),
    ])

    if algorithm == 'XGBoost':
        try:
            from xgboost import XGBClassifier  # optional: pip install xgboost
            clf = XGBClassifier(n_estimators=100, max_depth=6, verbosity=0)
        except ImportError:
            clf = RandomForestClassifier(n_estimators=120, random_state=42)
    else:
        clf = RandomForestClassifier(n_estimators=120, random_state=42)

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', clf),
    ])

    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc,
    )
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    f1 = float(f1_score(y_test, y_pred, average='macro'))
    try:
        proba = pipeline.predict_proba(X_test)
        auc = float(roc_auc_score(y_test, proba, multi_class='ovr', average='macro'))
    except Exception:
        auc = None

    cv_scores = cross_val_score(pipeline, X, y_enc, cv=5, scoring='f1_macro')
    importances = {}
    if hasattr(pipeline.named_steps['classifier'], 'feature_importances_'):
        importances = {'note': 'See sklearn feature importances post one-hot'}

    artifact = {
        'pipeline': pipeline,
        'label_encoder': le,
        'algorithm': algorithm,
    }
    joblib.dump(artifact, MODEL_FILE)

    from .models import FertilityModelRun
    FertilityModelRun.objects.filter(is_active=True).update(is_active=False)
    run = FertilityModelRun.objects.create(
        algorithm=algorithm,
        sample_count=len(df),
        f1_macro=round(f1, 4),
        auc_roc=round(auc, 4) if auc else None,
        feature_importance=importances,
        confusion_matrix=confusion_matrix(y_test, y_pred).tolist(),
        model_path=str(MODEL_FILE),
        is_active=True,
    )

    return {
        'run_id': run.id,
        'samples': len(df),
        'f1_macro': f1,
        'auc_roc': auc,
        'cv_f1_mean': float(cv_scores.mean()),
        'classification': classification_report(
            y_test, y_pred, target_names=le.classes_, output_dict=True,
        ),
    }


def _synthetic_augment(df: pd.DataFrame, target: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    rows = df.to_dict('records') if len(df) else []
    soil_types = ['argileux', 'sableux', 'limoneux', 'tourbeux', 'calcaire']
    while len(rows) < target:
        ph = rng.uniform(4.5, 8.5)
        ndvi = rng.uniform(0.15, 0.85)
        score = min(1.0, (ph - 4) / 4 * 0.35 + ndvi * 0.65)
        if score < 0.4:
            cls = 'faible'
        elif score < 0.7:
            cls = 'moyenne'
        else:
            cls = 'elevee'
        rows.append({
            'ph': ph,
            'humidity_pct': rng.uniform(10, 80),
            'soil_type': rng.choice(soil_types),
            'slope_pct': rng.uniform(0, 15),
            'ndvi_3m_avg': ndvi,
            'smap_moisture_avg': rng.uniform(0.08, 0.45),
            'temperature': rng.uniform(24, 34),
            'elevation_m': rng.uniform(0, 120),
            'season': rng.choice(['pluvieuse', 'seche']),
            'fertility_class': cls,
        })
    return pd.DataFrame(rows)


def load_artifact():
    if not MODEL_FILE.exists():
        train_and_save()
    return joblib.load(MODEL_FILE)


def _to_float(value, default):
    if value is None:
        return float(default)
    return float(value)


def predict_fertility(features: dict) -> dict:
    start = time.perf_counter()
    artifact = load_artifact()
    pipeline = artifact['pipeline']
    le = artifact['label_encoder']

    month = features.get('month', 6)
    row = {
        'ph': _to_float(features.get('ph'), 6.0),
        'humidity_pct': _to_float(features.get('humidity_pct'), 30),
        'soil_type': features.get('soil_type', 'limoneux'),
        'slope_pct': _to_float(features.get('slope_pct'), 3),
        'ndvi_3m_avg': _to_float(features.get('ndvi_3m_avg'), 0.45),
        'smap_moisture_avg': _to_float(features.get('smap_moisture_avg'), 0.2),
        'temperature': _to_float(features.get('temperature'), 28),
        'elevation_m': _to_float(features.get('elevation_m'), 50),
        'season': features.get('season') or _season_from_month(int(month)),
    }
    X = pd.DataFrame([row])
    pred_idx = pipeline.predict(X)[0]
    pred_class = le.inverse_transform([pred_idx])[0]
    proba = pipeline.predict_proba(X)[0]
    score = float(max(proba))
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        'predicted_class': pred_class,
        'confidence': round(score, 4),
        'recommendation': RECOMMENDATIONS.get(pred_class, ''),
        'inference_ms': round(elapsed_ms, 2),
        'probabilities': {
            le.classes_[i]: round(float(proba[i]), 4)
            for i in range(len(le.classes_))
        },
    }
