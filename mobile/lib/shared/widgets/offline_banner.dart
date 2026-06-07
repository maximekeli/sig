import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/i18n/locale_service.dart';
import '../../core/offline/offline_sync_service.dart';

class OfflineBanner extends StatelessWidget {
  const OfflineBanner({super.key});

  @override
  Widget build(BuildContext context) {
    final sync = context.watch<OfflineSyncService>();
    final i18n = context.watch<LocaleService>();
    final show = !sync.isOnline || sync.pendingCount > 0 || sync.isSyncing;
    if (!show) return const SizedBox.shrink();

    final text = sync.isSyncing
        ? i18n.t('offline.syncing')
        : !sync.isOnline
            ? sync.pendingCount > 0
                ? i18n.t('offline.pending', vars: {'n': '${sync.pendingCount}'})
                : i18n.t('offline.banner')
            : i18n.t('offline.queue', vars: {'n': '${sync.pendingCount}'});

    return Material(
      color: Colors.orange.shade800,
      child: SafeArea(
        bottom: false,
        child: InkWell(
          onTap: sync.isSyncing ? null : () => sync.sync(),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              children: [
                Icon(
                  sync.isOnline ? Icons.cloud_upload : Icons.cloud_off,
                  color: Colors.white,
                  size: 18,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(text, style: const TextStyle(color: Colors.white, fontSize: 13)),
                ),
                if (sync.isOnline && sync.pendingCount > 0 && !sync.isSyncing)
                  const Icon(Icons.sync, color: Colors.white, size: 18),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
