let quizSession = null;
let quizQuestions = [];
let quizIndex = 0;
let quizTimer = null;
let timeLeft = 20;

async function startQuiz() {
  const difficulty = document.getElementById('quiz-difficulty').value;
  const data = await SigSolsAPI.api('/education/quiz/start/', {
    method: 'POST',
    body: JSON.stringify({ difficulty, count: 5 }),
  });
  quizSession = data.session_id;
  quizQuestions = data.questions;
  quizIndex = 0;
  document.getElementById('quiz-area').classList.remove('hidden');
  document.getElementById('quiz-score').textContent = '0';
  showQuestion();
}

function showQuestion() {
  if (quizIndex >= quizQuestions.length) {
    document.getElementById('btn-quiz-finish').classList.remove('hidden');
    clearInterval(quizTimer);
    return;
  }
  const q = quizQuestions[quizIndex];
  document.getElementById('quiz-question').textContent = q.text;
  const choices = document.getElementById('quiz-choices');
  choices.innerHTML = '';
  q.choices.forEach((c, i) => {
    const btn = document.createElement('button');
    btn.className = 'quiz-choice';
    btn.textContent = c;
    btn.onclick = () => submitAnswer(i);
    choices.appendChild(btn);
  });
  timeLeft = 20;
  document.getElementById('quiz-timer').textContent = timeLeft;
  clearInterval(quizTimer);
  quizTimer = setInterval(() => {
    timeLeft -= 1;
    document.getElementById('quiz-timer').textContent = timeLeft;
    if (timeLeft <= 0) submitAnswer(-1);
  }, 1000);
}

async function submitAnswer(selectedIndex) {
  clearInterval(quizTimer);
  const q = quizQuestions[quizIndex];
  const body = { question_id: q.id, selected_index: Math.max(0, selectedIndex) };
  const r = await SigSolsAPI.api(`/education/quiz/${quizSession}/answer/`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
  document.getElementById('quiz-feedback').textContent = r.correct
    ? `✓ Correct (+${r.points_earned}) — ${r.explanation}`
    : `✗ ${r.explanation}`;
  document.getElementById('quiz-score').textContent = r.session_score;
  quizIndex += 1;
  setTimeout(showQuestion, 1500);
}

async function finishQuiz() {
  const r = await SigSolsAPI.api(`/education/quiz/${quizSession}/finish/`, { method: 'POST', body: '{}' });
  document.getElementById('quiz-feedback').textContent =
    `Score final: ${r.final_score}. Badges: ${(r.badges_earned || []).join(', ') || 'aucun'}`;
  loadLeaderboard();
  loadBadges();
}

async function loadLeaderboard() {
  const data = await SigSolsAPI.api('/education/quiz/leaderboard/');
  const ol = document.getElementById('leaderboard');
  ol.innerHTML = '';
  (data.top_10 || []).forEach((row, i) => {
    const li = document.createElement('li');
    li.textContent = `${i + 1}. ${row.pseudonym} — ${row.score} pts`;
    ol.appendChild(li);
  });
}

async function loadBadges() {
  if (!SigSolsAPI.getToken()) return;
  const data = await SigSolsAPI.api('/education/quiz/badges/');
  const ul = document.getElementById('my-badges');
  ul.innerHTML = '';
  data.forEach((b) => {
    const li = document.createElement('li');
    li.textContent = b.badge;
    ul.appendChild(li);
  });
}

async function loadSheets() {
  const data = await SigSolsAPI.api('/education/sheets/');
  const list = document.getElementById('sheets-list');
  list.innerHTML = '<h2>Fiches pédagogiques</h2>';
  (data.results || data).forEach((s) => {
    const div = document.createElement('article');
    div.className = 'sheet-card';
    div.innerHTML = `<h3>${s.title}</h3><p>${s.content_fr}</p>`;
    list.appendChild(div);
  });
}

window.SigSolsQuiz = { startQuiz, finishQuiz, loadLeaderboard, loadBadges, loadSheets };
