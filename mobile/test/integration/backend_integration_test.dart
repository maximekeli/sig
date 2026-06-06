import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// Tests d'intégration contre le backend Django réel (localhost:8081).
/// Ignorés automatiquement si le serveur ne répond pas.
void main() {
  const base = 'http://localhost:8081/api/v1';
  late bool backendUp;

  setUpAll(() async {
    backendUp = await _ping('http://localhost:8081/health/');
  });

  test('health endpoint', () async {
    if (!backendUp) {
      markTestSkipped('Backend indisponible — lancez: docker compose up -d');
    }
    final res = await _get('http://localhost:8081/health/');
    expect(res.statusCode, 200);
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    expect(body['status'], 'ok');
  });

  test('login admin', () async {
    if (!backendUp) markTestSkipped('Backend indisponible');
    final res = await _post('$base/auth/token/', {
      'username': 'admin',
      'password': 'admin123',
    });
    expect(res.statusCode, 200);
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    expect(body['access'], isNotEmpty);
    expect(body['user'], isA<Map>());
    expect((body['user'] as Map)['username'], 'admin');
  });

  test('weather status', () async {
    if (!backendUp) markTestSkipped('Backend indisponible');
    final res = await _get('$base/weather/status/');
    expect(res.statusCode, 200);
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    expect(body['configured'], isTrue);
  });

  test('sentinel status', () async {
    if (!backendUp) markTestSkipped('Backend indisponible');
    final res = await _get('$base/sentinel/status/');
    expect(res.statusCode, 200);
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    expect(body['configured'], isTrue);
  });

  test('points sol liste', () async {
    if (!backendUp) markTestSkipped('Backend indisponible');
    final res = await _get('$base/points/?light=1&limit=5');
    expect(res.statusCode, 200);
    expect(res.body.isNotEmpty, isTrue);
  });
}

Future<bool> _ping(String url) async {
  try {
    final client = HttpClient()..connectionTimeout = const Duration(seconds: 5);
    final req = await client.getUrl(Uri.parse(url));
    final res = await req.close().timeout(const Duration(seconds: 8));
    await res.drain();
    client.close();
    return res.statusCode == 200;
  } catch (_) {
    return false;
  }
}

Future<_HttpRes> _get(String url) async {
  final client = HttpClient()..connectionTimeout = const Duration(seconds: 10);
  final req = await client.getUrl(Uri.parse(url));
  final res = await req.close().timeout(const Duration(seconds: 30));
  final body = await res.transform(utf8.decoder).join();
  client.close();
  return _HttpRes(res.statusCode, body);
}

Future<_HttpRes> _post(String url, Map<String, dynamic> data) async {
  final client = HttpClient()..connectionTimeout = const Duration(seconds: 10);
  final req = await client.postUrl(Uri.parse(url));
  req.headers.contentType = ContentType.json;
  req.write(jsonEncode(data));
  final res = await req.close().timeout(const Duration(seconds: 30));
  final body = await res.transform(utf8.decoder).join();
  client.close();
  return _HttpRes(res.statusCode, body);
}

class _HttpRes {
  _HttpRes(this.statusCode, this.body);
  final int statusCode;
  final String body;
}
