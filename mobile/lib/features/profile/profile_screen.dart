import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../core/auth/auth_service.dart';
import '../../core/config/env.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
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
