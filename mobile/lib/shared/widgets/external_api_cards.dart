import 'package:flutter/material.dart';

/// Cartes Sentinel / OpenWeather / NASA / ML / Gemini — même logique que le web.
class ExternalApiCards extends StatelessWidget {
  const ExternalApiCards({
    super.key,
    this.weather,
    this.sentinel,
    this.nasa,
    this.ml,
    this.assistant,
  });

  final Map<String, dynamic>? weather;
  final Map<String, dynamic>? sentinel;
  final Map<String, dynamic>? nasa;
  final Map<String, dynamic>? ml;
  final Map<String, dynamic>? assistant;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _card(Icons.wb_sunny, 'OpenWeather', _weatherLine(weather)),
        _card(Icons.satellite_alt, 'Sentinel Hub', _sentinelLine(sentinel)),
        _card(Icons.public, 'NASA Earthdata', _nasaLine(nasa)),
        _card(Icons.psychology, 'ML Fertilité', _mlLine(ml)),
        _card(Icons.smart_toy, 'Gemini IA', _assistantLine(assistant)),
      ],
    );
  }

  Widget _card(IconData icon, String title, String subtitle) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        subtitle: Text(subtitle),
      ),
    );
  }

  static String _weatherLine(Map<String, dynamic>? w) {
    if (w == null) return 'Non demandé';
    if (w['error'] != null) return w['error'].toString();
    final cur = w['current'] as Map<String, dynamic>?;
    if (cur != null) {
      return '${cur['temp_c'] ?? '—'}°C · ${cur['description'] ?? ''}';
    }
    return w['message']?.toString() ?? (w['configured'] == true ? 'OK' : 'Non configuré');
  }

  static String _sentinelLine(Map<String, dynamic>? s) {
    if (s == null) return 'Non demandé';
    if (s['error'] != null) return s['error'].toString();
    if (s['ndvi_mean'] != null) return 'NDVI moyen: ${s['ndvi_mean']}';
    return s['message']?.toString() ?? (s['configured'] == true ? 'OK' : 'Non configuré');
  }

  static String _nasaLine(Map<String, dynamic>? n) {
    if (n == null) return 'Non demandé';
    if (n['error'] != null) return n['error'].toString();
    final ndvi = n['avg_ndvi'];
    final smap = n['avg_smap'];
    if (ndvi != null || smap != null) {
      return 'NDVI: ${ndvi ?? '—'} · SMAP: ${smap ?? '—'}';
    }
    final byProduct = n['by_product'];
    if (byProduct is List) return '${byProduct.length} produit(s) catalogue';
    if (byProduct is Map) return '${byProduct.length} produit(s) catalogue';
    final products = n['products'];
    if (products is List) return '${products.length} produit(s) catalogue';
    if (products is Map) return '${products.length} produit(s) catalogue';
    final count = n['count'];
    if (count != null) return '$count tuile(s) NASA';
    return n['ndvi_status']?.toString() ?? 'Données NASA';
  }

  static String _mlLine(Map<String, dynamic>? m) {
    if (m == null) return 'Non demandé';
    final pred = m['fertility_class'] ?? m['prediction'];
    if (pred != null) return 'Prédiction: $pred';
    return m['model_version']?.toString() ?? 'Modèle actif';
  }

  static String _assistantLine(Map<String, dynamic>? a) {
    if (a == null) return '—';
    if (a['available'] == true) return 'Gemini ${a['model'] ?? ''} disponible';
    return a['message']?.toString() ?? 'Non configuré';
  }
}
