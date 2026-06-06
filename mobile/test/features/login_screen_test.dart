import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:sig_sols_mobile/core/api/api_client.dart';
import 'package:sig_sols_mobile/core/auth/auth_service.dart';
import 'package:sig_sols_mobile/features/auth/login_screen.dart';
import 'package:sig_sols_mobile/services/sig_api.dart';

import '../helpers/fake_token_storage.dart';

void main() {
  testWidgets('LoginScreen affiche les champs et le bouton', (tester) async {
    final api = ApiClient(storage: FakeTokenStorage());
    final auth = AuthService(api);
    final sigApi = SigApi(api);

    await tester.pumpWidget(
      MultiProvider(
        providers: [
          Provider.value(value: api),
          ChangeNotifierProvider.value(value: auth),
          Provider.value(value: sigApi),
        ],
        child: const MaterialApp(home: LoginScreen()),
      ),
    );

    expect(find.text('SIG Sols Togo'), findsOneWidget);
    expect(find.text('Se connecter'), findsOneWidget);
    expect(find.text('Créer un compte'), findsOneWidget);
    expect(find.widgetWithText(TextField, 'Utilisateur'), findsOneWidget);
    expect(find.widgetWithText(TextField, 'Mot de passe'), findsOneWidget);
  });
}
