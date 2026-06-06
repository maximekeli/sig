import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';

import '../../services/sig_api.dart';
import '../auth/auth_service.dart';
import 'offline_queue_service.dart';

/// Synchronise la file offline vers PostGIS (même logique que `syncOfflineQueue` web).
class OfflineSyncService extends ChangeNotifier {
  OfflineSyncService({
    required SigApi api,
    required AuthService auth,
    OfflineQueueService? queue,
    Connectivity? connectivity,
  })  : _api = api,
        _auth = auth,
        _queue = queue ?? OfflineQueueService(),
        _connectivity = connectivity ?? Connectivity();

  final SigApi _api;
  final AuthService _auth;
  final OfflineQueueService _queue;
  final Connectivity _connectivity;

  StreamSubscription<List<ConnectivityResult>>? _sub;
  bool _online = true;
  int _pending = 0;
  bool _syncing = false;
  String? _lastMessage;

  bool get isOnline => _online;
  int get pendingCount => _pending;
  bool get isSyncing => _syncing;
  String? get lastMessage => _lastMessage;

  Future<void> init() async {
    _online = await _checkOnline();
    _pending = (await _queue.readAll()).length;
    notifyListeners();

    _sub = _connectivity.onConnectivityChanged.listen((_) async {
      final wasOffline = !_online;
      _online = await _checkOnline();
      notifyListeners();
      if (wasOffline && _online) {
        await sync();
      }
    });

    if (_online) {
      await sync();
    }
  }

  Future<void> refreshPending() async {
    _pending = (await _queue.readAll()).length;
    notifyListeners();
  }

  Future<bool> queuePoint(Map<String, dynamic> body) async {
    await _queue.enqueue(body);
    await refreshPending();
    _lastMessage = 'Point en file d\'attente (hors ligne).';
    notifyListeners();
    return false;
  }

  Future<bool> submitPoint(Map<String, dynamic> body) async {
    _online = await _checkOnline();
    if (!_online) {
      await queuePoint(body);
      return false;
    }
    if (!_auth.isAuthenticated) {
      throw StateError('Connexion requise pour enregistrer un point.');
    }
    try {
      await _api.createSoilPoint(body);
      _lastMessage = 'Point enregistré (validation en attente).';
      notifyListeners();
      return true;
    } catch (e) {
      if (!_online) {
        await queuePoint(body);
        return false;
      }
      rethrow;
    }
  }

  Future<int> sync() async {
    if (_syncing) return 0;
    _online = await _checkOnline();
    if (!_online || !_auth.isAuthenticated) return 0;

    _syncing = true;
    notifyListeners();

    var synced = 0;
    final remaining = <QueuedSoilPoint>[];

    try {
      final items = await _queue.readAll();
      for (final item in items) {
        try {
          await _api.createSoilPoint(item.body);
          synced += 1;
        } catch (_) {
          remaining.add(item);
        }
      }
      await _queue.replaceAll(remaining);
      _pending = remaining.length;
      if (synced > 0) {
        _lastMessage = '$synced point(s) synchronisé(s).';
      }
    } finally {
      _syncing = false;
      notifyListeners();
    }

    return synced;
  }

  Future<bool> _checkOnline() async {
    final results = await _connectivity.checkConnectivity();
    if (results.contains(ConnectivityResult.none)) return false;
    try {
      await _api.fetchSystemHealth();
      return true;
    } catch (_) {
      return false;
    }
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }
}
