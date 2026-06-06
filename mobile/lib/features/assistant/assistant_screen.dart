import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../services/sig_api.dart';

class AssistantScreen extends StatefulWidget {
  const AssistantScreen({super.key});

  @override
  State<AssistantScreen> createState() => _AssistantScreenState();
}

class _AssistantScreenState extends State<AssistantScreen> {
  final _ctrl = TextEditingController();
  final _messages = <Map<String, String>>[];
  Map<String, dynamic>? _status;
  bool _loading = false;
  bool _ready = false;

  @override
  void initState() {
    super.initState();
    _checkStatus();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _checkStatus() async {
    try {
      final s = await context.read<SigApi>().assistantStatus();
      setState(() {
        _status = s;
        _ready = s['available'] == true;
      });
    } catch (e) {
      setState(() => _status = {'available': false, 'message': e.toString()});
    }
  }

  Future<void> _send() async {
    final text = _ctrl.text.trim();
    if (text.isEmpty || _loading || !_ready) return;
    _ctrl.clear();
    setState(() {
      _messages.add({'role': 'user', 'content': text});
      _loading = true;
    });
    try {
      final res = await context.read<SigApi>().assistantChat(
            message: text,
            history: _messages.where((m) => m['role'] != 'system').toList(),
            context: {
              'view': 'mobile',
              'platform': 'flutter',
              'model': _status?['model'],
            },
          );
      setState(() {
        _messages.add({
          'role': 'assistant',
          'content': res['reply']?.toString() ?? res['message']?.toString() ?? '—',
        });
      });
    } catch (e) {
      setState(() {
        _messages.add({'role': 'assistant', 'content': 'Erreur Gemini: $e'});
      });
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        if (_status != null)
          Material(
            color: _ready ? Colors.green.withValues(alpha: 0.15) : Colors.orange.withValues(alpha: 0.15),
            child: ListTile(
              dense: true,
              leading: Icon(_ready ? Icons.smart_toy : Icons.warning_amber),
              title: Text(_ready
                  ? 'Gemini ${_status!['model'] ?? ''} — via /api/v1/assistant/'
                  : 'Gemini indisponible: ${_status!['message'] ?? 'clé manquante'}'),
            ),
          ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: _messages.length,
            itemBuilder: (_, i) {
              final m = _messages[i];
              final isUser = m['role'] == 'user';
              return Align(
                alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  margin: const EdgeInsets.symmetric(vertical: 4),
                  padding: const EdgeInsets.all(12),
                  constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
                  decoration: BoxDecoration(
                    color: isUser
                        ? Theme.of(context).colorScheme.primary.withValues(alpha: 0.2)
                        : Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(m['content'] ?? ''),
                ),
              );
            },
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(8),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _ctrl,
                  enabled: _ready,
                  decoration: const InputDecoration(hintText: 'Question sols, parcelles, NDVI…'),
                  onSubmitted: (_) => _send(),
                ),
              ),
              IconButton(
                onPressed: _loading || !_ready ? null : _send,
                icon: _loading
                    ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Icon(Icons.send),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
