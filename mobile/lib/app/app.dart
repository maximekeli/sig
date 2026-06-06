import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../core/api/api_client.dart';
import '../core/auth/auth_service.dart';
import '../core/offline/offline_sync_service.dart';
import '../core/theme/app_theme.dart';
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
  GoRouter? _router;

  @override
  void initState() {
    super.initState();
    _apiClient = ApiClient();
    _authService = AuthService(_apiClient);
    _sigApi = SigApi(_apiClient);
    _offlineSync = OfflineSyncService(api: _sigApi, auth: _authService);
    _authService.init().then((_) async {
      await _offlineSync.init();
      _authService.addListener(_onAuthChanged);
      if (mounted) setState(() => _router = createRouter(_authService));
    });
  }

  void _onAuthChanged() {
    if (_authService.isAuthenticated) {
      _offlineSync.sync();
    }
  }

  @override
  void dispose() {
    _authService.removeListener(_onAuthChanged);
    _offlineSync.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_router == null) {
      return MaterialApp(
        theme: AppTheme.dark,
        home: const Scaffold(body: Center(child: CircularProgressIndicator())),
      );
    }

    return MultiProvider(
      providers: [
        Provider.value(value: _apiClient),
        ChangeNotifierProvider.value(value: _authService),
        Provider.value(value: _sigApi),
        ChangeNotifierProvider.value(value: _offlineSync),
      ],
      child: MaterialApp.router(
        title: 'SIG Sols Togo',
        theme: AppTheme.dark,
        routerConfig: _router!,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
