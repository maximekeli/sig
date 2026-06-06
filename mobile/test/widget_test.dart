import 'package:flutter_test/flutter_test.dart';
import 'package:sig_sols_mobile/app/app.dart';

void main() {
  testWidgets('SigSolsApp démarre', (tester) async {
    await tester.pumpWidget(const SigSolsApp());
    await tester.pump();
    expect(find.byType(SigSolsApp), findsOneWidget);
  });
}
