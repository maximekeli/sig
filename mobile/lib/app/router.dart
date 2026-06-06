import 'package:go_router/go_router.dart';

import '../core/auth/auth_service.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/register_screen.dart';
import '../features/parcel/parcel_screen.dart';
import 'shell_screen.dart';

GoRouter createRouter(AuthService auth) {
  return GoRouter(
    initialLocation: '/',
    refreshListenable: auth,
    redirect: (context, state) {
      final loggedIn = auth.isAuthenticated;
      final onAuth = state.matchedLocation == '/login' ||
          state.matchedLocation == '/register';
      if (!loggedIn && !onAuth) return '/login';
      if (loggedIn && state.matchedLocation == '/login') return '/';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/parcel', builder: (_, __) => const ParcelScreen()),
      ShellRoute(
        builder: (context, state, child) => ShellScreen(child: child),
        routes: [
          GoRoute(path: '/', builder: (_, __) => const ShellIndexScreen(route: '/')),
          GoRoute(path: '/dashboard', builder: (_, __) => const ShellIndexScreen(route: '/dashboard')),
          GoRoute(path: '/quiz', builder: (_, __) => const ShellIndexScreen(route: '/quiz')),
          GoRoute(path: '/sheets', builder: (_, __) => const ShellIndexScreen(route: '/sheets')),
          GoRoute(path: '/videos', builder: (_, __) => const ShellIndexScreen(route: '/videos')),
          GoRoute(path: '/shorts', builder: (_, __) => const ShellIndexScreen(route: '/shorts')),
          GoRoute(path: '/community', builder: (_, __) => const ShellIndexScreen(route: '/community')),
          GoRoute(path: '/assistant', builder: (_, __) => const ShellIndexScreen(route: '/assistant')),
          GoRoute(path: '/profile', builder: (_, __) => const ShellIndexScreen(route: '/profile')),
        ],
      ),
    ],
  );
}
