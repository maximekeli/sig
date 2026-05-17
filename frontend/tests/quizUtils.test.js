import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  QUIZ_TIMER_SECONDS,
  buildAnswerBody,
  formatAnswerFeedback,
  formatFinishMessage,
  formatLeaderboardRow,
  isQuizComplete,
} from '../js/core/quizUtils.js';

describe('quizUtils', () => {
  it('timer 20s', () => {
    assert.equal(QUIZ_TIMER_SECONDS, 20);
  });

  it('formatAnswerFeedback correct et incorrect', () => {
    assert.ok(formatAnswerFeedback({ correct: true, points_earned: 5, explanation: 'OK' }).includes('✓'));
    assert.ok(formatAnswerFeedback({ correct: false, points_earned: 0, explanation: 'Non' }).includes('✗'));
  });

  it('formatFinishMessage', () => {
    assert.ok(formatFinishMessage({ final_score: 50, badges_earned: ['apprenti'] }).includes('apprenti'));
    assert.ok(formatFinishMessage({ final_score: 10, badges_earned: [] }).includes('aucun'));
  });

  it('formatLeaderboardRow', () => {
    assert.equal(formatLeaderboardRow({ pseudonym: 'Agent1', score: 120 }, 0), '1. Agent1 — 120 pts');
  });

  it('buildAnswerBody', () => {
    assert.equal(buildAnswerBody(3, -1).selected_index, 0);
    assert.equal(buildAnswerBody(3, 2).selected_index, 2);
  });

  it('isQuizComplete', () => {
    assert.equal(isQuizComplete(5, 5), true);
    assert.equal(isQuizComplete(2, 5), false);
  });
});
