import 'package:shared_preferences/shared_preferences.dart';

/// Stockage tokens JWT (SharedPreferences — compatible Linux, Web, Android, iOS).
class TokenStorage {
  TokenStorage({SharedPreferences? prefs}) : _prefs = prefs;

  SharedPreferences? _prefs;

  Future<SharedPreferences> get _shared async =>
      _prefs ??= await SharedPreferences.getInstance();

  Future<void> write(String key, String value) async {
    final p = await _shared;
    await p.setString(key, value);
  }

  Future<String?> read(String key) async {
    final p = await _shared;
    return p.getString(key);
  }

  Future<void> delete(String key) async {
    final p = await _shared;
    await p.remove(key);
  }

  Future<void> deleteAll() async {
    final p = await _shared;
    await p.remove('sig_sols_token');
    await p.remove('sig_sols_refresh');
    await p.remove('sig_sols_user_json');
  }
}
