import 'package:flutter_test/flutter_test.dart';
import 'package:sig_sols_mobile/core/config/env.dart';

void main() {
  test('apiBaseUrl contient /api/v1', () {
    expect(Env.apiBaseUrl, endsWith('/api/v1'));
  });

  test('resolveMediaUrl chemin relatif', () {
    expect(Env.resolveMediaUrl('/media/photo.jpg'), contains('/media/photo.jpg'));
    expect(Env.resolveMediaUrl('http://cdn.test/img.png'), 'http://cdn.test/img.png');
    expect(Env.resolveMediaUrl(null), '');
  });

  test('wsBaseUrl utilise ws://', () {
    expect(Env.wsBaseUrl, startsWith('ws://'));
    expect(Env.wsBaseUrl, endsWith('/ws/live/'));
  });

  test('constantes app', () {
    expect(Env.appName, 'SIG Sols Togo');
    expect(Env.developer, isNotEmpty);
    expect(Env.developerPhone, startsWith('+'));
  });

  test('tuiles NASA et Sentinel', () {
    expect(Env.nasaTileUrl('NDVI'), contains('/api/v1/nasa/tiles/NDVI/'));
    expect(Env.sentinelTileUrl('ndvi'), contains('/api/v1/sentinel/tiles/ndvi/'));
  });
}
