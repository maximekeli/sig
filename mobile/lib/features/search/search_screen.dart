import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../services/sig_api.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _ctrl = TextEditingController();
  List<dynamic> _results = [];
  bool _loading = false;

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final q = _ctrl.text.trim();
    if (q.length < 2) return;
    setState(() => _loading = true);
    try {
      final results = await context.read<SigApi>().globalSearch(q);
      setState(() {
        _results = results;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Recherche globale')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _ctrl,
                    decoration: const InputDecoration(
                      hintText: 'Points, fiches, vidéos, utilisateurs…',
                      prefixIcon: Icon(Icons.search),
                    ),
                    onSubmitted: (_) => _search(),
                  ),
                ),
                IconButton(icon: const Icon(Icons.search), onPressed: _search),
              ],
            ),
          ),
          if (_loading) const LinearProgressIndicator(),
          Expanded(
            child: ListView.builder(
              itemCount: _results.length,
              itemBuilder: (_, i) {
                final r = Map<String, dynamic>.from(_results[i] as Map);
                return ListTile(
                  leading: Icon(_iconFor(r['type']?.toString())),
                  title: Text(r['title']?.toString() ?? '—'),
                  subtitle: Text('${r['type'] ?? ''} · ${r['subtitle'] ?? ''}'),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  IconData _iconFor(String? type) {
    switch (type) {
      case 'point':
        return Icons.place;
      case 'sheet':
        return Icons.menu_book;
      case 'video':
        return Icons.videocam;
      case 'user':
        return Icons.person;
      default:
        return Icons.search;
    }
  }
}
