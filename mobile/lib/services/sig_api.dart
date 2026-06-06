import 'package:dio/dio.dart';

import '../core/api/api_client.dart';
import '../core/config/env.dart';
import '../models/parcel_analysis.dart';
import '../models/soil_point.dart';

/// Façade API — mêmes endpoints que le site web (frontend/js/).
class SigApi {
  SigApi(this._client);

  final ApiClient _client;

  // --- Sols / dashboard ---
  /// Création point sol (GeoJSON Feature — même format que le site web).
  Future<Map<String, dynamic>> createSoilPoint(Map<String, dynamic> geoJsonBody) =>
      _client.post('/points/', data: geoJsonBody);

  Future<List<SoilPoint>> fetchSoilPoints({bool light = true}) async {
    final data = await _client.get<dynamic>(
      '/points/',
      query: {'light': light ? '1' : '0', 'is_validated': 'true'},
    );
    final list = data is Map
        ? (data['results'] as List? ?? data['features'] as List? ?? [])
        : data as List;
    return list
        .map((e) => SoilPoint.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
  }

  Future<Map<String, dynamic>> fetchDashboardStats() =>
      _client.get('/dashboard/stats/');

  /// Santé backend + base de données (PostGIS partagée web/mobile).
  Future<Map<String, dynamic>> fetchSystemHealth() async {
    final dio = Dio(BaseOptions(
      connectTimeout: const Duration(seconds: 8),
      receiveTimeout: const Duration(seconds: 12),
    ));
    final res = await dio.get<Map<String, dynamic>>(Env.healthUrl);
    return Map<String, dynamic>.from(res.data ?? {});
  }

  Future<Map<String, dynamic>> fetchMlMetrics() => _client.get('/ml/metrics/');

  Future<Map<String, dynamic>> predictFertility({
    required double lat,
    required double lon,
    int? pointId,
  }) =>
      _client.post('/ml/predict/', data: {
        if (pointId != null) 'point_id': pointId,
        'lat': lat,
        'lon': lon,
      });

  // --- NASA ---
  Future<Map<String, dynamic>> nasaCatalogSummary() =>
      _client.get('/nasa/catalog/summary/');

  Future<List<dynamic>> nasaLayers() async {
    final data = await _client.get<dynamic>('/nasa/layers/');
    if (data is List) return data;
    return (data as Map)['results'] as List? ?? [];
  }

  // --- Sentinel Hub ---
  Future<Map<String, dynamic>> sentinelStatus() =>
      _client.get('/sentinel/status/');

  Future<Map<String, dynamic>> sentinelLayers() =>
      _client.get('/sentinel/layers/');

  Future<Map<String, dynamic>> sentinelAnalyze({
    required double minLon,
    required double minLat,
    required double maxLon,
    required double maxLat,
  }) =>
      _client.post('/sentinel/analyze/', data: {
        'bbox': [minLon, minLat, maxLon, maxLat],
      });

  // --- OpenWeather ---
  Future<Map<String, dynamic>> weatherStatus() =>
      _client.get('/weather/status/');

  Future<Map<String, dynamic>> weatherCurrent(double lat, double lon) =>
      _client.get('/weather/current/', query: {'lat': lat, 'lon': lon});

  Future<Map<String, dynamic>> weatherForecast(double lat, double lon) =>
      _client.get('/weather/forecast/', query: {'lat': lat, 'lon': lon});

  // --- Gemini / Assistant ---
  Future<Map<String, dynamic>> assistantStatus() =>
      _client.get('/assistant/status/');

  Future<Map<String, dynamic>> assistantChat({
    required String message,
    List<Map<String, String>> history = const [],
    Map<String, dynamic>? context,
  }) =>
      _client.post('/assistant/chat/', data: {
        'message': message,
        'history': history,
        'context': context ?? {},
      });

  // --- Spatial / parcelle ---
  Future<List<dynamic>> parcelZones({String? zoneType}) async {
    final data = await _client.get<dynamic>(
      '/spatial/parcel/zones/',
      query: zoneType != null ? {'zone_type': zoneType} : null,
    );
    if (data is List) return data;
    return (data as Map)['results'] as List? ?? data['zones'] as List? ?? [];
  }

  Future<Map<String, dynamic>> parcelZonesGeoJson({String types = 'canton,degraded'}) =>
      _client.get('/spatial/parcel/zones/geojson/', query: {'types': types});

  Future<ParcelAnalysis> analyzeParcelLive({
    required Map<String, dynamic> geometry,
    bool useSentinel = true,
    bool useWeather = true,
    bool useMl = true,
    String? zoneCode,
  }) async {
    final data = await _client.post<Map<String, dynamic>>(
      '/spatial/parcel/live/',
      data: {
        'geometry': geometry,
        'use_sentinel': useSentinel,
        'use_weather': useWeather,
        'use_ml': useMl,
        if (zoneCode != null) 'zone_code': zoneCode,
      },
    );
    return ParcelAnalysis.fromJson(data);
  }

  Future<ParcelAnalysis> analyzeParcelAt(double lat, double lon) {
    final geometry = {
      'type': 'Polygon',
      'coordinates': [
        [
          [lon - 0.01, lat - 0.01],
          [lon + 0.01, lat - 0.01],
          [lon + 0.01, lat + 0.01],
          [lon - 0.01, lat + 0.01],
          [lon - 0.01, lat - 0.01],
        ],
      ],
    };
    return analyzeParcelLive(geometry: geometry);
  }

  Future<Map<String, dynamic>> ndviTimeseries(int pointId) =>
      _client.get('/spatial/ndvi-timeseries/$pointId/');

  Future<Map<String, dynamic>> proximity({
    required double lat,
    required double lon,
    int radiusM = 5000,
  }) =>
      _client.get('/spatial/proximity/', query: {
        'lat': lat,
        'lon': lon,
        'radius_m': radiusM,
      });

  Future<Map<String, dynamic>> smapCorrelation() =>
      _client.get('/spatial/smap-correlation/');

  // --- Éducation / quiz ---
  Future<Map<String, dynamic>> quizStats() =>
      _client.get('/education/quiz/stats/');

  Future<Map<String, dynamic>> startQuiz({
    String difficulty = 'facile',
    int count = 10,
    bool examMode = false,
  }) =>
      _client.post('/education/quiz/start/', data: {
        'difficulty': difficulty,
        'count': count,
        'exam_mode': examMode,
      });

  Future<Map<String, dynamic>> submitQuizAnswer(
    int sessionId, {
    required int questionId,
    required int selectedIndex,
  }) =>
      _client.post('/education/quiz/$sessionId/answer/', data: {
        'question_id': questionId,
        'selected_index': selectedIndex,
      });

  Future<Map<String, dynamic>> finishQuiz(int sessionId) =>
      _client.post('/education/quiz/$sessionId/finish/');

  Future<dynamic> quizLeaderboard() =>
      _client.get('/education/quiz/leaderboard/');

  Future<List<dynamic>> quizBadges() async {
    final data = await _client.get<dynamic>('/education/quiz/badges/');
    if (data is List) return data;
    return (data as Map)['badges'] as List? ?? [];
  }

  Future<List<dynamic>> fetchSheets() async {
    final data = await _client.get<dynamic>('/education/sheets/');
    if (data is List) return data;
    return (data as Map)['results'] as List? ?? [];
  }

  // --- Vidéos ---
  Future<List<dynamic>> fetchVideos({String kind = 'video'}) async {
    final data = await _client.get<dynamic>(
      '/videos/posts/',
      query: {'kind': kind},
    );
    if (data is List) return data;
    return (data as Map)['results'] as List? ?? [];
  }

  Future<void> toggleVideoLike(int postId) =>
      _client.post('/videos/posts/$postId/toggle_like/');

  Future<List<dynamic>> fetchStories() async {
    final data = await _client.get<dynamic>('/videos/stories/');
    if (data is List) return data;
    return (data as Map)['results'] as List? ?? [];
  }

  // --- Communauté ---
  Future<List<dynamic>> fetchFeed() async {
    final data = await _client.get<dynamic>('/auth/feed/');
    if (data is List) return data;
    return (data as Map)['results'] as List? ?? [];
  }

  Future<List<dynamic>> searchUsers(String query) async {
    final data = await _client.get<dynamic>(
      '/auth/users/search/',
      query: {'q': query},
    );
    if (data is List) return data;
    return (data as Map)['results'] as List? ?? [];
  }

  Future<void> followUser(String username) =>
      _client.post('/auth/users/$username/follow/');

  Future<void> unfollowUser(String username) =>
      _client.delete('/auth/users/$username/follow/');

  // --- Notifications / GPS ---
  Future<List<dynamic>> fetchNotifications() async {
    final data = await _client.get<dynamic>('/platform/notifications/');
    if (data is List) return data;
    return (data as Map)['results'] as List? ?? [];
  }

  Future<int> unreadNotifications() async {
    final data =
        await _client.get<Map<String, dynamic>>('/platform/notifications/unread-count/');
    return data['unread_count'] as int? ?? data['count'] as int? ?? 0;
  }

  Future<void> updateLocation(double lat, double lon) =>
      _client.post('/auth/location/', data: {'lat': lat, 'lon': lon});

  /// Statuts de toutes les APIs externes (comme le dashboard web).
  Future<Map<String, Map<String, dynamic>>> fetchExternalApiStatus() async {
    final results = await Future.wait([
      weatherStatus(),
      sentinelStatus(),
      assistantStatus(),
      nasaCatalogSummary(),
      fetchMlMetrics(),
    ]);
    return {
      'weather': Map<String, dynamic>.from(results[0] as Map),
      'sentinel': Map<String, dynamic>.from(results[1] as Map),
      'assistant': Map<String, dynamic>.from(results[2] as Map),
      'nasa': Map<String, dynamic>.from(results[3] as Map),
      'ml': Map<String, dynamic>.from(results[4] as Map),
    };
  }
}
