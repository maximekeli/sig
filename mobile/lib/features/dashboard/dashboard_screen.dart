import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../services/sig_api.dart';
import '../../shared/widgets/external_api_cards.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _stats;
  Map<String, Map<String, dynamic>>? _apis;
  Map<String, dynamic>? _smap;
  Map<String, dynamic>? _dbInfo;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final api = context.read<SigApi>();
      final results = await Future.wait([
        api.fetchDashboardStats(),
        api.fetchExternalApiStatus(),
        api.smapCorrelation().catchError((_) => <String, dynamic>{}),
        api.fetchSystemHealth().catchError((_) => <String, dynamic>{}),
      ]);
      final health = Map<String, dynamic>.from(results[3] as Map);
      final checks = health['checks'] as Map<String, dynamic>?;
      setState(() {
        _stats = Map<String, dynamic>.from(results[0] as Map);
        _apis = results[1] as Map<String, Map<String, dynamic>>;
        _smap = Map<String, dynamic>.from(results[2] as Map);
        _dbInfo = checks?['database_info'] != null
            ? Map<String, dynamic>.from(checks!['database_info'] as Map)
            : null;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const LoadingView(message: 'Tableau de bord…');
    if (_error != null) return ErrorView(message: _error!, onRetry: _load);

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (_dbInfo != null && _dbInfo!.isNotEmpty)
            Card(
              color: Theme.of(context).colorScheme.primaryContainer.withValues(alpha: 0.35),
              child: ListTile(
                leading: const Icon(Icons.storage),
                title: const Text('Base de données partagée'),
                subtitle: Text(
                  '${_dbInfo!['backend'] ?? '—'} · ${_dbInfo!['name'] ?? '—'} · '
                  '${_dbInfo!['host'] ?? '—'}\n'
                  'Même source que le site web (API Django).',
                ),
                isThreeLine: true,
              ),
            ),
          Text('KPIs sols', style: Theme.of(context).textTheme.titleMedium),
          _kpiCard('Points validés', '${_stats?['validated_points'] ?? _stats?['total_points'] ?? '—'}'),
          _kpiCard('Points en attente', '${_stats?['pending_points'] ?? '—'}'),
          const SizedBox(height: 12),
          Text('APIs externes (via backend)', style: Theme.of(context).textTheme.titleMedium),
          ExternalApiCards(
            weather: _apis?['weather'],
            sentinel: _apis?['sentinel'],
            nasa: _apis?['nasa'],
            ml: _apis?['ml'],
            assistant: _apis?['assistant'],
          ),
          if (_smap != null && _smap!.isNotEmpty)
            Card(
              child: ListTile(
                title: const Text('Corrélation SMAP'),
                subtitle: Text(_smap!['summary']?.toString() ?? _smap.toString()),
              ),
            ),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Répartition fertilité', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  ..._buildDistribution(_stats?['fertility_distribution']),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _kpiCard(String title, String value) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(title: Text(title), trailing: Text(value, style: const TextStyle(fontWeight: FontWeight.bold))),
    );
  }

  List<Widget> _buildDistribution(dynamic data) {
    if (data is! Map) return [const Text('—')];
    return data.entries
        .map((e) => Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [Text(e.key.toString()), Text('${e.value}')],
            ))
        .toList();
  }
}
