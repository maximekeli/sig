import '../core/api/api_client.dart';
import '../models/parcel_analysis.dart';
import '../models/soil_point.dart';

/// Façade API — mêmes endpoints que le site web.
class SigApi {
  SigApi(this._client);

  final ApiClient _client;

  // --- Carte / sols ---
  Future<List<SoilPoint>> fetchSoilPoints({bool light = true}) async {
    final data = await _client.get<dynamic>(
      '/points/',
      query: {'light': light ? '1' : '0', 'is_validated': 'true'},
    );
    final list = data is Map ? (data['results'] as List? ?? data['features'] as List? ?? []) : data as List;
    return list.map((e) => SoilPoint.fromJson(Map<String, dynamic>.from(e as Map))).toList();
  }

  Future<Map<String, dynamic>> fetchDashboardStats() =>
      _client.get('/dashboard/stats/');

  Future<Map<String, dynamic>> fetchMlMetrics() => _client.get('/ml/metrics/');

  // --- Parcelle ---
  Future<ParcelAnalysis> analyzeParcelAt(double lat, double lon) async {
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
    final data = await _client.post<Map<String, dynamic>>(
      '/spatial/parcel/live/',
      data: {
        'geometry': geometry,
        'use_sentinel': true,
        'use_weather': true,
        'use_ml': true,
      },
    );
    return ParcelAnalysis.fromJson(data);
  }

  // --- Météo ---
  Future<Map<String, dynamic>> weatherStatus() => _client.get('/weather/status/');

  Future<Map<String, dynamic>> weatherCurrent(double lat, double lon) =>
      _client.get('/weather/current/', query: {'lat': lat, 'lon': lon});

  Future<Map<String, dynamic>> weatherForecast(double lat, double lon) =>
      _client.get('/weather/forecast/', query: {'lat': lat, 'lon': lon});

  // --- Sentinel ---
  Future<Map<String, dynamic>> sentinelStatus() => _client.get('/sentinel/status/');

  // --- Quiz / éducation ---
  Future<Map<String, dynamic>> quizStats() => _client.get('/education/quiz/stats/');

  Future<Map<String, dynamic>> startQuiz() =>
      _client.post('/education/quiz/start/');

  Future<dynamic> quizLeaderboard() =>
      _client.get('/education/quiz/leaderboard/');

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

  // --- Assistant ---
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

  // --- Notifications ---
  Future<List<dynamic>> fetchNotifications() async {
    final data = await _client.get<dynamic>('/platform/notifications/');
    if (data is List) return data;
    return (data as Map)['results'] as List? ?? [];
  }

  Future<int> unreadNotifications() async {
    final data = await _client.get<Map<String, dynamic>>('/platform/notifications/unread-count/');
    return data['count'] as int? ?? 0;
  }

  // --- GPS ---
  Future<void> updateLocation(double lat, double lon) =>
      _client.post('/auth/location/', data: {'lat': lat, 'lon': lon});
}
