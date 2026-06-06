import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/config/env.dart';
import '../../services/sig_api.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';
import 'package:url_launcher/url_launcher.dart';

class QuizScreen extends StatefulWidget {
  const QuizScreen({super.key});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  Map<String, dynamic>? _stats;
  List<dynamic>? _leaderboard;
  int? _sessionId;
  List<dynamic> _questions = [];
  int _qIndex = 0;
  int _score = 0;
  String _feedback = '';
  bool _loading = true;
  bool _finished = false;
  Map<String, dynamic>? _finishResult;
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
        _leaderboard = board is List
            ? board
            : ((board as Map)['top_10'] as List? ?? (board as Map)['results'] as List? ?? []);
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
    setState(() {
      _loading = true;
      _finished = false;
      _finishResult = null;
      _feedback = '';
      _score = 0;
    });
    try {
      final data = await context.read<SigApi>().startQuiz();
      setState(() {
        _sessionId = data['session_id'] as int?;
        _questions = data['questions'] as List? ?? [];
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

  Future<void> _answer(int selectedIndex) async {
    if (_sessionId == null || _qIndex >= _questions.length) return;
    final q = _questions[_qIndex] as Map<String, dynamic>;
    try {
      final r = await context.read<SigApi>().submitQuizAnswer(
            _sessionId!,
            questionId: q['id'] as int,
            selectedIndex: selectedIndex,
          );
      setState(() {
        _score = r['session_score'] as int? ?? _score;
        _feedback = r['correct'] == true
            ? '✓ Correct (+${r['points_earned']})'
            : '✗ ${r['explanation'] ?? ''}';
        _qIndex++;
      });
      if (_qIndex >= _questions.length) await _finish();
    } catch (e) {
      setState(() => _feedback = 'Erreur: $e');
    }
  }

  Future<void> _finish() async {
    if (_sessionId == null) return;
    try {
      final r = await context.read<SigApi>().finishQuiz(_sessionId!);
      setState(() {
        _finished = true;
        _finishResult = r;
      });
    } catch (e) {
      setState(() => _feedback = 'Erreur finish: $e');
    }
  }

  void _reset() {
    setState(() {
      _sessionId = null;
      _questions = [];
      _qIndex = 0;
      _finished = false;
      _finishResult = null;
      _feedback = '';
    });
    _load();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const LoadingView();
    if (_error != null) return ErrorView(message: _error!, onRetry: _load);

    if (_finished && _finishResult != null) {
      final score = _finishResult!['final_score'] ?? _finishResult!['score'] ?? _score;
      return ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('Quiz terminé !', style: Theme.of(context).textTheme.headlineSmall),
          Text('Score final: $score'),
          Text('Badges: ${(_finishResult!['badges_earned'] as List?)?.join(', ') ?? 'aucun'}'),
          const SizedBox(height: 16),
          if (_sessionId != null && (score as num) >= 10)
            FilledButton.icon(
              onPressed: () => launchUrl(
                Uri.parse('${Env.origin}/api/v1/education/quiz/$_sessionId/certificate/'),
              ),
              icon: const Icon(Icons.workspace_premium),
              label: const Text('Certificat PDF'),
            ),
          FilledButton(onPressed: _reset, child: const Text('Nouveau quiz')),
        ],
      );
    }

    if (_sessionId != null && _qIndex < _questions.length) {
      final q = _questions[_qIndex] as Map<String, dynamic>;
      final choices = q['choices'] as List? ?? [];
      return Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Question ${_qIndex + 1}/${_questions.length} · Score: $_score'),
            if (_feedback.isNotEmpty) Text(_feedback, style: TextStyle(color: _feedback.startsWith('✓') ? Colors.green : Colors.redAccent)),
            const SizedBox(height: 12),
            Text(q['text']?.toString() ?? '', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            ...choices.asMap().entries.map((e) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: OutlinedButton(
                    onPressed: () => _answer(e.key),
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
            subtitle: Text('Meilleur: ${_stats?['best_score'] ?? '—'} · Parties: ${_stats?['sessions_count'] ?? '—'}'),
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
            title: Text(m['pseudonym']?.toString() ?? m['username']?.toString() ?? '—'),
            trailing: Text('${m['score'] ?? m['best_score'] ?? ''}'),
          );
        }),
      ],
    );
  }
}
