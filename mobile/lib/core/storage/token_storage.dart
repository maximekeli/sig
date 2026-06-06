import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Stockage tokens — secure sur mobile, SharedPreferences sur Linux/Web (évite erreur linker libsecret).
class TokenStorage {
  TokenStorage({FlutterSecureStorage? secure, SharedPreferences? prefs})
      : _secure = secure ?? const FlutterSecureStorage(),
        _prefs = prefs;

  final FlutterSecureStorage _secure;
  SharedPreferences? _prefs;

  bool get _useSecure => !kIsWeb && (Platform.isAndroid || Platform.isIOS);

  Future<SharedPreferences> get _shared async =>
      _prefs ??= await SharedPreferences.getInstance();

  Future<void> write(String key, String value) async {
    if (_useSecure) {
      await _secure.write(key: key, value: value);
    } else {
      final p = await _shared;
      await p.setString(key, value);
    }
  }

  Future<String?> read(String key) async {
    if (_useSecure) return _secure.read(key: key);
    final p = await _shared;
    return p.getString(key);
  }

  Future<void> delete(String key) async {
    if (_useSecure) {
      await _secure.delete(key: key);
    } else {
      final p = await _shared;
      await p.remove(key);
    }
  }

  Future<void> deleteAll() async {
    if (_useSecure) {
      await _secure.deleteAll();
    } else {
      final p = await _shared;
      await p.remove('sig_sols_token');
      await p.remove('sig_sols_refresh');
      await p.remove('sig_sols_user_json');
    }
  }
}
