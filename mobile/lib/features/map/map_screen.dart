import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator.dart';
import 'package:latlong2/latlong.dart';
import 'package:provider/provider.dart';

import '../../core/config/env.dart';
import '../../models/soil_point.dart';
import '../../services/sig_api.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  static const _togoCenter = LatLng(6.4, 1.35);
  final _mapController = MapController();

  List<SoilPoint> _points = [];
  bool _loading = true;
  String? _error;
  LatLng? _myPosition;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final api = context.read<SigApi>();
      final points = await api.fetchSoilPoints();
      LatLng? pos;
      try {
        final perm = await Geolocator.checkPermission();
        if (perm == LocationPermission.denied) {
          await Geolocator.requestPermission();
        }
        final loc = await Geolocator.getCurrentPosition();
        pos = LatLng(loc.latitude, loc.longitude);
        await api.updateLocation(loc.latitude, loc.longitude);
      } catch (_) {}
      setState(() {
        _points = points;
        _myPosition = pos;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Color _phColor(SoilPoint p) {
    final ph = p.ph;
    if (ph == null) return Colors.grey;
    if (ph < 5.5) return Colors.red;
    if (ph < 6.5) return Colors.orange;
    if (ph < 7.5) return Colors.green;
    return Colors.blue;
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const LoadingView(message: 'Chargement carte…');
    if (_error != null) return ErrorView(message: _error!, onRetry: _load);

    return Stack(
      children: [
        FlutterMap(
          mapController: _mapController,
          options: MapOptions(
            initialCenter: _myPosition ?? _togoCenter,
            initialZoom: 9,
            onTap: (_, point) => _showWeatherAt(context, point),
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'tg.dusol.sig_sols_mobile',
            ),
            MarkerLayer(
              markers: [
                ..._points.map((p) => Marker(
                      point: LatLng(p.lat, p.lon),
                      width: 28,
                      height: 28,
                      child: GestureDetector(
                        onTap: () => _showPointSheet(p),
                        child: Icon(Icons.circle, color: _phColor(p), size: 14),
                      ),
                    )),
                if (_myPosition != null)
                  Marker(
                    point: _myPosition!,
                    width: 36,
                    height: 36,
                    child: const Icon(Icons.my_location, color: Colors.cyanAccent),
                  ),
              ],
            ),
          ],
        ),
        Positioned(
          top: 8,
          left: 8,
          right: 8,
          child: Card(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Text('${_points.length} points sol · NASA · Sentinel · Météo'),
            ),
          ),
        ),
        Positioned(
          bottom: 16,
          right: 16,
          child: FloatingActionButton(
            heroTag: 'loc',
            onPressed: () {
              if (_myPosition != null) {
                _mapController.move(_myPosition!, 12);
              }
            },
            child: const Icon(Icons.gps_fixed),
          ),
        ),
      ],
    );
  }

  void _showPointSheet(SoilPoint p) {
    showModalBottomSheet(
      context: context,
      builder: (_) => Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Point sol #${p.id}', style: Theme.of(context).textTheme.titleLarge),
            Text('pH: ${p.ph?.toStringAsFixed(1) ?? '—'}'),
            Text('Type: ${p.soilType ?? '—'}'),
            Text('Fertilité: ${p.fertilityClass ?? '—'}'),
            Text('NDVI: ${p.ndvi3mAvg?.toStringAsFixed(2) ?? '—'}'),
          ],
        ),
      ),
    );
  }

  Future<void> _showWeatherAt(BuildContext context, LatLng point) async {
    try {
      final w = await context.read<SigApi>().weatherCurrent(point.latitude, point.longitude);
      final cur = w['current'] as Map<String, dynamic>? ?? w;
      if (!context.mounted) return;
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Météo ici'),
          content: Text(
            '${cur['description'] ?? cur['temp_c'] ?? ''}\n'
            'Temp: ${cur['temp_c'] ?? '—'}°C · Humidité: ${cur['humidity_pct'] ?? '—'}%',
          ),
        ),
      );
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }
}
