export const QUIZ_TIMER_SECONDS = 20;

export function formatAnswerFeedback(result) {
  if (result.correct) {
    return `✓ Correct (+${result.points_earned}) — ${result.explanation}`;
  }
  return `✗ ${result.explanation}`;
}

export function formatFinishMessage(result) {
  const badges = (result.badges_earned || []).join(', ') || 'aucun';
  return `Score final: ${result.final_score}. Badges: ${badges}`;
}

export function formatLeaderboardRow(row, index) {
  return `${index + 1}. ${row.pseudonym} — ${row.score} pts`;
}

export function buildAnswerBody(questionId, selectedIndex) {
  return {
    question_id: questionId,
    selected_index: Math.max(0, selectedIndex),
  };
}

export function isQuizComplete(quizIndex, questionsLength) {
  return quizIndex >= questionsLength;
}

export function formatPoolInfo(stats) {
  const b = stats.by_level || {};
  const f = b.facile ?? 0;
  const m = b.moyen ?? 0;
  const d = b.difficile ?? 0;
  return `Banque : Facile ${f} · Moyen ${m} · Difficile ${d} questions (objectif 100/niveau)`;
}

export function updateProgress(currentIndex, total) {
  const fill = document.getElementById('quiz-progress-fill');
  if (!fill || !total) return;
  const pct = Math.min(100, Math.round((currentIndex / total) * 100));
  fill.style.width = `${pct}%`;
}
