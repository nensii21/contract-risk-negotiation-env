const canvas = document.getElementById('bg-canvas') || createCanvas();
const endpointSelect  = document.getElementById("endpoint-select");
const baseUrlInput    = document.getElementById("base-url");
const bodyGroup       = document.getElementById("body-group");
const bodyInput       = document.getElementById("body-input");
const runBtn          = document.getElementById("run-btn");
const btnText         = document.getElementById("btn-text");
const btnLoader       = document.getElementById("btn-loader");
const outputCard      = document.getElementById("output-card");
const outputBox       = document.getElementById("output-box");
const statusBadge     = document.getElementById("status-badge");
const responseTime    = document.getElementById("response-time");
const copyBtn         = document.getElementById("copy-btn");

let lastJson = null;
let particles = [];
let animationId;
let confettiCanvas;
let confettiCtx;

endpointSelect.addEventListener("change", updateUI);

// Theme toggle
const themeToggle = document.createElement('button');
themeToggle.innerHTML = '🌙';
themeToggle.className = 'theme-toggle';
themeToggle.title = 'Toggle theme';
document.querySelector('.header').appendChild(themeToggle);
themeToggle.addEventListener('click', toggleTheme);

function toggleTheme() {
  document.documentElement.dataset.theme = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', document.documentElement.dataset.theme);
}

if (localStorage.getItem('theme') === 'light') {
  document.documentElement.dataset.theme = 'light';
}

updateUI();

function updateUI() {
  const val = endpointSelect.value;
  bodyGroup.style.display     = val === "POST /step" ? "block" : "none";
}

function createCanvas() {
  const canvas = document.createElement('canvas');
  canvas.id = 'bg-canvas';
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.zIndex = '-1';
  canvas.style.pointerEvents = 'none';
  document.body.appendChild(canvas);
  return canvas;
}

function initParticles() {
  const c = canvas;
  c.width = window.innerWidth;
  c.height = window.innerHeight;
  const ctx = c.getContext('2d');
  particles = [];

  for (let i = 0; i < 100; i++) {
    particles.push({
      x: Math.random() * c.width,
      y: Math.random() * c.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      radius: Math.random() * 2 + 1,
      color: `hsl(${200 + Math.random() * 60}, 70%, ${50 + Math.random() * 30}%)`
    });
  }

  function animate() {
    ctx.clearRect(0, 0, c.width, c.height);
    
    const mouse = { x: c.width / 2, y: c.height / 2 };
    canvas.onmousemove = (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };

    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > c.width) p.vx *= -1;
      if (p.y < 0 || p.y > c.height) p.vy *= -1;

      const dx = mouse.x - p.x;
      const dy = mouse.y - p.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 100) {
        p.vx += dx / dist * 0.1;
        p.vy += dy / dist * 0.1;
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();
    });

    // Connecting lines
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.lineWidth = (1 - dist / 120) * 0.5;
          ctx.strokeStyle = `rgba(90,154,255,${(1 - dist / 120) * 0.3})`;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }

    animationId = requestAnimationFrame(animate);
  }
  animate();
}

window.addEventListener('resize', () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});

initParticles();

document.querySelectorAll(".preset-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    bodyInput.value = btn.dataset.value;
    bodyInput.focus();
  });
});

runBtn.addEventListener("click", async () => {
  const val = endpointSelect.value;
  const [method, path] = val.split(" ");
  await sendRequest(method, path);
});

async function sendRequest(method, path) {
  setLoading(true);

  const baseUrl = baseUrlInput ? baseUrlInput.value.trim() || 'http://127.0.0.1:7860' : 'http://127.0.0.1:7860';
  let url = baseUrl.replace(/\/$/, '') + path;
  let options = { method, headers: {} };

  if (method === "POST") {
    const raw = bodyInput.value.trim();
    if (!raw) {
      showError("Request body is required for POST /step.");
      setLoading(false);
      return;
    }
    try {
      JSON.parse(raw);
    } catch {
      showError("Invalid JSON in request body.");
      setLoading(false);
      return;
    }
    options.headers["Content-Type"] = "application/json";
    options.body = raw;
  }

  const start = Date.now();

  try {
    const response = await fetch(url, options);
    const elapsed  = Date.now() - start;
    const text     = await response.text();

    let data;
    try { data = JSON.parse(text); } catch { data = text; }

    lastJson = typeof data === "object" ? data : null;
    showOutput(data, response.status, response.ok, elapsed);
  } catch (err) {
    showError(`Network error: ${err.message}`);
  } finally {
    setLoading(false);
  }
}

