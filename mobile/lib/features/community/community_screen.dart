import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../services/sig_api.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';

class CommunityScreen extends StatefulWidget {
  const CommunityScreen({super.key});

  @override
  State<CommunityScreen> createState() => _CommunityScreenState();
}

class _CommunityScreenState extends State<CommunityScreen> {
  List<dynamic> _feed = [];
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
      final feed = await context.read<SigApi>().fetchFeed();
      setState(() {
        _feed = feed;
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
    if (_loading) return const LoadingView();
    if (_error != null) return ErrorView(message: _error!, onRetry: _load);

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: _feed.length,
        itemBuilder: (_, i) {
          final item = Map<String, dynamic>.from(_feed[i] as Map);
          return Card(
            child: ListTile(
              leading: CircleAvatar(child: Text((item['author_username'] ?? '?').toString()[0].toUpperCase())),
              title: Text(item['title']?.toString() ?? item['kind']?.toString() ?? 'Publication'),
              subtitle: Text(item['author_display']?.toString() ?? ''),
              trailing: Text('❤ ${item['like_count'] ?? 0}'),
            ),
          );
        },
      ),
    );
  }
}
