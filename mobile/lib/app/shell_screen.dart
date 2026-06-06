import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../shared/widgets/offline_banner.dart';
import '../features/assistant/assistant_screen.dart';
import '../features/community/community_screen.dart';
import '../features/dashboard/dashboard_screen.dart';
import '../features/map/map_screen.dart';
import '../features/profile/profile_screen.dart';
import '../features/quiz/quiz_screen.dart';
import '../features/sheets/sheets_screen.dart';
import '../features/videos/videos_screen.dart';

class ShellScreen extends StatefulWidget {
  const ShellScreen({super.key, required this.child});

  final Widget child;

  @override
  State<ShellScreen> createState() => _ShellScreenState();
}

class _ShellScreenState extends State<ShellScreen> {
  int _indexFromLocation(String loc) {
    if (loc.startsWith('/dashboard')) return 1;
    if (loc.startsWith('/quiz')) return 2;
    if (loc.startsWith('/sheets')) return 3;
    if (loc.startsWith('/videos')) return 4;
    if (loc.startsWith('/shorts')) return 5;
    if (loc.startsWith('/community')) return 6;
    if (loc.startsWith('/assistant')) return 7;
    if (loc.startsWith('/profile')) return 8;
    return 0;
  }

  void _go(int index) {
    const routes = ['/', '/dashboard', '/quiz', '/sheets', '/videos', '/shorts', '/community', '/assistant', '/profile'];
    context.go(routes[index]);
  }

  @override
  Widget build(BuildContext context) {
    final loc = GoRouterState.of(context).uri.toString();
    final index = _indexFromLocation(loc);

    return Scaffold(
      appBar: AppBar(
        title: const Text('SIG Sols Togo'),
        actions: [
          IconButton(icon: const Icon(Icons.map_outlined), tooltip: 'Parcelle', onPressed: () => context.push('/parcel')),
          IconButton(icon: const Icon(Icons.person), tooltip: 'Profil', onPressed: () => context.go('/profile')),
        ],
      ),
      body: Column(
        children: [
          const OfflineBanner(),
          Expanded(child: widget.child),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: index.clamp(0, 8),
        onDestinationSelected: _go,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.map), label: 'Carte'),
          NavigationDestination(icon: Icon(Icons.dashboard), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.quiz), label: 'Quiz'),
          NavigationDestination(icon: Icon(Icons.menu_book), label: 'Fiches'),
          NavigationDestination(icon: Icon(Icons.video_library), label: 'Vidéos'),
          NavigationDestination(icon: Icon(Icons.play_circle), label: 'Shorts'),
          NavigationDestination(icon: Icon(Icons.people), label: 'Communauté'),
          NavigationDestination(icon: Icon(Icons.smart_toy), label: 'IA'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Profil'),
        ],
      ),
    );
  }
}

class ShellIndexScreen extends StatelessWidget {
  const ShellIndexScreen({super.key, required this.route});

  final String route;

  @override
  Widget build(BuildContext context) {
    switch (route) {
      case '/':
        return const MapScreen();
      case '/dashboard':
        return const DashboardScreen();
      case '/quiz':
        return const QuizScreen();
      case '/sheets':
        return const SheetsScreen();
      case '/videos':
        return const VideosScreen(kind: 'video');
      case '/shorts':
        return const VideosScreen(kind: 'short');
      case '/community':
        return const CommunityScreen();
      case '/assistant':
        return const AssistantScreen();
      case '/profile':
        return const ProfileScreen();
      default:
        return const MapScreen();
    }
  }
}
