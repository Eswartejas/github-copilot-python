// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudokuLeaderboard';
const THEME_KEY = 'sudokuTheme';
let puzzle = [];
let elapsedSeconds = 0;
let timerInterval = null;
let currentDifficulty = 'medium';
let gameCompleted = false;

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timerDisplay = document.getElementById('timer-display');
  if (timerDisplay) {
    timerDisplay.innerText = formatTime(elapsedSeconds);
  }
}

function loadTheme() {
  return localStorage.getItem(THEME_KEY) || 'light';
}

function saveTheme(theme) {
  localStorage.setItem(THEME_KEY, theme);
}

function applyTheme(theme) {
  document.body.classList.toggle('dark-theme', theme === 'dark');
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.innerText = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
  }
}

function toggleTheme() {
  const nextTheme = document.body.classList.contains('dark-theme') ? 'light' : 'dark';
  applyTheme(nextTheme);
  saveTheme(nextTheme);
}

function loadLeaderboard() {
  try {
    const raw = localStorage.getItem(LEADERBOARD_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (err) {
    return [];
  }
}

function saveLeaderboard(scores) {
  localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores));
}

function renderLeaderboard() {
  const leaderboard = document.getElementById('leaderboard');
  const scores = loadLeaderboard();
  if (!leaderboard) return;
  if (scores.length === 0) {
    leaderboard.innerHTML = 'No scores yet.';
    return;
  }

  const rows = scores.map((entry, index) => {
    return `
      <tr>
        <td>${index + 1}</td>
        <td>${entry.name}</td>
        <td>${entry.difficulty}</td>
        <td>${formatTime(entry.time)}</td>
      </tr>`;
  }).join('');

  leaderboard.innerHTML = `
    <table class="leaderboard-table">
      <thead>
        <tr><th>#</th><th>Name</th><th>Difficulty</th><th>Time</th></tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
}

function addLeaderboardEntry(name, time, difficulty) {
  const scores = loadLeaderboard();
  scores.push({name, time, difficulty, timestamp: Date.now()});
  scores.sort((a, b) => a.time - b.time);
  const topScores = scores.slice(0, 10);
  saveLeaderboard(topScores);
  renderLeaderboard();
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function disableBoardInputs() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  for (let idx = 0; idx < inputs.length; idx++) {
    inputs[idx].disabled = true;
  }
}

function setHintButtonState(enabled) {
  const hintButton = document.getElementById('hint-button');
  if (hintButton) {
    hintButton.disabled = !enabled;
  }
}

function resetTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
}

function startTimer() {
  resetTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      const blockClass = ((Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 0) ? 'block-light' : 'block-dark';
      input.className = `sudoku-cell ${blockClass}`;
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        e.target.classList.remove('incorrect');
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function setMessage(text, color = '#000') {
  const message = document.getElementById('message');
  message.style.color = color;
  message.innerText = text;
}

async function newGame() {
  gameCompleted = false;
  currentDifficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(currentDifficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  setMessage(`Difficulty: ${data.difficulty} (${data.clues} clues)`);
  setHintButtonState(true);
  startTimer();
}

async function requestHint() {
  if (gameCompleted) {
    setMessage('Puzzle already completed. Start a new game to continue.', '#388e3c');
    return;
  }
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
  });
  const data = await res.json();
  if (data.error) {
    setMessage(data.error, '#d32f2f');
    return;
  }

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const idx = data.row * SIZE + data.col;
  const input = inputs[idx];
  input.value = data.value;
  input.disabled = true;
  input.className = 'sudoku-cell prefilled';
  setMessage(`Hint revealed at row ${data.row + 1}, col ${data.col + 1}`, '#388e3c');
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (data.solved) {
    stopTimer();
    gameCompleted = true;
    disableBoardInputs();
    setHintButtonState(false);
    const playerName = prompt('Puzzle solved! Enter your name for the leaderboard:', 'Anonymous');
    const normalizedName = playerName && playerName.trim() ? playerName.trim() : 'Anonymous';
    addLeaderboardEntry(normalizedName, elapsedSeconds, currentDifficulty);
    msg.style.color = '#388e3c';
    msg.innerText = `Congratulations! You solved the ${currentDifficulty} puzzle in ${formatTime(elapsedSeconds)}.`;
  } else if (incorrect.size === 0) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'The puzzle is not complete yet.';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  renderLeaderboard();
  applyTheme(loadTheme());
  // initialize
  newGame();
});