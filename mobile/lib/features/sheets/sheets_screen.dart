import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/config/env.dart';
import '../../services/sig_api.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';

class SheetsScreen extends StatefulWidget {
  const SheetsScreen({super.key});

  @override
  State<SheetsScreen> createState() => _SheetsScreenState();
}

class _SheetsScreenState extends State<SheetsScreen> {
  List<dynamic> _sheets = [];
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
      final sheets = await context.read<SigApi>().fetchSheets();
      setState(() {
        _sheets = sheets;
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

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: _sheets.length,
      itemBuilder: (_, i) {
        final s = Map<String, dynamic>.from(_sheets[i] as Map);
        return Card(
          child: ListTile(
            title: Text(s['title']?.toString() ?? 'Fiche'),
            subtitle: Text(s['theme']?.toString() ?? ''),
            trailing: s['pdf_url'] != null ? const Icon(Icons.picture_as_pdf) : null,
            onTap: () async {
              final url = Env.resolveMediaUrl(s['pdf_url']?.toString());
              if (url.isNotEmpty) await launchUrl(Uri.parse(url));
            },
          ),
        );
      },
    );
  }
}
