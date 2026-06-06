import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../services/sig_api.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';

/// Équivalent web : #view-my-dashboard /platform/me/dashboard/
class MyDashboardScreen extends StatefulWidget {
  const MyDashboardScreen({super.key});

  @override
  State<MyDashboardScreen> createState() => _MyDashboardScreenState();
}

class _MyDashboardScreenState extends State<MyDashboardScreen> {
  Map<String, dynamic>? _data;
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
      final data = await context.read<SigApi>().personalDashboard();
      setState(() {
        _data = data;
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
    return Scaffold(
      appBar: AppBar(title: const Text('Mon espace')),
      body: _loading
          ? const LoadingView()
          : _error != null
              ? ErrorView(message: _error!, onRetry: _load)
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      Text('Bienvenue, ${_data?['display_name'] ?? _data?['username'] ?? ''}',
                          style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 12),
                      ..._data?.entries.map((e) => Card(
                            child: ListTile(
                              title: Text(e.key),
                              trailing: Text('${e.value}'),
                            ),
                          )) ??
                          [const Text('—')],
                    ],
                  ),
                ),
    );
  }
}
