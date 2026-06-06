@Tags(['integration'])
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// Tests API réels (backend Docker requis).
/// `flutter test --tags integration`
void main() {
  test('API backend — health, auth, weather, sentinel, points', () async {
    const base = 'http://localhost:8081/api/v1';

    if (!await _ping('http://localhost:8081/health/')) {
      markTestSkipped('Backend indisponible — lancez: docker compose up -d');
    }

    final health = await _get('http://localhost:8081/health/');
    expect(health.statusCode, 200);
    expect((jsonDecode(health.body) as Map)['status'], 'ok');

    final login = await _post('$base/auth/token/', {
      'username': 'admin',
      'password': 'admin123',
    });
    expect(login.statusCode, 200);
    final loginBody = jsonDecode(login.body) as Map<String, dynamic>;
    expect(loginBody['access'], isNotEmpty);
    expect((loginBody['user'] as Map)['username'], 'admin');

    final weather = await _get('$base/weather/status/');
    expect(weather.statusCode, 200);
    expect((jsonDecode(weather.body) as Map)['configured'], isTrue);

    final sentinel = await _get('$base/sentinel/status/');
    expect(sentinel.statusCode, 200);
    expect((jsonDecode(sentinel.body) as Map)['configured'], isTrue);

    final points = await _get('$base/points/?light=1&limit=5');
    expect(points.statusCode, 200);
    expect(points.body.isNotEmpty, isTrue);
  });
}

Future<bool> _ping(String url) async {
  try {
    final client = HttpClient()..connectionTimeout = const Duration(seconds: 3);
    final req = await client.getUrl(Uri.parse(url));
    final res = await req.close().timeout(const Duration(seconds: 5));
    final ok = res.statusCode == 200;
    await res.drain();
    client.close(force: true);
    return ok;
  } catch (_) {
    return false;
  }
}

Future<_HttpRes> _get(String url) async {
  final client = HttpClient()..connectionTimeout = const Duration(seconds: 5);
  final req = await client.getUrl(Uri.parse(url));
  final res = await req.close().timeout(const Duration(seconds: 10));
  final body = await res.transform(utf8.decoder).join();
  client.close(force: true);
  return _HttpRes(res.statusCode, body);
}

Future<_HttpRes> _post(String url, Map<String, dynamic> data) async {
  final client = HttpClient()..connectionTimeout = const Duration(seconds: 5);
  final req = await client.postUrl(Uri.parse(url));
  req.headers.contentType = ContentType.json;
  req.write(jsonEncode(data));
  final res = await req.close().timeout(const Duration(seconds: 15));
  final body = await res.transform(utf8.decoder).join();
  client.close(force: true);
  return _HttpRes(res.statusCode, body);
}

class _HttpRes {
  _HttpRes(this.statusCode, this.body);
  final int statusCode;
  final String body;
}
