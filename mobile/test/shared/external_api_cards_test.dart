import 'package:flutter_test/flutter_test.dart';
import 'package:sig_sols_mobile/shared/widgets/external_api_cards.dart';

void main() {
  test('ExternalApiCards accepte by_product en liste NASA', () {
    const widget = ExternalApiCards(
      nasa: {
        'by_product': [
          {'product': 'MOD13Q1', 'count': 3},
          {'product': 'SMAP', 'count': 1},
        ],
      },
    );
    expect(widget.nasa, isNotNull);
  });
}
