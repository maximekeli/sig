import { describe, expect, it } from 'vitest';
import {
  QUIZ_TIMER_SECONDS,
  buildAnswerBody,
  formatAnswerFeedback,
  formatFinishMessage,
  formatLeaderboardRow,
  isQuizComplete,
} from '../js/core/quizUtils.js';

describe('quizUtils', () => {
  it('timer TdR = 20s', () => {
    expect(QUIZ_TIMER_SECONDS).toBe(20);
  });

  it('formatAnswerFeedback correct', () => {
    const msg = formatAnswerFeedback({ correct: true, points_earned: 5, explanation: 'OK' });
    expect(msg).toContain('✓');
    expect(msg).toContain('5');
  });

  it('formatFinishMessage', () => {
    const msg = formatFinishMessage({ final_score: 50, badges_earned: ['apprenti'] });
    expect(msg).toContain('50');
    expect(msg).toContain('apprenti');
  });

  it('formatLeaderboardRow', () => {
    expect(formatLeaderboardRow({ pseudonym: 'Agent1', score: 120 }, 0)).toBe('1. Agent1 — 120 pts');
  });

  it('buildAnswerBody borne index négatif', () => {
    expect(buildAnswerBody(3, -1).selected_index).toBe(0);
  });

  it('isQuizComplete', () => {
    expect(isQuizComplete(5, 5)).toBe(true);
    expect(isQuizComplete(2, 5)).toBe(false);
  });
});
