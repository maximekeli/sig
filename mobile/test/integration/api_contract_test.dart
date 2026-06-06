@Tags(['integration'])
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// Contrat API — mêmes endpoints que le site web (frontend/js/) et SigApi mobile.
void main() {
  const base = 'http://localhost:8081/api/v1';
  const origin = 'http://localhost:8081';

  final publicGets = [
    '$origin/health/?detail=1',
    '$base/points/?light=1',
    '$base/dashboard/stats/',
    '$base/weather/status/',
    '$base/sentinel/status/',
    '$base/sentinel/layers/',
    '$base/assistant/status/',
    '$base/nasa/catalog/summary/',
    '$base/ml/metrics/',
    '$base/spatial/smap-correlation/',
    '$base/education/quiz/stats/',
    '$base/education/quiz/leaderboard/',
    '$base/education/sheets/',
    '$base/videos/posts/?kind=video',
  ];

  final authGets = [
    '$base/auth/profile/',
    '$base/auth/feed/',
    '$base/education/quiz/badges/',
    '$base/platform/notifications/',
    '$base/platform/notifications/unread-count/',
    '$base/videos/stories/',
  ];

  test('Contrat API web/mobile — endpoints publics + auth', () async {
    if (!await _ping('$origin/health/')) {
      markTestSkipped('Backend indisponible — sudo ./scripts/fix-docker-network.sh');
      return;
    }

    for (final url in publicGets) {
      final res = await _get(url);
      expect(res.statusCode, 200, reason: 'GET $url');
    }

    final health = jsonDecode((await _get('$origin/health/?detail=1')).body) as Map;
    final dbInfo = (health['checks'] as Map)['database_info'] as Map;
    expect(dbInfo['clients'], 'web,mobile');

    final login = await _post('$base/auth/token/', {
      'username': 'admin',
      'password': 'admin123',
    });
    expect(login.statusCode, 200);
    final token = (jsonDecode(login.body) as Map)['access'] as String;

    for (final url in authGets) {
      final res = await _get(url, token: token);
      expect(res.statusCode, 200, reason: 'GET $url');
    }

    final unread = jsonDecode(
      (await _get('$base/platform/notifications/unread-count/', token: token)).body,
    ) as Map;
    expect(unread.containsKey('unread_count') || unread.containsKey('count'), isTrue);

    final pointBody = {
      'type': 'Feature',
      'geometry': {'type': 'Point', 'coordinates': [1.27, 6.37]},
      'properties': {
        'ph': 6.5,
        'humidity_pct': 30,
        'soil_type': 'limoneux',
        'collected_at': '2026-06-01',
        'source': 'terrain',
      },
    };
    final create = await _post('$base/points/', pointBody, token: token);
    expect(create.statusCode, isIn([200, 201]), reason: 'POST /points/');

    final parcel = await _post('$base/spatial/parcel/live/', {
      'geometry': {
        'type': 'Polygon',
        'coordinates': [
          [
            [1.34, 6.39],
            [1.36, 6.39],
            [1.36, 6.41],
            [1.34, 6.41],
            [1.34, 6.39],
          ],
        ],
      },
      'use_sentinel': false,
      'use_weather': false,
      'use_ml': false,
    });
    expect(parcel.statusCode, 200, reason: 'POST /spatial/parcel/live/');
  });
}

Future<bool> _ping(String url) async {
  try {
    final client = HttpClient()..connectionTimeout = const Duration(seconds: 5);
    final req = await client.getUrl(Uri.parse(url));
    final res = await req.close().timeout(const Duration(seconds: 8));
    final ok = res.statusCode == 200;
    await res.drain();
    client.close(force: true);
    return ok;
  } catch (_) {
    return false;
  }
}

Future<_HttpRes> _get(String url, {String? token}) async {
  final client = HttpClient()..connectionTimeout = const Duration(seconds: 5);
  final req = await client.getUrl(Uri.parse(url));
  if (token != null) req.headers.set('Authorization', 'Bearer $token');
  final res = await req.close().timeout(const Duration(seconds: 15));
  final body = await res.transform(utf8.decoder).join();
  client.close(force: true);
  return _HttpRes(res.statusCode, body);
}

Future<_HttpRes> _post(String url, Map<String, dynamic> data, {String? token}) async {
  final client = HttpClient()..connectionTimeout = const Duration(seconds: 5);
  final req = await client.postUrl(Uri.parse(url));
  req.headers.contentType = ContentType.json;
  if (token != null) req.headers.set('Authorization', 'Bearer $token');
  req.write(jsonEncode(data));
  final res = await req.close().timeout(const Duration(seconds: 30));
  final body = await res.transform(utf8.decoder).join();
  client.close(force: true);
  return _HttpRes(res.statusCode, body);
}

class _HttpRes {
  _HttpRes(this.statusCode, this.body);
  final int statusCode;
  final String body;
}
