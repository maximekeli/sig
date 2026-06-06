import 'package:flutter_test/flutter_test.dart';
import 'package:sig_sols_mobile/app/app.dart';

void main() {
  testWidgets('App smoke test', (tester) async {
    await tester.pumpWidget(const SigSolsApp());
    await tester.pump();
    expect(find.byType(SigSolsApp), findsOneWidget);
  });
}
