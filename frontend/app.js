const API = "http://localhost:5000/api";

const SUGGESTED_QUESTIONS = [
  "How does this project work overall?",
  "Show me the file structure",
  "What is the main entry point?",
  "How is data stored or fetched?",
  "What are the key dependencies?",
  "How is authentication handled?",
];

let repoLoaded = false;

// Configure marked with highlight.js
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true,
  gfm: true,
});

async function loadRepo() {
  const url = document.getElementById("repoUrl").value.trim();
  if (!url) return alert("Please enter a GitHub URL");

  showLoadingOverlay();
  setLoadBtn(true);

  try {
    const res = await fetch(`${API}/load`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || "Failed to load repo");

    document.getElementById("repoName").textContent = `${data.owner}/${data.repo}`;
    document.getElementById("filesCount").textContent = data.files_indexed;
    document.getElementById("repoSummary").textContent = data.summary;
    document.getElementById("repoInfo").classList.remove("hidden");

    const sqList = document.getElementById("sqList");
    sqList.innerHTML = "";
    SUGGESTED_QUESTIONS.forEach((q) => {
      const btn = document.createElement("button");
      btn.className = "sq-item";
      btn.textContent = q;
      btn.onclick = () => {
        document.getElementById("questionInput").value = q;
        askQuestion();
      };
      sqList.appendChild(btn);
    });
    document.getElementById("suggestedSection").classList.remove("hidden");
    document.getElementById("chatHeaderTitle").textContent =
      `${data.owner}/${data.repo}  ·  ${data.files_indexed} files indexed`;
    document.getElementById("emptyState").classList.add("hidden");
    document.getElementById("questionInput").disabled = false;
    document.getElementById("askBtn").disabled = false;
    repoLoaded = true;

    hideLoadingOverlay();
    addSystemMessage(`✓ Repository loaded — ${data.files_indexed} files indexed. Ask me anything.`);
  } catch (err) {
    hideLoadingOverlay();
    alert("Error: " + err.message);
  } finally {
    setLoadBtn(false);
  }
}

async function askQuestion() {
  const input = document.getElementById("questionInput");
  const question = input.value.trim();
  if (!question || !repoLoaded) return;

  input.value = "";
  autoResize(input);
  addUserMessage(question);
  const thinkingEl = addThinking();
  document.getElementById("askBtn").disabled = true;

  try {
    const res = await fetch(`${API}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    thinkingEl.remove();
    if (data.error) throw new Error(data.error);
    addAIMessage(data.answer, data.sources);
  } catch (err) {
    thinkingEl.remove();
    addAIMessage(`**Error:** ${err.message}`, []);
  } finally {
    document.getElementById("askBtn").disabled = false;
  }
}

function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    askQuestion();
  }
  autoResize(e.target);
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 120) + "px";
}

/* ── Message builders ── */

function addUserMessage(text) {
  const msgs = document.getElementById("messages");
  const el = document.createElement("div");
  el.className = "message";
  el.innerHTML = `
    <div class="msg-header">
      <div class="msg-avatar user">U</div>
      <span class="msg-role">You</span>
    </div>
    <div class="msg-body user-body">${escHtml(text)}</div>
  `;
  msgs.appendChild(el);
  scrollChat();
}

function addAIMessage(text, sources) {
  const msgs = document.getElementById("messages");
  const el = document.createElement("div");
  el.className = "message";

  // Render markdown beautifully
  const rendered = marked.parse(text);

  const sourcesHtml =
    sources && sources.length
      ? `<div class="sources-row">
           <span class="sources-label">Referenced files:</span>
           ${sources.map((s) => `<span class="source-chip">${escHtml(s)}</span>`).join("")}
         </div>`
      : "";

  el.innerHTML = `
    <div class="msg-header">
      <div class="msg-avatar ai">AI</div>
      <span class="msg-role">RepoMind</span>
    </div>
    <div class="msg-body markdown-body">${rendered}</div>
    ${sourcesHtml}
  `;

  msgs.appendChild(el);

  // Apply syntax highlighting to all code blocks
  el.querySelectorAll("pre code").forEach((block) => {
    hljs.highlightElement(block);
  });

  scrollChat();
}

function addSystemMessage(text) {
  const msgs = document.getElementById("messages");
  const el = document.createElement("div");
  el.className = "system-msg";
  el.textContent = text;
  msgs.appendChild(el);
  scrollChat();
}

function addThinking() {
  const msgs = document.getElementById("messages");
  const el = document.createElement("div");
  el.className = "message";
  el.innerHTML = `
    <div class="msg-header">
      <div class="msg-avatar ai">AI</div>
      <span class="msg-role">RepoMind</span>
    </div>
    <div class="thinking">
      <div class="think-dots">
        <div class="think-dot"></div>
        <div class="think-dot"></div>
        <div class="think-dot"></div>
      </div>
      Analyzing codebase...
    </div>
  `;
  msgs.appendChild(el);
  scrollChat();
  return el;
}

/* ── Overlay ── */
function showLoadingOverlay() {
  const overlay = document.createElement("div");
  overlay.id = "loadOverlay";
  overlay.className = "load-overlay";
  overlay.innerHTML = `
    <div class="load-card">
      <div style="font-size:36px">⬡</div>
      <h3>Indexing Repository</h3>
      <p>Fetching files, generating embeddings<br>and building vector index…</p>
      <div class="progress-bar-bg"><div class="progress-bar"></div></div>
      <p style="font-size:11px;color:var(--text-muted)">This takes 30–90 seconds for large repos</p>
    </div>
  `;
  document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
  const el = document.getElementById("loadOverlay");
  if (el) el.remove();
}

function setLoadBtn(loading) {
  const btn = document.getElementById("loadBtn");
  document.getElementById("loadBtnText").textContent = loading ? "Indexing…" : "Analyze Repository";
  document.getElementById("loadSpinner").classList.toggle("hidden", !loading);
  btn.disabled = loading;
}

function scrollChat() {
  const area = document.getElementById("chatArea");
  area.scrollTop = area.scrollHeight;
}

function escHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", () => {
  const ta = document.getElementById("questionInput");
  ta.addEventListener("input", () => autoResize(ta));
});