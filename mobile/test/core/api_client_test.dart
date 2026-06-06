import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sig_sols_mobile/core/api/api_client.dart';
import 'package:sig_sols_mobile/core/api/api_exception.dart';

import '../helpers/fake_token_storage.dart';

void main() {
  late FakeTokenStorage storage;
  late ApiClient client;

  setUp(() {
    storage = FakeTokenStorage();
    client = ApiClient(storage: storage);
  });

  test('isAuthenticated false sans token', () async {
    expect(await client.isAuthenticated(), isFalse);
  });

  test('login persiste les tokens', () async {
    client.dio.httpClientAdapter = _MockAdapter({
      '/auth/token/': {
        'access': 'access-token-xyz',
        'refresh': 'refresh-token-xyz',
        'user': {'id': 1, 'username': 'admin', 'role': 'admin'},
      },
    });
    final data = await client.login('admin', 'admin123');
    expect(data['access'], 'access-token-xyz');
    expect(await client.isAuthenticated(), isTrue);
    expect(await storage.read('sig_sols_token'), 'access-token-xyz');
  });

  test('logout efface la session', () async {
    await storage.write('sig_sols_token', 'tok');
    await storage.write('sig_sols_refresh', 'ref');
    client.dio.httpClientAdapter = _MockAdapter({'/_noop': {}});
    await client.logout();
    expect(await client.isAuthenticated(), isFalse);
  });

  test('get lève ApiException sur erreur 400', () async {
    client.dio.httpClientAdapter = _ErrorAdapter(400, {'detail': 'Bad request'});
    expect(
      () => client.get('/points/'),
      throwsA(isA<ApiException>().having((e) => e.message, 'message', 'Bad request')),
    );
  });
}

class _MockAdapter implements HttpClientAdapter {
  _MockAdapter(this._routes);

  final Map<String, dynamic> _routes;

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    final path = options.path;
    for (final entry in _routes.entries) {
      if (path.contains(entry.key.replaceAll('/', '')) || path.endsWith(entry.key) || path == entry.key) {
        final data = entry.value;
        return ResponseBody.fromString(
          _encodeJson(data),
          200,
          headers: {Headers.contentTypeHeader: ['application/json']},
        );
      }
    }
    return ResponseBody.fromString('{"detail":"not found"}', 404);
  }

  String _encodeJson(dynamic data) {
    if (data is Map) {
      final parts = data.entries.map((e) {
        final v = e.value;
        if (v is Map) return '"${e.key}":${_encodeJson(v)}';
        if (v is String) return '"${e.key}":"$v"';
        return '"${e.key}":$v';
      });
      return '{${parts.join(',')}}';
    }
    return '{}';
  }
}

class _ErrorAdapter implements HttpClientAdapter {
  _ErrorAdapter(this.status, this.body);

  final int status;
  final Map<String, dynamic> body;

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    final detail = body['detail'] ?? 'error';
    return ResponseBody.fromString('{"detail":"$detail"}', status);
  }
}
