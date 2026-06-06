import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

/// Configuration API — même backend Django que le site web.
class Env {
  /// Surcharge via : flutter run --dart-define=API_BASE_URL=http://192.168.x.x:8081/api/v1
  static const String _override = String.fromEnvironment('API_BASE_URL');

  static String get apiBaseUrl {
    if (_override.isNotEmpty) return _override;
    if (kIsWeb) return 'http://localhost:8081/api/v1';
    if (Platform.isAndroid) return 'http://10.0.2.2:8081/api/v1';
    return 'http://localhost:8081/api/v1';
  }

  static String get wsBaseUrl {
    final api = apiBaseUrl.replaceFirst('/api/v1', '');
    return '${api.replaceFirst('http', 'ws')}/ws/live/';
  }

  static String get mediaBaseUrl {
    return apiBaseUrl.replaceFirst('/api/v1', '');
  }

  static String resolveMediaUrl(String? path) {
    if (path == null || path.isEmpty) return '';
    if (path.startsWith('http')) return path;
    return '$mediaBaseUrl${path.startsWith('/') ? '' : '/'}$path';
  }

  static const String appName = 'SIG Sols Togo';
  static const String developer = 'Maxime Dzidula KELI';
  static const String developerPhone = '+33 754830039';
}
