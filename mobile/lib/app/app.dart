import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../core/api/api_client.dart';
import '../core/auth/auth_service.dart';
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
  GoRouter? _router;

  @override
  void initState() {
    super.initState();
    _apiClient = ApiClient();
    _authService = AuthService(_apiClient);
    _sigApi = SigApi(_apiClient);
    _authService.init().then((_) {
      setState(() => _router = createRouter(_authService));
    });
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
