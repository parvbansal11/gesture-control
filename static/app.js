const socket = io();

// Section navigation
function showSection(name, el) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('section-' + name).classList.add('active');
  el.classList.add('active');
}

// Logging
function log(message, type = '') {
  const feed = document.getElementById('logFeed');
  const entry = document.createElement('div');
  const time = new Date().toLocaleTimeString();
  entry.className = 'log-entry ' + type;
  entry.textContent = `[${time}] ${message}`;
  feed.appendChild(entry);
  feed.scrollTop = feed.scrollHeight;
}

// Update status UI
function updateStatusUI(status) {
  const dot = document.getElementById('statusDot');
  const label = document.getElementById('statusLabel');
  const cardStatus = document.getElementById('cardStatus');
  dot.className = 'status-dot ' + status;
  if (status === 'running') {
    label.textContent = 'System Running';
    cardStatus.textContent = 'Running';
  } else if (status === 'training') {
    label.textContent = 'Retraining...';
    cardStatus.textContent = 'Training';
  } else {
    label.textContent = 'System Stopped';
    cardStatus.textContent = 'Stopped';
  }
}

// Start engine
async function startEngine() {
  await fetch('/api/engine/start', { method: 'POST' });
  updateStatusUI('running');
  log('Gesture recognition started.', 'info');
}

// Stop engine
async function stopEngine() {
  await fetch('/api/engine/stop', { method: 'POST' });
  updateStatusUI('stopped');
  log('Gesture recognition stopped.', 'error');
}

// Retrain
async function retrain() {
  await fetch('/api/retrain', { method: 'POST' });
  updateStatusUI('training');
  log('Retraining model...', 'info');
}

// Socket events
socket.on('retrain_complete', (data) => {
  updateStatusUI('stopped');
  log(data.message, 'action');
});

// Poll status every 2 seconds
let previousAction = null;

setInterval(async () => {
  const res = await fetch('/api/engine/status');
  const data = await res.json();

  if (data.last_gesture) {
    document.getElementById('cardGesture').textContent = data.last_gesture;
  }

  if (data.last_action && data.last_action !== previousAction) {
    document.getElementById('cardAction').textContent = data.last_action;
    log(`Action triggered: ${data.last_action}`, 'action');
    previousAction = data.last_action;
  }
}, 2000);

// Load gestures
async function loadGestures() {
  const res = await fetch('/api/gestures');
  const data = await res.json();

  document.getElementById('cardTotal').textContent = data.gestures.length;

  const list = document.getElementById('gestureList');
  list.innerHTML = '';

  data.gestures.forEach(g => {
    const item = document.createElement('div');
    item.className = 'gesture-item';
    item.innerHTML = `
      <div class="gesture-info">
        <div class="gesture-name">${g.name}</div>
        <div class="gesture-desc">${g.description || 'No description'}</div>
      </div>
      <div class="gesture-badge">${g.action}</div>
      <button class="delete-btn" onclick="deleteGesture(${g.id})">Delete</button>
    `;
    list.appendChild(item);
  });
}

// Add gesture
async function addGesture() {
  const name = document.getElementById('gestureName').value.trim();
  const action = document.getElementById('gestureAction').value;
  const description = document.getElementById('gestureDesc').value.trim();

  if (!name) {
    log('Please enter a gesture name.', 'error');
    return;
  }

  await fetch('/api/gestures', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, action, description })
  });

  document.getElementById('gestureName').value = '';
  document.getElementById('gestureDesc').value = '';
  log(`Gesture "${name}" added.`, 'action');
  loadGestures();
}

// Delete gesture
async function deleteGesture(id) {
  await fetch(`/api/gestures/${id}`, { method: 'DELETE' });
  log('Gesture deleted.', 'error');
  loadGestures();
}

// Record gesture
async function recordGesture() {
  const recordStatus = document.getElementById('recordStatus');
  const recordResult = document.getElementById('recordResult');
  const countdownNum = document.getElementById('countdownNum');

  recordStatus.style.display = 'block';
  recordResult.textContent = '';
  countdownNum.textContent = '3';

  await fetch('/api/gestures/record', { method: 'POST' });

  let count = 3;
  const timer = setInterval(() => {
    count--;
    countdownNum.textContent = count;
    if (count <= 0) {
      clearInterval(timer);
      countdownNum.textContent = '✓';
    }
  }, 1000);
}

// Record complete
socket.on('record_complete', (data) => {
  const recordResult = document.getElementById('recordResult');
  if (data.finger_count === -1) {
    recordResult.textContent = '❌ No hand detected. Try again.';
    recordResult.style.color = '#f87171';
  } else {
    recordResult.textContent = `✅ Detected ${data.finger_count} fingers. Click + Add to save.`;
    recordResult.style.color = '#4ade80';
  }
});

// Start webcam
async function startWebcam() {
  try {
    const video = document.getElementById('cameraFeed');
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 1280, height: 720 }
    });
    video.srcObject = stream;
    video.onloadedmetadata = () => {
      video.play();
      log('Camera connected.', 'info');
    };
  } catch (err) {
    log('Camera error: ' + err.message, 'error');
    console.error('Camera error:', err);
  }
}

// Init
loadGestures();
startWebcam();
