import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  QUIZ_TIMER_SECONDS,
  buildAnswerBody,
  formatAnswerFeedback,
  isQuizComplete,
} from '../js/core/quizUtils.js';

describe('quizUtils', () => {
  it('timer 20s', () => {
    assert.equal(QUIZ_TIMER_SECONDS, 20);
  });

  it('formatAnswerFeedback', () => {
    const msg = formatAnswerFeedback({ correct: true, points_earned: 5, explanation: 'OK' });
    assert.ok(msg.includes('✓'));
  });

  it('buildAnswerBody', () => {
    assert.equal(buildAnswerBody(3, -1).selected_index, 0);
  });

  it('isQuizComplete', () => {
    assert.equal(isQuizComplete(5, 5), true);
  });
});
