import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../core/activity/activity_tracker.dart';
import '../core/auth/auth_service.dart';
import '../core/theme/theme_service.dart';
import '../features/assistant/assistant_screen.dart';
import '../features/community/community_screen.dart';
import '../features/dashboard/dashboard_screen.dart';
import '../features/map/map_screen.dart';
import '../features/profile/profile_screen.dart';
import '../features/quiz/quiz_screen.dart';
import '../features/sheets/sheets_screen.dart';
import '../features/videos/videos_screen.dart';
import '../services/sig_api.dart';
import '../shared/widgets/offline_banner.dart';

class ShellScreen extends StatefulWidget {
  const ShellScreen({super.key, required this.child});

  final Widget child;

  @override
  State<ShellScreen> createState() => _ShellScreenState();
}

class _ShellScreenState extends State<ShellScreen> {
  int _unread = 0;

  @override
  void initState() {
    super.initState();
    _loadUnread();
  }

  Future<void> _loadUnread() async {
    try {
      final n = await context.read<SigApi>().unreadNotifications();
      if (mounted) setState(() => _unread = n);
    } catch (_) {}
  }

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
    const names = ['map', 'dashboard', 'quiz', 'sheets', 'videos', 'shorts', 'community', 'assistant', 'profile'];
    context.read<ActivityTracker>().trackNav(names[index]);
    context.go(routes[index]);
  }

  @override
  Widget build(BuildContext context) {
    final loc = GoRouterState.of(context).uri.toString();
    final index = _indexFromLocation(loc);
    final user = context.watch<AuthService>().user;

    return Scaffold(
      drawer: Drawer(
        child: ListView(
          children: [
            DrawerHeader(
              decoration: BoxDecoration(color: Theme.of(context).colorScheme.primaryContainer),
              child: Text('SIG Sols Togo\n${user?.displayName ?? ''}', style: const TextStyle(fontSize: 18)),
            ),
            ListTile(
              leading: const Icon(Icons.search),
              title: const Text('Recherche globale'),
              onTap: () {
                Navigator.pop(context);
                context.push('/search');
              },
            ),
            ListTile(
              leading: Badge(label: Text('$_unread'), isLabelVisible: _unread > 0, child: const Icon(Icons.notifications)),
              title: const Text('Notifications'),
              onTap: () {
                Navigator.pop(context);
                context.push('/notifications').then((_) => _loadUnread());
              },
            ),
            ListTile(
              leading: const Icon(Icons.dashboard_customize),
              title: const Text('Mon espace'),
              onTap: () {
                Navigator.pop(context);
                context.push('/my-dashboard');
              },
            ),
            if (user?.isAdmin == true)
              ListTile(
                leading: const Icon(Icons.admin_panel_settings),
                title: const Text('Administration'),
                onTap: () {
                  Navigator.pop(context);
                  context.push('/admin');
                },
              ),
            ListTile(
              leading: const Icon(Icons.help),
              title: const Text('Aide'),
              onTap: () {
                Navigator.pop(context);
                context.push('/help');
              },
            ),
            Consumer<ThemeService>(
              builder: (_, theme, __) => SwitchListTile(
                secondary: Icon(theme.isDark ? Icons.dark_mode : Icons.light_mode),
                title: const Text('Thème clair / sombre'),
                value: !theme.isDark,
                onChanged: (_) => theme.toggle(),
              ),
            ),
          ],
        ),
      ),
      appBar: AppBar(
        title: const Text('SIG Sols Togo'),
        actions: [
          IconButton(
            icon: Badge(
              label: Text('$_unread'),
              isLabelVisible: _unread > 0,
              child: const Icon(Icons.notifications_outlined),
            ),
            onPressed: () => context.push('/notifications').then((_) => _loadUnread()),
          ),
          IconButton(icon: const Icon(Icons.map_outlined), tooltip: 'Parcelle', onPressed: () => context.push('/parcel')),
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
