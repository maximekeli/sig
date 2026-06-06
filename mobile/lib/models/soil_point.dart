class SoilPoint {
  SoilPoint({
    required this.id,
    required this.lat,
    required this.lon,
    this.ph,
    this.humidityPct,
    this.soilType,
    this.fertilityClass,
    this.fertilityScore,
    this.ndvi3mAvg,
    this.validationStatus,
    this.phColor,
  });

  final int id;
  final double lat;
  final double lon;
  final double? ph;
  final double? humidityPct;
  final String? soilType;
  final String? fertilityClass;
  final double? fertilityScore;
  final double? ndvi3mAvg;
  final String? validationStatus;
  final String? phColor;

  factory SoilPoint.fromJson(Map<String, dynamic> json) {
    double? lat = (json['lat'] as num?)?.toDouble();
    double? lon = (json['lon'] as num?)?.toDouble();
    final loc = json['location'];
    if (loc is Map && loc['coordinates'] is List) {
      final coords = loc['coordinates'] as List;
      if (coords.length >= 2) {
        lon ??= (coords[0] as num).toDouble();
        lat ??= (coords[1] as num).toDouble();
      }
    }
    return SoilPoint(
      id: json['id'] as int,
      lat: lat ?? 0,
      lon: lon ?? 0,
      ph: (json['ph'] as num?)?.toDouble(),
      humidityPct: (json['humidity_pct'] as num?)?.toDouble(),
      soilType: json['soil_type'] as String?,
      fertilityClass: json['fertility_class'] as String?,
      fertilityScore: (json['fertility_score'] as num?)?.toDouble(),
      ndvi3mAvg: (json['ndvi_3m_avg'] as num?)?.toDouble(),
      validationStatus: json['validation_status'] as String?,
      phColor: json['ph_color'] as String?,
    );
  }
}
