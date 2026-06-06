import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sig_sols_mobile/core/offline/offline_queue_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  test('buildPointBody format GeoJSON identique au web', () {
    final body = OfflineQueueService.buildPointBody(
      lat: 6.4,
      lon: 1.35,
      ph: 6.2,
      humidityPct: 35,
      soilType: 'limoneux',
    );
    expect(body['type'], 'Feature');
    expect(body['geometry']['type'], 'Point');
    expect(body['geometry']['coordinates'], [1.35, 6.4]);
    expect(body['properties']['ph'], 6.2);
    expect(body['properties']['humidity_pct'], 35);
    expect(body['properties']['soil_type'], 'limoneux');
    expect(body['properties']['source'], 'terrain');
    expect(body['properties']['collected_at'], isNotEmpty);
  });

  test('enqueue et readAll persistent la file', () async {
    final queue = OfflineQueueService();
    final body = OfflineQueueService.buildPointBody(
      lat: 1, lon: 2, ph: 7, humidityPct: 40, soilType: 'argileux',
    );
    await queue.enqueue(body);
    final items = await queue.readAll();
    expect(items.length, 1);
    expect(items.first.body['properties']['soil_type'], 'argileux');
    expect(items.first.queuedAt, greaterThan(0));
  });

  test('replaceAll met à jour la file', () async {
    final queue = OfflineQueueService();
    await queue.enqueue({'body': {'x': 1}});
    await queue.replaceAll([]);
    expect(await queue.readAll(), isEmpty);
  });

  test('QueuedSoilPoint round-trip JSON', () {
    final item = QueuedSoilPoint(
      body: {'type': 'Feature'},
      queuedAt: 12345,
    );
    final restored = QueuedSoilPoint.fromJson(item.toJson());
    expect(restored.body['type'], 'Feature');
    expect(restored.queuedAt, 12345);
  });
}
