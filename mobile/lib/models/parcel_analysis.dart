class ParcelAnalysis {
  ParcelAnalysis({
    required this.parcelName,
    this.areaHa,
    this.centroidLat,
    this.centroidLon,
    this.weather,
    this.sentinel,
    this.soilPointsCount,
    this.healthIndex,
    this.recommendations = const [],
    this.raw,
  });

  final String parcelName;
  final double? areaHa;
  final double? centroidLat;
  final double? centroidLon;
  final Map<String, dynamic>? weather;
  final Map<String, dynamic>? sentinel;
  final int? soilPointsCount;
  final double? healthIndex;
  final List<String> recommendations;
  final Map<String, dynamic>? raw;

  factory ParcelAnalysis.fromJson(Map<String, dynamic> json) {
    final centroid = json['centroid'] as Map<String, dynamic>?;
    final area = json['area'] as Map<String, dynamic>?;
    final soil = json['soil_points'] as Map<String, dynamic>?;
    final recs = json['recommendations'];
    return ParcelAnalysis(
      parcelName: json['parcel_name'] as String? ?? 'Parcelle',
      areaHa: (area?['area_ha'] as num?)?.toDouble(),
      centroidLat: (centroid?['lat'] as num?)?.toDouble(),
      centroidLon: (centroid?['lon'] as num?)?.toDouble(),
      weather: json['weather'] as Map<String, dynamic>?,
      sentinel: json['sentinel'] as Map<String, dynamic>?,
      soilPointsCount: soil?['count'] as int?,
      healthIndex: (json['health_index'] as num?)?.toDouble(),
      recommendations: recs is List
          ? recs.map((e) => e.toString()).toList()
          : const [],
      raw: json,
    );
  }
}
