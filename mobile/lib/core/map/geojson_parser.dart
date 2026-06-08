import 'package:latlong2/latlong.dart';

/// Parse GeoJSON FeatureCollection → polygones pour flutter_map.
class GeoJsonZone {
  GeoJsonZone({
    required this.code,
    required this.name,
    required this.zoneType,
    required this.rings,
  });

  final String code;
  final String name;
  final String zoneType;
  final List<List<LatLng>> rings;
}

List<GeoJsonZone> parseZonesGeoJson(Map<String, dynamic> geojson) {
  final features = geojson['features'] as List? ?? [];
  final zones = <GeoJsonZone>[];
  for (final f in features) {
    final feature = Map<String, dynamic>.from(f as Map);
    final props = Map<String, dynamic>.from(feature['properties'] as Map? ?? {});
    final geom = Map<String, dynamic>.from(feature['geometry'] as Map? ?? {});
    final rings = _ringsFromGeometry(geom);
    if (rings.isEmpty) continue;
    zones.add(GeoJsonZone(
      code: props['code']?.toString() ?? '',
      name: props['name']?.toString() ?? props['code']?.toString() ?? 'Zone',
      zoneType: props['zone_type']?.toString() ?? 'canton',
      rings: rings,
    ));
  }
  return zones;
}

List<List<LatLng>> _ringsFromGeometry(Map<String, dynamic> geom) {
  final type = geom['type']?.toString();
  final coords = geom['coordinates'];
  if (coords == null) return [];

  if (type == 'Polygon') {
    return [_ringFromCoords(coords as List)];
  }
  if (type == 'MultiPolygon') {
    return (coords as List)
        .map((poly) => _ringFromCoords((poly as List).first as List))
        .toList();
  }
  return [];
}

List<LatLng> _ringFromCoords(List ring) {
  return ring
      .map((c) {
        final pair = c as List;
        return LatLng((pair[1] as num).toDouble(), (pair[0] as num).toDouble());
      })
      .toList();
}
