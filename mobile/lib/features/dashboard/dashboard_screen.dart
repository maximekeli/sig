import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../services/sig_api.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _stats;
  Map<String, dynamic>? _ml;
  Map<String, dynamic>? _weatherStatus;
  Map<String, dynamic>? _sentinelStatus;
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
        api.fetchMlMetrics(),
        api.weatherStatus(),
        api.sentinelStatus(),
      ]);
      setState(() {
        _stats = results[0] as Map<String, dynamic>;
        _ml = results[1] as Map<String, dynamic>;
        _weatherStatus = results[2] as Map<String, dynamic>;
        _sentinelStatus = results[3] as Map<String, dynamic>;
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
          _kpiCard('Points sol validés', '${_stats?['validated_points'] ?? _stats?['total_points'] ?? '—'}'),
          _kpiCard('Points en attente', '${_stats?['pending_points'] ?? '—'}'),
          _kpiCard('ML fertilité', _ml?['model_version']?.toString() ?? 'Actif'),
          _kpiCard('OpenWeather', _weatherStatus?['message']?.toString() ?? '—'),
          _kpiCard('Sentinel Hub', _sentinelStatus?['message']?.toString() ?? '—'),
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
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        title: Text(title),
        trailing: Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      ),
    );
  }

  List<Widget> _buildDistribution(dynamic data) {
    if (data is! Map) return [const Text('—')];
    return data.entries
        .map((e) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 2),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [Text(e.key.toString()), Text('${e.value}')],
              ),
            ))
        .toList();
  }
}
