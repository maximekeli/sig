import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

/// File d'attente hors ligne — même format que le site web (`sig_sols_offline_queue`).
class OfflineQueueService {
  static const storageKey = 'sig_sols_offline_queue';

  Future<List<QueuedSoilPoint>> readAll() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(storageKey);
    if (raw == null || raw.isEmpty) return [];
    final list = jsonDecode(raw) as List<dynamic>;
    return list
        .map((e) => QueuedSoilPoint.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
  }

  Future<void> enqueue(Map<String, dynamic> body) async {
    final items = await readAll();
    items.add(QueuedSoilPoint(body: body, queuedAt: DateTime.now().millisecondsSinceEpoch));
    await _write(items);
  }

  Future<void> replaceAll(List<QueuedSoilPoint> items) async {
    await _write(items);
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(storageKey);
  }

  Future<void> _write(List<QueuedSoilPoint> items) async {
    final prefs = await SharedPreferences.getInstance();
    final encoded = jsonEncode(items.map((e) => e.toJson()).toList());
    await prefs.setString(storageKey, encoded);
  }

  /// Corps GeoJSON identique à frontend/js/features.js `submitAddPoint`.
  static Map<String, dynamic> buildPointBody({
    required double lat,
    required double lon,
    required double ph,
    required double humidityPct,
    required String soilType,
  }) {
    final today = DateTime.now().toIso8601String().split('T').first;
    return {
      'type': 'Feature',
      'geometry': {
        'type': 'Point',
        'coordinates': [lon, lat],
      },
      'properties': {
        'ph': ph,
        'humidity_pct': humidityPct,
        'soil_type': soilType,
        'collected_at': today,
        'source': 'terrain',
      },
    };
  }
}

class QueuedSoilPoint {
  QueuedSoilPoint({required this.body, required this.queuedAt});

  final Map<String, dynamic> body;
  final int queuedAt;

  factory QueuedSoilPoint.fromJson(Map<String, dynamic> json) => QueuedSoilPoint(
        body: Map<String, dynamic>.from(json['body'] as Map),
        queuedAt: json['queued_at'] as int? ?? 0,
      );

  Map<String, dynamic> toJson() => {
        'body': body,
        'queued_at': queuedAt,
      };
}
