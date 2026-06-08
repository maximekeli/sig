/// Fonds de carte — parité avec frontend/js/map.js (3 basemaps).
enum BasemapType {
  osm,
  satellite,
  topo,
}

extension BasemapTypeExt on BasemapType {
  String get label {
    switch (this) {
      case BasemapType.osm:
        return 'Plan (OSM)';
      case BasemapType.satellite:
        return 'Satellite';
      case BasemapType.topo:
        return 'Topographique';
    }
  }

  String get urlTemplate {
    switch (this) {
      case BasemapType.osm:
        return 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
      case BasemapType.satellite:
        return 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
      case BasemapType.topo:
        return 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png';
    }
  }

  List<String>? get subdomains {
    if (this == BasemapType.topo) return const ['a', 'b', 'c'];
    return null;
  }
}
