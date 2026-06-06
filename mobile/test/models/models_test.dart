import 'package:flutter_test/flutter_test.dart';
import 'package:sig_sols_mobile/models/parcel_analysis.dart';
import 'package:sig_sols_mobile/models/soil_point.dart';
import 'package:sig_sols_mobile/models/user.dart';

void main() {
  group('AppUser', () {
    test('fromJson et displayName', () {
      final user = AppUser.fromJson({
        'id': 1,
        'username': 'admin',
        'first_name': 'Max',
        'last_name': 'Keli',
        'role': 'admin',
        'email': 'a@test.tg',
      });
      expect(user.displayName, 'Max Keli');
      expect(user.isAdmin, isTrue);
      expect(user.isAgent, isTrue);
    });

    test('displayName fallback username', () {
      final user = AppUser.fromJson({'id': 2, 'username': 'agent1', 'role': 'agent'});
      expect(user.displayName, 'agent1');
      expect(user.isAgent, isTrue);
      expect(user.isAdmin, isFalse);
    });
  });

  group('SoilPoint', () {
    test('fromJson avec lat/lon directs', () {
      final p = SoilPoint.fromJson({
        'id': 10,
        'lat': 6.4,
        'lon': 1.35,
        'ph': 6.2,
        'soil_type': 'ferralitique',
      });
      expect(p.lat, 6.4);
      expect(p.lon, 1.35);
      expect(p.ph, 6.2);
    });

    test('fromJson avec GeoJSON location', () {
      final p = SoilPoint.fromJson({
        'id': 11,
        'location': {
          'type': 'Point',
          'coordinates': [1.25, 6.12],
        },
        'ph': 5.8,
      });
      expect(p.lon, 1.25);
      expect(p.lat, 6.12);
    });
  });

  group('ParcelAnalysis', () {
    test('fromJson avec weather et sentinel', () {
      final a = ParcelAnalysis.fromJson({
        'parcel_name': 'Test parcelle',
        'centroid': {'lat': 6.1, 'lon': 1.2},
        'area': {'area_ha': 12.5},
        'soil_points': {'count': 3},
        'weather': {'configured': true, 'current': {'temp_c': 28}},
        'sentinel': {'ndvi_mean': 0.45},
        'recommendations': ['Irriguer', 'Surveiller NDVI'],
        'health_index': 0.72,
      });
      expect(a.parcelName, 'Test parcelle');
      expect(a.areaHa, 12.5);
      expect(a.soilPointsCount, 3);
      expect(a.weather?['configured'], isTrue);
      expect(a.sentinel?['ndvi_mean'], 0.45);
      expect(a.recommendations, hasLength(2));
      expect(a.healthIndex, 0.72);
    });
  });
}
