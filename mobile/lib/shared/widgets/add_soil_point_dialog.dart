import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';

import '../../core/offline/offline_queue_service.dart';

class AddSoilPointDialog extends StatefulWidget {
  const AddSoilPointDialog({super.key, required this.coords});

  final LatLng coords;

  @override
  State<AddSoilPointDialog> createState() => _AddSoilPointDialogState();
}

class _AddSoilPointDialogState extends State<AddSoilPointDialog> {
  final _phCtrl = TextEditingController(text: '6.2');
  final _humidityCtrl = TextEditingController(text: '35');
  String _soilType = 'limoneux';

  static const _soilTypes = [
    ('limoneux', 'Limoneux'),
    ('argileux', 'Argileux'),
    ('sableux', 'Sableux'),
    ('tourbeux', 'Tourbeux'),
    ('calcaire', 'Calcaire'),
  ];

  @override
  void dispose() {
    _phCtrl.dispose();
    _humidityCtrl.dispose();
    super.dispose();
  }

  Map<String, dynamic> _buildBody() {
    return OfflineQueueService.buildPointBody(
      lat: widget.coords.latitude,
      lon: widget.coords.longitude,
      ph: double.tryParse(_phCtrl.text.replaceAll(',', '.')) ?? 6.2,
      humidityPct: double.tryParse(_humidityCtrl.text.replaceAll(',', '.')) ?? 35,
      soilType: _soilType,
    );
  }

  @override
  Widget build(BuildContext context) {
    final lat = widget.coords.latitude;
    final lon = widget.coords.longitude;

    return AlertDialog(
      title: const Text('Nouveau point de sol'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Coordonnées : ${lat.toStringAsFixed(5)}, ${lon.toStringAsFixed(5)}'),
            const SizedBox(height: 12),
            TextField(
              controller: _phCtrl,
              decoration: const InputDecoration(labelText: 'pH (3,5–9,5)'),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _humidityCtrl,
              decoration: const InputDecoration(labelText: 'Humidité %'),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _soilType,
              decoration: const InputDecoration(labelText: 'Type de sol'),
              items: _soilTypes
                  .map((e) => DropdownMenuItem(value: e.$1, child: Text(e.$2)))
                  .toList(),
              onChanged: (v) => setState(() => _soilType = v ?? 'limoneux'),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Annuler')),
        FilledButton(
          onPressed: () => Navigator.pop(context, _buildBody()),
          child: const Text('Enregistrer'),
        ),
      ],
    );
  }
}
