import 'package:flutter_test/flutter_test.dart';
import 'package:sig_sols_mobile/core/map/geojson_parser.dart';

void main() {
  test('parseZonesGeoJson extrait canton', () {
    final zones = parseZonesGeoJson({
      'type': 'FeatureCollection',
      'features': [
        {
          'type': 'Feature',
          'properties': {'code': 'CANTON-M01', 'name': 'Canton Test', 'zone_type': 'canton'},
          'geometry': {
            'type': 'Polygon',
            'coordinates': [
              [
                [1.2, 6.3],
                [1.3, 6.3],
                [1.3, 6.4],
                [1.2, 6.4],
                [1.2, 6.3],
              ],
            ],
          },
        },
      ],
    });
    expect(zones.length, 1);
    expect(zones.first.code, 'CANTON-M01');
    expect(zones.first.rings.first.length, 5);
  });
}
