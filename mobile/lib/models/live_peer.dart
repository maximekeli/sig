class LivePeer {
  const LivePeer({
    required this.userId,
    required this.username,
    required this.lat,
    required this.lon,
    this.displayName,
    this.role = 'agent',
    this.accuracyM,
  });

  final int userId;
  final String username;
  final String? displayName;
  final String role;
  final double lat;
  final double lon;
  final double? accuracyM;

  factory LivePeer.fromJson(Map<String, dynamic> json) => LivePeer(
        userId: json['user_id'] as int,
        username: json['username']?.toString() ?? '',
        displayName: json['display_name']?.toString(),
        role: json['role']?.toString() ?? 'agent',
        lat: (json['lat'] as num).toDouble(),
        lon: (json['lon'] as num).toDouble(),
        accuracyM: (json['accuracy_m'] as num?)?.toDouble(),
      );

  String get label => displayName ?? username;
}
