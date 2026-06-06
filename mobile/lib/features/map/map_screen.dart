import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';
import 'package:provider/provider.dart';

import '../../core/config/env.dart';
import '../../core/offline/offline_sync_service.dart';
import '../../models/soil_point.dart';
import '../../services/sig_api.dart';
import '../../shared/widgets/add_soil_point_dialog.dart';
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
  Map<String, dynamic>? _apiStatus;
  bool _showSentinelNdvi = false;
  bool _showNasaNdvi = false;
  bool _addPointMode = false;
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
      final results = await Future.wait([
        api.fetchSoilPoints(),
        api.fetchExternalApiStatus().catchError((_) => <String, Map<String, dynamic>>{}),
      ]);
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
        _points = results[0] as List<SoilPoint>;
        _apiStatus = results[1] as Map<String, Map<String, dynamic>>;
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

    final layers = <Widget>[
      TileLayer(
        urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        userAgentPackageName: 'tg.dusol.sig_sols_mobile',
      ),
      if (_showSentinelNdvi)
        Opacity(
          opacity: 0.55,
          child: TileLayer(
            urlTemplate: Env.sentinelTileUrl('ndvi'),
            userAgentPackageName: 'tg.dusol.sig_sols_mobile',
          ),
        ),
      if (_showNasaNdvi)
        Opacity(
          opacity: 0.5,
          child: TileLayer(
            urlTemplate: Env.nasaTileUrl('NDVI'),
            userAgentPackageName: 'tg.dusol.sig_sols_mobile',
          ),
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
    ];

    return Stack(
      children: [
        FlutterMap(
          mapController: _mapController,
          options: MapOptions(
            initialCenter: _myPosition ?? _togoCenter,
            initialZoom: 9,
            onTap: (_, point) {
              if (_addPointMode) {
                _openAddPointForm(point);
              } else {
                _showProbeMenu(context, point);
              }
            },
          ),
          children: layers,
        ),
        Positioned(
          top: 8,
          left: 8,
          right: 8,
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(10),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('${_points.length} points sol'),
                  Text(
                    'OW: ${_statusMsg('weather')} · Sentinel: ${_statusMsg('sentinel')} · NASA: ${_statusMsg('nasa')}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 6,
                    children: [
                      FilterChip(
                        label: const Text('NDVI Sentinel'),
                        selected: _showSentinelNdvi,
                        onSelected: (v) => setState(() => _showSentinelNdvi = v),
                      ),
                      FilterChip(
                        label: const Text('NDVI NASA'),
                        selected: _showNasaNdvi,
                        onSelected: (v) => setState(() => _showNasaNdvi = v),
                      ),
                      FilterChip(
                        label: const Text('Ajouter point'),
                        selected: _addPointMode,
                        avatar: Icon(
                          _addPointMode ? Icons.add_location_alt : Icons.add_location,
                          size: 18,
                        ),
                        onSelected: (v) => setState(() => _addPointMode = v),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
        if (_addPointMode)
          Positioned(
            bottom: 80,
            left: 16,
            right: 16,
            child: Card(
              color: Theme.of(context).colorScheme.primaryContainer,
              child: const Padding(
                padding: EdgeInsets.all(10),
                child: Text('Mode ajout actif — touchez la carte pour placer un point'),
              ),
            ),
          ),
        Positioned(
          bottom: 16,
          right: 16,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              FloatingActionButton.small(
                heroTag: 'tools',
                onPressed: () => _showMapTools(context),
                child: const Icon(Icons.build),
              ),
              const SizedBox(height: 8),
              FloatingActionButton(
                heroTag: 'loc',
                onPressed: () {
                  if (_myPosition != null) _mapController.move(_myPosition!, 12);
                },
                child: const Icon(Icons.gps_fixed),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _statusMsg(String key) {
    final s = _apiStatus?[key];
    if (s == null) return '—';
    if (s['ok'] == true || s['configured'] == true || s['available'] == true) return 'OK';
    return s['message']?.toString() ?? '—';
  }

  void _showPointSheet(SoilPoint p) {
    showModalBottomSheet(
      context: context,
      builder: (ctx) => _PointSheet(point: p),
    );
  }

  Future<void> _openAddPointForm(LatLng coords) async {
    final body = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (_) => AddSoilPointDialog(coords: coords),
    );
    if (body == null || !mounted) return;

    final sync = context.read<OfflineSyncService>();
    try {
      final saved = await sync.submitPoint(body);
      if (!mounted) return;
      setState(() => _addPointMode = false);
      final msg = sync.lastMessage ??
          (saved ? 'Point enregistré.' : 'Point en file d\'attente.');
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
      if (saved) await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
    }
  }

  Future<void> _showProbeMenu(BuildContext context, LatLng point) async {
    final action = await showModalBottomSheet<String>(
      context: context,
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.wb_sunny),
              title: const Text('Météo OpenWeather'),
              onTap: () => Navigator.pop(context, 'weather'),
            ),
            ListTile(
              leading: const Icon(Icons.satellite_alt),
              title: const Text('NDVI Sentinel (zone)'),
              onTap: () => Navigator.pop(context, 'sentinel'),
            ),
            ListTile(
              leading: const Icon(Icons.psychology),
              title: const Text('ML fertilité'),
              onTap: () => Navigator.pop(context, 'ml'),
            ),
          ],
        ),
      ),
    );
    if (!context.mounted || action == null) return;
    final api = context.read<SigApi>();
    try {
      if (action == 'weather') {
        final w = await api.weatherCurrent(point.latitude, point.longitude);
        final cur = w['current'] as Map<String, dynamic>? ?? w;
        if (!context.mounted) return;
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('OpenWeather'),
            content: Text(
              '${cur['description'] ?? ''}\n'
              'Temp: ${cur['temp_c'] ?? '—'}°C · Humidité: ${cur['humidity_pct'] ?? '—'}%',
            ),
          ),
        );
      } else if (action == 'sentinel') {
        final bbox = _bboxAround(point, 0.02);
        final s = await api.sentinelAnalyze(
          minLon: bbox[0], minLat: bbox[1], maxLon: bbox[2], maxLat: bbox[3],
        );
        if (!context.mounted) return;
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Sentinel Hub NDVI'),
            content: Text('NDVI moyen: ${s['ndvi_mean'] ?? s['error'] ?? '—'}'),
          ),
        );
      } else if (action == 'ml') {
        final m = await api.predictFertility(lat: point.latitude, lon: point.longitude);
        if (!context.mounted) return;
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('ML Fertilité'),
            content: Text('Classe: ${m['fertility_class'] ?? m['prediction'] ?? '—'}'),
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  List<double> _bboxAround(LatLng p, double d) =>
      [p.longitude - d, p.latitude - d, p.longitude + d, p.latitude + d];
}

class _PointSheet extends StatelessWidget {
  const _PointSheet({required this.point});

  final SoilPoint point;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Point sol #${point.id}', style: Theme.of(context).textTheme.titleLarge),
          Text('pH: ${point.ph?.toStringAsFixed(1) ?? '—'}'),
          Text('Type: ${point.soilType ?? '—'}'),
          Text('Fertilité: ${point.fertilityClass ?? '—'}'),
          Text('NDVI: ${point.ndvi3mAvg?.toStringAsFixed(2) ?? '—'}'),
          const SizedBox(height: 12),
          Row(
            children: [
              TextButton.icon(
                onPressed: () async {
                  try {
                    final ts = await context.read<SigApi>().ndviTimeseries(point.id);
                    if (!context.mounted) return;
                    showDialog(
                      context: context,
                      builder: (_) => AlertDialog(
                        title: const Text('NDVI time series'),
                        content: Text(ts.toString()),
                      ),
                    );
                  } catch (e) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
                    }
                  }
                },
                icon: const Icon(Icons.timeline),
                label: const Text('Série NDVI'),
              ),
              TextButton.icon(
                onPressed: () async {
                  try {
                    final m = await context.read<SigApi>().predictFertility(
                          lat: point.lat,
                          lon: point.lon,
                          pointId: point.id,
                        );
                    if (!context.mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('ML: ${m['fertility_class'] ?? '—'}')),
                    );
                  } catch (e) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
                    }
                  }
                },
                icon: const Icon(Icons.psychology),
                label: const Text('ML'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
