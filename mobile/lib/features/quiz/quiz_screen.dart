import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../services/sig_api.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';

class QuizScreen extends StatefulWidget {
  const QuizScreen({super.key});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  Map<String, dynamic>? _stats;
  List<dynamic>? _leaderboard;
  Map<String, dynamic>? _session;
  int _qIndex = 0;
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
      final stats = await api.quizStats();
      final board = await api.quizLeaderboard();
      setState(() {
        _stats = stats;
        _leaderboard = board is List ? board : (board['results'] as List? ?? []);
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _startQuiz() async {
    setState(() => _loading = true);
    try {
      final session = await context.read<SigApi>().startQuiz();
      setState(() {
        _session = session;
        _qIndex = 0;
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

    if (_session != null) {
      final questions = _session!['questions'] as List? ?? [];
      if (_qIndex >= questions.length) {
        return Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Quiz terminé !'),
              FilledButton(onPressed: () => setState(() => _session = null), child: const Text('Retour')),
            ],
          ),
        );
      }
      final q = questions[_qIndex] as Map<String, dynamic>;
      final choices = q['choices'] as List? ?? [];
      return Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Question ${_qIndex + 1}/${questions.length}', style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 12),
            Text(q['text']?.toString() ?? '', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            ...choices.asMap().entries.map((e) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: OutlinedButton(
                    onPressed: () => setState(() => _qIndex++),
                    child: Align(alignment: Alignment.centerLeft, child: Text(e.value.toString())),
                  ),
                )),
          ],
        ),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: ListTile(
            title: const Text('Mes statistiques'),
            subtitle: Text('Score: ${_stats?['best_score'] ?? '—'} · Parties: ${_stats?['sessions_count'] ?? '—'}'),
          ),
        ),
        FilledButton.icon(
          onPressed: _startQuiz,
          icon: const Icon(Icons.play_arrow),
          label: const Text('Démarrer un quiz'),
        ),
        const SizedBox(height: 16),
        Text('Classement', style: Theme.of(context).textTheme.titleMedium),
        ...(_leaderboard ?? []).take(10).map((e) {
          final m = Map<String, dynamic>.from(e as Map);
          return ListTile(
            title: Text(m['username']?.toString() ?? m['pseudonym']?.toString() ?? '—'),
            trailing: Text('${m['score'] ?? m['best_score'] ?? ''}'),
          );
        }),
      ],
    );
  }
}
