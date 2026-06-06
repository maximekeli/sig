import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:provider/provider.dart';

import '../../models/parcel_analysis.dart';
import '../../services/sig_api.dart';
import '../../shared/widgets/loading_view.dart';

class ParcelScreen extends StatefulWidget {
  const ParcelScreen({super.key});

  @override
  State<ParcelScreen> createState() => _ParcelScreenState();
}

class _ParcelScreenState extends State<ParcelScreen> {
  ParcelAnalysis? _result;
  bool _loading = false;

  Future<void> _analyzeHere() async {
    final api = context.read<SigApi>();
    setState(() => _loading = true);
    try {
      final pos = await Geolocator.getCurrentPosition();
      final result = await api.analyzeParcelAt(pos.latitude, pos.longitude);
      setState(() => _result = result);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Analyse parcelle')),
      body: _loading
          ? const LoadingView(message: 'Analyse Sentinel + Météo + ML…')
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                const Text(
                  'Analysez une parcelle autour de votre position (même API que le site web).',
                ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: _analyzeHere,
                  icon: const Icon(Icons.analytics),
                  label: const Text('Analyser ici'),
                ),
                if (_result != null) ...[
                  const SizedBox(height: 20),
                  _buildResult(_result!),
                ],
              ],
            ),
    );
  }

  Widget _buildResult(ParcelAnalysis r) {
    final w = r.weather?['current'] as Map<String, dynamic>?;
    final s = r.sentinel;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Card(child: ListTile(title: Text(r.parcelName), subtitle: Text('${r.areaHa?.toStringAsFixed(1) ?? '—'} ha'))),
        Card(
          child: ListTile(
            leading: const Icon(Icons.wb_sunny),
            title: const Text('OpenWeather'),
            subtitle: Text(w != null
                ? '${w['temp_c']}°C · ${w['description']}'
                : r.weather?['error']?.toString() ?? '—'),
          ),
        ),
        Card(
          child: ListTile(
            leading: const Icon(Icons.satellite_alt),
            title: const Text('Sentinel NDVI'),
            subtitle: Text(s != null
                ? 'NDVI moyen: ${s['ndvi_mean']}'
                : s?['error']?.toString() ?? '—'),
          ),
        ),
        if (r.recommendations.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text('Recommandations', style: Theme.of(context).textTheme.titleMedium),
          ...r.recommendations.map((rec) => ListTile(dense: true, leading: const Icon(Icons.lightbulb_outline), title: Text(rec))),
        ],
      ],
    );
  }
}
