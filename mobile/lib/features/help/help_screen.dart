import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/config/env.dart';

/// Équivalent web : #view-help
class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Aide')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('SIG Sols Togo — même backend que le site web.'),
          const SizedBox(height: 16),
          ListTile(
            leading: const Icon(Icons.health_and_safety),
            title: const Text('Santé système'),
            subtitle: const Text('PostGIS, Redis, APIs'),
            onTap: () => launchUrl(Uri.parse(Env.healthUrl)),
          ),
          ListTile(
            leading: const Icon(Icons.api),
            title: const Text('Schéma API'),
            onTap: () => launchUrl(Uri.parse('${Env.origin}/api/schema/')),
          ),
          ListTile(
            leading: const Icon(Icons.admin_panel_settings),
            title: const Text('Administration Django'),
            onTap: () => launchUrl(Uri.parse('${Env.origin}/admin/')),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.person),
            title: Text(Env.developer),
            subtitle: Text(Env.developerPhone),
          ),
        ],
      ),
    );
  }
}
