import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../core/activity/activity_tracker.dart';
import '../core/api/api_client.dart';
import '../core/auth/auth_service.dart';
import '../core/offline/offline_sync_service.dart';
import '../core/theme/theme_service.dart';
import '../services/sig_api.dart';
import 'router.dart';

class SigSolsApp extends StatefulWidget {
  const SigSolsApp({super.key});

  @override
  State<SigSolsApp> createState() => _SigSolsAppState();
}

class _SigSolsAppState extends State<SigSolsApp> {
  late final ApiClient _apiClient;
  late final AuthService _authService;
  late final SigApi _sigApi;
  late final OfflineSyncService _offlineSync;
  late final ThemeService _themeService;
  late final ActivityTracker _activity;
  GoRouter? _router;

  @override
  void initState() {
    super.initState();
    _apiClient = ApiClient();
    _authService = AuthService(_apiClient);
    _sigApi = SigApi(_apiClient);
    _offlineSync = OfflineSyncService(api: _sigApi, auth: _authService);
    _themeService = ThemeService();
    _activity = ActivityTracker(_sigApi);
    Future.wait([_authService.init(), _themeService.init()]).then((_) async {
      await _offlineSync.init();
      _authService.addListener(_onAuthChanged);
      _activity.init();
      if (mounted) setState(() => _router = createRouter(_authService));
    });
  }

  void _onAuthChanged() {
    if (_authService.isAuthenticated) {
      _offlineSync.sync();
      _activity.track('auth', detail: {'action': 'session'}, category: 'auth');
    } else {
      _activity.flush();
    }
  }

  @override
  void dispose() {
    _authService.removeListener(_onAuthChanged);
    _offlineSync.dispose();
    _activity.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_router == null) {
      return MaterialApp(
        theme: _themeService.theme,
        home: const Scaffold(body: Center(child: CircularProgressIndicator())),
      );
    }

    return MultiProvider(
      providers: [
        Provider.value(value: _apiClient),
        ChangeNotifierProvider.value(value: _authService),
        Provider.value(value: _sigApi),
        ChangeNotifierProvider.value(value: _activity),
        ChangeNotifierProvider.value(value: _themeService),
        ChangeNotifierProvider.value(value: _offlineSync),
      ],
      child: Consumer<ThemeService>(
        builder: (_, theme, __) => MaterialApp.router(
          title: 'SIG Sols Togo',
          theme: theme.theme,
          routerConfig: _router!,
          debugShowCheckedModeBanner: false,
        ),
      ),
    );
  }
}
