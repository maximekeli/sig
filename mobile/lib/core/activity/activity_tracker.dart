import 'dart:async';
import 'dart:math';

import 'package:flutter/foundation.dart';

import '../../services/sig_api.dart';

/// Suivi d'activité — même endpoint que frontend/js/core/activityTracker.js
class ActivityTracker {
  ActivityTracker(this._api);

  final SigApi _api;
  final _sessionId = '${DateTime.now().millisecondsSinceEpoch}_${Random().nextInt(9999)}';
  final _buffer = <Map<String, dynamic>>[];
  Timer? _flushTimer;

  void init() {
    _flushTimer?.cancel();
    _flushTimer = Timer.periodic(const Duration(seconds: 30), (_) => flush());
  }

  void dispose() {
    _flushTimer?.cancel();
    flush();
  }

  void track(String eventType, {Map<String, dynamic> detail = const {}, String category = 'other'}) {
    _buffer.add({
      'event_type': eventType,
      'category': category,
      'detail': detail,
      'ts': DateTime.now().toUtc().toIso8601String(),
    });
    if (_buffer.length >= 10) flush();
  }

  void trackNav(String view) => track('nav', detail: {'view': view}, category: 'navigation');

  Future<void> flush() async {
    if (_buffer.isEmpty) return;
    final batch = List<Map<String, dynamic>>.from(_buffer);
    _buffer.clear();
    try {
      await _api.postActivity(sessionId: _sessionId, events: batch);
    } catch (e) {
      if (kDebugMode) debugPrint('Activity flush: $e');
      _buffer.insertAll(0, batch);
    }
  }
}
