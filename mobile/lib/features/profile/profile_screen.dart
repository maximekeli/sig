import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../core/auth/auth_service.dart';
import '../../core/config/env.dart';
import '../../core/offline/offline_sync_service.dart';
import '../../services/sig_api.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _dbInfo;
  String? _dbStatus;

  @override
  void initState() {
    super.initState();
    _loadHealth();
  }

  Future<void> _loadHealth() async {
    try {
      final health = await context.read<SigApi>().fetchSystemHealth();
      if (!mounted) return;
      final checks = health['checks'] as Map<String, dynamic>?;
      setState(() {
        _dbStatus = checks?['database']?.toString();
        _dbInfo = checks?['database_info'] != null
            ? Map<String, dynamic>.from(checks!['database_info'] as Map)
            : null;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _dbStatus = 'indisponible');
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    final sync = context.watch<OfflineSyncService>();
    final user = auth.user;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        CircleAvatar(
          radius: 40,
          child: Text((user?.displayName ?? '?')[0].toUpperCase(), style: const TextStyle(fontSize: 32)),
        ),
        const SizedBox(height: 12),
        Text(user?.displayName ?? '', style: Theme.of(context).textTheme.headlineSmall, textAlign: TextAlign.center),
        Text('@${user?.username ?? ''} · ${user?.role ?? ''}', textAlign: TextAlign.center),
        const SizedBox(height: 20),
        if (user?.email != null) ListTile(leading: const Icon(Icons.email), title: Text(user!.email!)),
        if (user?.phone != null) ListTile(leading: const Icon(Icons.phone), title: Text(user!.phone!)),
        if (user?.region != null) ListTile(leading: const Icon(Icons.place), title: Text(user!.region!)),
        const Divider(),
        ListTile(
          leading: const Icon(Icons.api),
          title: const Text('API backend'),
          subtitle: Text(Env.apiBaseUrl),
        ),
        if (sync.pendingCount > 0)
          ListTile(
            leading: const Icon(Icons.cloud_upload),
            title: Text('${sync.pendingCount} point(s) en attente'),
            subtitle: const Text('Synchronisation vers PostGIS'),
            trailing: sync.isSyncing
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : IconButton(
                    icon: const Icon(Icons.sync),
                    onPressed: () => sync.sync(),
                  ),
          ),
        ListTile(
          leading: Icon(
            _dbStatus == 'ok' ? Icons.check_circle : Icons.storage,
            color: _dbStatus == 'ok' ? Colors.green : null,
          ),
          title: const Text('Base de données'),
          subtitle: Text(
            _dbInfo != null
                ? '${_dbInfo!['backend']} · ${_dbInfo!['name']} (${_dbInfo!['host']})\n'
                  'Partagée avec le site web'
                : _dbStatus == null
                    ? 'Vérification…'
                    : 'Connexion impossible — vérifiez Docker',
          ),
          isThreeLine: _dbInfo != null,
        ),
        ListTile(
          leading: const Icon(Icons.person),
          title: Text(Env.developer),
          subtitle: Text(Env.developerPhone),
        ),
        const SizedBox(height: 20),
        FilledButton.icon(
          onPressed: () async {
            final ok = await showDialog<bool>(
              context: context,
              builder: (_) => AlertDialog(
                title: const Text('Déconnexion'),
                content: const Text('Voulez-vous vraiment vous déconnecter ?'),
                actions: [
                  TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Annuler')),
                  FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Déconnecter')),
                ],
              ),
            );
            if (ok == true) {
              await auth.logout();
              if (context.mounted) context.go('/login');
            }
          },
          icon: const Icon(Icons.logout),
          label: const Text('Se déconnecter'),
        ),
      ],
    );
  }
}
