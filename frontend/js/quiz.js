import {
  QUIZ_TIMER_SECONDS,
  buildAnswerBody,
  formatAnswerFeedback,
  formatFinishMessage,
  formatLeaderboardRow,
  formatPoolInfo,
  isQuizComplete,
  updateProgress,
} from './core/quizUtils.js';
import { notifyError } from './core/ui.js';

let quizSession = null;
let quizQuestions = [];
let quizIndex = 0;
let quizTimer = null;
let timeLeft = QUIZ_TIMER_SECONDS;
let answerInFlight = false;

function getQuizCount() {
  const el = document.getElementById('quiz-count');
  return el ? parseInt(el.value, 10) || 10 : 10;
}

async function loadQuizStats() {
  const info = document.getElementById('quiz-pool-info');
  if (!info) return;
  try {
    const data = await SigSolsAPI.api('/education/quiz/stats/');
    info.textContent = formatPoolInfo(data);
    info.dataset.loaded = '1';
  } catch {
    info.textContent = 'Banque : 100 questions par niveau (après chargement serveur).';
  }
}

async function startQuiz() {
  const difficulty = document.getElementById('quiz-difficulty').value;
  const count = getQuizCount();
  const data = await SigSolsAPI.api('/education/quiz/start/', {
    method: 'POST',
    body: JSON.stringify({ difficulty, count }),
  });
  quizSession = data.session_id;
  quizQuestions = data.questions;
  quizIndex = 0;
  document.getElementById('quiz-area').classList.remove('hidden');
  document.getElementById('btn-quiz-finish').classList.add('hidden');
  document.getElementById('quiz-score').textContent = '0';
  document.getElementById('quiz-feedback').textContent = '';
  document.getElementById('quiz-total').textContent = String(quizQuestions.length);
  document.getElementById('btn-quiz-start').disabled = true;
  updateProgress(quizIndex, quizQuestions.length);
  showQuestion();
}

function showQuestion() {
  if (isQuizComplete(quizIndex, quizQuestions.length)) {
    document.getElementById('btn-quiz-finish').classList.remove('hidden');
    clearInterval(quizTimer);
    updateProgress(quizQuestions.length, quizQuestions.length);
    return;
  }
  const q = quizQuestions[quizIndex];
  document.getElementById('quiz-current').textContent = String(quizIndex + 1);
  updateProgress(quizIndex, quizQuestions.length);
  document.getElementById('quiz-question').textContent = q.text;
  const choices = document.getElementById('quiz-choices');
  choices.innerHTML = '';
  q.choices.forEach((c, i) => {
    const btn = document.createElement('button');
    btn.className = 'quiz-choice';
    btn.textContent = c;
    btn.style.animationDelay = `${i * 0.05}s`;
    btn.onclick = () => submitAnswer(i);
    choices.appendChild(btn);
  });
  timeLeft = QUIZ_TIMER_SECONDS;
  document.getElementById('quiz-timer').textContent = timeLeft;
  clearInterval(quizTimer);
  quizTimer = setInterval(() => {
    timeLeft -= 1;
    document.getElementById('quiz-timer').textContent = timeLeft;
    if (timeLeft <= 0) submitAnswer(-1);
  }, 1000);
}

async function submitAnswer(selectedIndex) {
  if (answerInFlight) return;
  answerInFlight = true;
  clearInterval(quizTimer);
  const q = quizQuestions[quizIndex];
  const buttons = document.querySelectorAll('#quiz-choices .quiz-choice');
  buttons.forEach((b) => { b.disabled = true; });

  try {
    const r = await SigSolsAPI.api(`/education/quiz/${quizSession}/answer/`, {
      method: 'POST',
      body: JSON.stringify(buildAnswerBody(q.id, selectedIndex)),
    });
    const feedback = document.getElementById('quiz-feedback');
    feedback.textContent = formatAnswerFeedback(r);
    feedback.className = r.correct ? 'quiz-feedback quiz-feedback--ok' : 'quiz-feedback quiz-feedback--ko';
    document.getElementById('quiz-score').textContent = r.session_score;
    quizIndex += 1;
    answerInFlight = false;
    setTimeout(showQuestion, 1500);
  } catch (e) {
    notifyError(e);
    answerInFlight = false;
    buttons.forEach((b) => { b.disabled = false; });
    timeLeft = QUIZ_TIMER_SECONDS;
    document.getElementById('quiz-timer').textContent = timeLeft;
    quizTimer = setInterval(() => {
      timeLeft -= 1;
      document.getElementById('quiz-timer').textContent = timeLeft;
      if (timeLeft <= 0) submitAnswer(-1);
    }, 1000);
  }
}

async function finishQuiz() {
  const r = await SigSolsAPI.api(`/education/quiz/${quizSession}/finish/`, { method: 'POST', body: '{}' });
  document.getElementById('quiz-feedback').textContent = formatFinishMessage(r);
  document.getElementById('quiz-feedback').className = 'quiz-feedback quiz-feedback--ok';
  document.getElementById('btn-quiz-start').disabled = false;
  document.getElementById('btn-quiz-finish').classList.add('hidden');
  loadLeaderboard();
  loadBadges();
}

async function loadLeaderboard() {
  const data = await SigSolsAPI.api('/education/quiz/leaderboard/');
  const ol = document.getElementById('leaderboard');
  ol.innerHTML = '';
  (data.top_10 || []).forEach((row, i) => {
    const li = document.createElement('li');
    li.textContent = formatLeaderboardRow(row, i);
    li.style.animationDelay = `${i * 0.06}s`;
    ol.appendChild(li);
  });
}

async function loadBadges() {
  if (!SigSolsAPI.getToken()) return;
  const data = await SigSolsAPI.api('/education/quiz/badges/');
  const ul = document.getElementById('my-badges');
  ul.innerHTML = '';
  data.forEach((b, i) => {
    const li = document.createElement('li');
    li.textContent = b.badge;
    li.className = 'badge-item';
    li.style.animationDelay = `${i * 0.05}s`;
    ul.appendChild(li);
  });
}

async function loadSheets() {
  const data = await SigSolsAPI.api('/education/sheets/');
  const list = document.getElementById('sheets-list');
  list.innerHTML = '';
  const rows = data.results || data;
  rows.forEach((s, i) => {
    const div = document.createElement('article');
    div.className = 'sheet-card';
    div.style.animationDelay = `${i * 0.08}s`;
    const pdfHref = s.pdf_url || '';
    const pdfBtn = pdfHref
      ? `<p class="sheet-pdf-row"><a class="sheet-pdf-link" href="${pdfHref}" target="_blank" rel="noopener">Télécharger le PDF complet (≈ 20+ pages)</a></p>`
      : '';
    div.innerHTML = `
      <h3>${s.title}</h3>
      <p class="sheet-excerpt">${s.content_fr}</p>
      ${pdfBtn}`;
    list.appendChild(div);
  });
}

window.SigSolsQuiz = {
  startQuiz,
  finishQuiz,
  loadLeaderboard,
  loadBadges,
  loadSheets,
  loadQuizStats,
};
