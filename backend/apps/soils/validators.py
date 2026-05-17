"""Automatic quality controls — target error rate < 2%."""


def validate_soil_point_quality(data):
    errors = {}
    ph = data.get('ph')
    humidity = data.get('humidity_pct')
    if ph is not None and (ph < 3.5 or ph > 9.5):
        errors['ph'] = 'pH hors plage valide (3,5 – 9,5).'
    if humidity is not None and (humidity < 0 or humidity > 100):
        errors['humidity_pct'] = 'Humidité hors plage (0 – 100 %).'
    loc = data.get('location')
    if loc is not None:
        lon, lat = loc.x, loc.y
        bbox = (0.9, 6.0, 1.8, 6.8)  # Maritime Togo approx
        if not (bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]):
            errors['location'] = 'Coordonnées hors Région Maritime (pilote).'
    return errors
