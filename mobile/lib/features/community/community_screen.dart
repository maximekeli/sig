import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../services/sig_api.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';

class CommunityScreen extends StatefulWidget {
  const CommunityScreen({super.key});

  @override
  State<CommunityScreen> createState() => _CommunityScreenState();
}

class _CommunityScreenState extends State<CommunityScreen> with SingleTickerProviderStateMixin {
  late final TabController _tabs;
  final _searchCtrl = TextEditingController();
  final _dmUserCtrl = TextEditingController();
  final _dmBodyCtrl = TextEditingController();

  List<dynamic> _feed = [];
  List<dynamic> _favorites = [];
  List<dynamic> _searchResults = [];
  List<dynamic> _messages = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 4, vsync: this);
    _loadFeed();
  }

  @override
  void dispose() {
    _tabs.dispose();
    _searchCtrl.dispose();
    _dmUserCtrl.dispose();
    _dmBodyCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadFeed() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final feed = await context.read<SigApi>().fetchFeed();
      setState(() {
        _feed = feed;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _loadFavorites() async {
    try {
      final fav = await context.read<SigApi>().fetchFavorites();
      setState(() => _favorites = fav);
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
    }
  }

  Future<void> _searchUsers() async {
    final q = _searchCtrl.text.trim();
    if (q.isEmpty) return;
    final results = await context.read<SigApi>().searchUsers(q);
    setState(() => _searchResults = results);
  }

  Future<void> _loadMessages() async {
    final withUser = _dmUserCtrl.text.trim();
    final msgs = await context.read<SigApi>().fetchMessages(
          withUser: withUser.isEmpty ? null : withUser,
        );
    setState(() => _messages = msgs);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TabBar(
          controller: _tabs,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Fil'),
            Tab(text: 'Recherche'),
            Tab(text: 'Favoris'),
            Tab(text: 'Messages'),
          ],
          onTap: (i) {
            if (i == 1) _searchUsers();
            if (i == 2) _loadFavorites();
            if (i == 3) _loadMessages();
          },
        ),
        Expanded(
          child: _loading && _tabs.index == 0
              ? const LoadingView()
              : _error != null && _tabs.index == 0
                  ? ErrorView(message: _error!, onRetry: _loadFeed)
                  : TabBarView(
                      controller: _tabs,
                      children: [
                        RefreshIndicator(
                          onRefresh: _loadFeed,
                          child: ListView.builder(
                            padding: const EdgeInsets.all(12),
                            itemCount: _feed.length,
                            itemBuilder: (_, i) => _feedTile(_feed[i]),
                          ),
                        ),
                        ListView(
                          padding: const EdgeInsets.all(12),
                          children: [
                            TextField(
                              controller: _searchCtrl,
                              decoration: InputDecoration(
                                hintText: 'Rechercher un membre',
                                suffixIcon: IconButton(
                                  icon: const Icon(Icons.search),
                                  onPressed: _searchUsers,
                                ),
                              ),
                              onSubmitted: (_) => _searchUsers(),
                            ),
                            ..._searchResults.map((u) {
                              final user = Map<String, dynamic>.from(u as Map);
                              final un = user['username']?.toString() ?? '';
                              return ListTile(
                                title: Text(user['display_name']?.toString() ?? un),
                                subtitle: Text('@$un'),
                                trailing: IconButton(
                                  icon: const Icon(Icons.person_add),
                                  onPressed: () async {
                                    await context.read<SigApi>().followUser(un);
                                    if (mounted) {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(content: Text('Abonné à $un')),
                                      );
                                    }
                                  },
                                ),
                              );
                            }),
                          ],
                        ),
                        RefreshIndicator(
                          onRefresh: _loadFavorites,
                          child: ListView.builder(
                            itemCount: _favorites.length,
                            itemBuilder: (_, i) {
                              final f = Map<String, dynamic>.from(_favorites[i] as Map);
                              return ListTile(
                                title: Text(f['title']?.toString() ?? f['target_type']?.toString() ?? '—'),
                                subtitle: Text('${f['target_type']} #${f['target_id']}'),
                              );
                            },
                          ),
                        ),
                        ListView(
                          padding: const EdgeInsets.all(12),
                          children: [
                            TextField(
                              controller: _dmUserCtrl,
                              decoration: const InputDecoration(labelText: 'Utilisateur'),
                            ),
                            Row(
                              children: [
                                Expanded(
                                  child: TextField(
                                    controller: _dmBodyCtrl,
                                    decoration: const InputDecoration(labelText: 'Message'),
                                  ),
                                ),
                                IconButton(
                                  icon: const Icon(Icons.send),
                                  onPressed: () async {
                                    await context.read<SigApi>().sendMessage(
                                          recipientUsername: _dmUserCtrl.text.trim(),
                                          body: _dmBodyCtrl.text.trim(),
                                        );
                                    _dmBodyCtrl.clear();
                                    _loadMessages();
                                  },
                                ),
                              ],
                            ),
                            ..._messages.map((m) {
                              final msg = Map<String, dynamic>.from(m as Map);
                              return ListTile(
                                title: Text(msg['body']?.toString() ?? ''),
                                subtitle: Text(msg['sender']?.toString() ?? msg['created_at']?.toString() ?? ''),
                              );
                            }),
                          ],
                        ),
                      ],
                    ),
        ),
      ],
    );
  }

  Widget _feedTile(dynamic item) {
    final f = Map<String, dynamic>.from(item as Map);
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          child: Text((f['author_username'] ?? '?').toString()[0].toUpperCase()),
        ),
        title: Text(f['title']?.toString() ?? f['kind']?.toString() ?? 'Publication'),
        subtitle: Text(f['author_display']?.toString() ?? ''),
        trailing: Text('❤ ${f['like_count'] ?? 0}'),
      ),
    );
  }
}
