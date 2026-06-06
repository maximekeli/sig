import 'package:cached_network_image/cached_network_image.dart';
import 'package:file_picker/file_picker.dart';
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
  List<dynamic> _stories = [];
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
      final api = context.read<SigApi>();
      final posts = await api.fetchVideos(kind: widget.kind);
      List<dynamic> stories = [];
      if (widget.kind == 'video') {
        stories = await api.fetchStories().catchError((_) => <dynamic>[]);
      }
      setState(() {
        _posts = posts;
        _stories = stories;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _upload() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.video);
    if (result == null || result.files.single.path == null) return;
    final titleCtrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text('Publier ${widget.kind == 'short' ? 'un short' : 'une vidéo'}'),
        content: TextField(controller: titleCtrl, decoration: const InputDecoration(labelText: 'Titre')),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Annuler')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Envoyer')),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await context.read<SigApi>().uploadVideo(
            filePath: result.files.single.path!,
            kind: widget.kind,
            title: titleCtrl.text.trim().isEmpty ? 'Sans titre' : titleCtrl.text.trim(),
          );
      _load();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
    }
  }

  Future<void> _showComments(int postId) async {
    final comments = await context.read<SigApi>().fetchVideoComments(postId);
    final ctrl = TextEditingController();
    if (!mounted) return;
    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(bottom: MediaQuery.of(ctx).viewInsets.bottom, left: 16, right: 16, top: 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Commentaires', style: Theme.of(ctx).textTheme.titleMedium),
            ...comments.map((c) {
              final m = Map<String, dynamic>.from(c as Map);
              return ListTile(
                title: Text(m['text']?.toString() ?? ''),
                subtitle: Text(m['author_display']?.toString() ?? ''),
              );
            }),
            TextField(controller: ctrl, decoration: const InputDecoration(labelText: 'Commentaire')),
            FilledButton(
              onPressed: () async {
                await context.read<SigApi>().postVideoComment(postId, ctrl.text.trim());
                Navigator.pop(ctx);
              },
              child: const Text('Publier'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const LoadingView();
    if (_error != null) return ErrorView(message: _error!, onRetry: _load);

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView.builder(
          padding: const EdgeInsets.all(12),
          itemCount: _posts.length + (widget.kind == 'video' && _stories.isNotEmpty ? 1 : 0),
          itemBuilder: (_, i) {
            if (widget.kind == 'video' && _stories.isNotEmpty && i == 0) {
              return SizedBox(
                height: 90,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _stories.length,
                  itemBuilder: (_, si) {
                    final s = Map<String, dynamic>.from(_stories[si] as Map);
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: Chip(label: Text(s['author']?.toString() ?? 'Story')),
                    );
                  },
                ),
              );
            }
            final idx = widget.kind == 'video' && _stories.isNotEmpty ? i - 1 : i;
            final p = Map<String, dynamic>.from(_posts[idx] as Map);
            final thumb = Env.resolveMediaUrl(p['thumbnail_url']?.toString());
            final id = p['id'] as int;
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
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.favorite_border),
                          onPressed: () async {
                            await context.read<SigApi>().toggleVideoLike(id);
                            _load();
                          },
                        ),
                        IconButton(
                          icon: const Icon(Icons.comment),
                          onPressed: () => _showComments(id),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _upload,
        child: const Icon(Icons.upload),
      ),
    );
  }
}
