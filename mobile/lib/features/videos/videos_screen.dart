import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/config/env.dart';
import '../../services/sig_api.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';

class VideosScreen extends StatefulWidget {
  const VideosScreen({super.key, this.kind = 'video'});

  final String kind;

  @override
  State<VideosScreen> createState() => _VideosScreenState();
}

class _VideosScreenState extends State<VideosScreen> {
  List<dynamic> _posts = [];
  bool _loading = true;
  String? _error;

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
      final posts = await context.read<SigApi>().fetchVideos(kind: widget.kind);
      setState(() {
        _posts = posts;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const LoadingView();
    if (_error != null) return ErrorView(message: _error!, onRetry: _load);

    if (_posts.isEmpty) {
      return const Center(child: Text('Aucune vidéo publiée'));
    }

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: _posts.length,
        itemBuilder: (_, i) {
          final p = Map<String, dynamic>.from(_posts[i] as Map);
          final thumb = Env.resolveMediaUrl(p['thumbnail_url']?.toString());
          return Card(
            clipBehavior: Clip.antiAlias,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (thumb.isNotEmpty)
                  CachedNetworkImage(
                    imageUrl: thumb,
                    height: widget.kind == 'short' ? 220 : 160,
                    width: double.infinity,
                    fit: BoxFit.cover,
                    errorWidget: (_, __, ___) => Container(
                      height: 120,
                      color: Colors.black26,
                      child: const Icon(Icons.videocam, size: 48),
                    ),
                  ),
                ListTile(
                  title: Text(p['title']?.toString() ?? 'Sans titre'),
                  subtitle: Text('${p['author_display'] ?? p['author_username'] ?? ''} · ❤ ${p['like_count'] ?? 0}'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