function showOutput(data, status, ok, elapsed) {
  outputCard.style.display = "block";

  statusBadge.textContent = `${status} ${ok ? "OK" : "ERROR"}`;
  statusBadge.className   = `badge ${ok ? "ok" : "error"}`;
  responseTime.textContent = `${elapsed}ms`;

  const formatted = typeof data === "object"
    ? syntaxHighlight(JSON.stringify(data, null, 2))
    : escapeHtml(String(data));

  outputBox.innerHTML = formatted;
  outputCard.scrollIntoView({ behavior: "smooth", block: "nearest" });

  if (ok) {
    launchConfetti();
  }
}

function launchConfetti() {
  confettiCanvas = document.createElement('canvas');
  confettiCtx = confettiCanvas.getContext('2d');
  confettiCanvas.style.position = 'fixed';
  confettiCanvas.style.top = '0';
  confettiCanvas.style.left = '0';
  confettiCanvas.style.width = '100%';
  confettiCanvas.style.height = '100%';
  confettiCanvas.style.pointerEvents = 'none';
  confettiCanvas.width = window.innerWidth;
  confettiCanvas.height = window.innerHeight;
  document.body.appendChild(confettiCanvas);

  const confetti = [];
  for (let i = 0; i < 100; i++) {
    confetti.push({
      x: Math.random() * confettiCanvas.width,
      y: -10,
      vx: (Math.random() - 0.5) * 10,
      vy: Math.random() * 5 + 5,
      size: Math.random() * 5 + 3,
      color: ['#5a9aff', '#a855f7', '#3ecf8e', '#f87171'][Math.floor(Math.random() * 4)]
    });
  }

  function animateConfetti() {
    confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
    let active = false;

    confetti.forEach((p, i) => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.1;
      p.vx *= 0.99;

      if (p.y < confettiCanvas.height) {
        confettiCtx.fillStyle = p.color;
        confettiCtx.fillRect(p.x, p.y, p.size, p.size);
        active = true;
      } else {
        confetti.splice(i, 1);
      }
    });

    if (active) {
      requestAnimationFrame(animateConfetti);
    } else {
      document.body.removeChild(confettiCanvas);
    }
  }
  animateConfetti();
}

function showError(message) {
  outputCard.style.display = "block";
  statusBadge.textContent  = "Error";
  statusBadge.className    = "badge error";
  responseTime.textContent = "";
  outputBox.innerHTML = `<span class="error-msg">⚠ ${escapeHtml(message)}</span>`;
  lastJson = null;
}

function setLoading(on) {
  runBtn.disabled       = on;
  btnText.style.display = on ? "none"   : "inline";
  btnLoader.style.display = on ? "inline-flex" : "none";
}

copyBtn.addEventListener("click", () => {
  const text = lastJson
    ? JSON.stringify(lastJson, null, 2)
    : outputBox.innerText;

  navigator.clipboard.writeText(text).then(() => {
    copyBtn.textContent  = "Copied!";
    copyBtn.classList.add("copied");
    setTimeout(() => {
      copyBtn.textContent = "Copy";
      copyBtn.classList.remove("copied");
    }, 1800);
  });
});

function syntaxHighlight(json) {
  const escaped = escapeHtml(json);
  return escaped.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(\.\d+)?([eE][+-]?\d+)?)/g,
    match => {
      if (/^"/.test(match)) {
        return match.endsWith(":")
          ? `<span class="json-key">${match}</span>`
          : `<span class="json-string">${match}</span>`;
      }
      if (/true|false/.test(match)) return `<span class="json-bool">${match}</span>`;
      if (/null/.test(match))       return `<span class="json-null">${match}</span>`;
      return `<span class="json-number">${match}</span>`;
    }
  );
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
