import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

/// Configuration API — même backend Django que le site web.
class Env {
  static const String _override = String.fromEnvironment('API_BASE_URL');

  static String get apiBaseUrl {
    if (_override.isNotEmpty) return _override;
    if (kIsWeb) return 'http://localhost:8081/api/v1';
    if (Platform.isAndroid) return 'http://10.0.2.2:8081/api/v1';
    return 'http://localhost:8081/api/v1';
  }

  static String get origin => apiBaseUrl.replaceFirst('/api/v1', '');

  static String get wsBaseUrl => '${origin.replaceFirst('http', 'ws')}/ws/live/';

  static String get mediaBaseUrl => origin;

  static String resolveMediaUrl(String? path) {
    if (path == null || path.isEmpty) return '';
    if (path.startsWith('http')) return path;
    return '$mediaBaseUrl${path.startsWith('/') ? '' : '/'}$path';
  }

  /// Tuiles NASA — même URL que frontend/js/core/mapUtils.js
  static String nasaTileUrl(String product, {String date = 'latest'}) =>
      '$origin/api/v1/nasa/tiles/$product/$date/{z}/{x}/{y}.png';

  /// Tuiles Sentinel Hub
  static String sentinelTileUrl(String layer) =>
      '$origin/api/v1/sentinel/tiles/$layer/{z}/{x}/{y}.png';

  static const String appName = 'SIG Sols Togo';
  static const String developer = 'Maxime Dzidula KELI';
  static const String developerPhone = '+33 754830039';
}
