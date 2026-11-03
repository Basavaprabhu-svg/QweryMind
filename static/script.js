const $ = (id) => document.getElementById(id);
let latestRows = [], latestColumns = [], toastTimer;

function toast(message) {
  const el = $("toast"); el.textContent = message; el.classList.add("show");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove("show"), 3200);
}
async function api(url, body) {
  const options = body === undefined ? {} : {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)
  };
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed.");
  return data;
}
function busy(button, text) { button.dataset.oldText = button.textContent; button.disabled = true; button.textContent = text; }
function ready(button) { button.disabled = false; button.textContent = button.dataset.oldText || button.textContent; }

document.querySelectorAll(".nav").forEach(button => button.addEventListener("click", () => showView(button.dataset.view)));
function showView(view) {
  document.querySelectorAll(".view").forEach(el => el.classList.add("hidden"));
  $(view + "-view").classList.remove("hidden");
  document.querySelectorAll(".nav").forEach(el => el.classList.toggle("active", el.dataset.view === view));
  const names = {query:["QUERY STUDIO","Ask your data anything."],history:["QUERY HISTORY","Your recent activity."],schema:["DATABASE EXPLORER","Understand your data." ]};
  $("crumb").textContent = names[view][0]; $("page-title").textContent = names[view][1];
  if (view === "history") loadHistory();
  if (view === "schema") loadSchema();
}
document.querySelectorAll(".example").forEach(btn => btn.addEventListener("click", () => {
  $("question").value = btn.textContent; $("question").focus();
}));
$("generate-btn").addEventListener("click", async () => {
  const question = $("question").value.trim();
  if (!question) return toast("Enter a question first.");
  const btn = $("generate-btn"); busy(btn, "Generating…"); $("status-text").textContent = "Working…";
  $("sql-message").className = "message"; $("sql-message").textContent = "Generating SQL and validating it…";
  try {
    const data = await api("/api/query", {question});
    $("sql-editor").value = data.sql;
    renderResults(data); $("status-text").textContent = "Ready";
    $("validation-badge").textContent = "VALIDATED"; $("validation-badge").className = "badge";
    $("sql-message").className = "message good"; $("sql-message").textContent = "SQL passed backend validation. Review it, then run it again if edited.";
    toast("SQL generated and executed successfully.");
  } catch (err) {
    $("status-text").textContent = "Check request";
    $("sql-message").className = "message bad"; $("sql-message").textContent = err.message;
    $("explanation").textContent = "The request could not be completed. Review the message above and try again.";
    toast(err.message);
  } finally { ready(btn); }
});
$("validate-btn").addEventListener("click", async () => {
  try {
    const data = await api("/api/validate", {sql: $("sql-editor").value});
    $("validation-badge").textContent = "VALID SELECT"; $("validation-badge").className = "badge";
    $("sql-message").className = "message good"; $("sql-message").textContent = data.message;
    toast("Query is valid and read-only.");
  } catch (err) {
    $("validation-badge").textContent = "BLOCKED"; $("validation-badge").className = "badge muted";
    $("sql-message").className = "message bad"; $("sql-message").textContent = err.message;
    toast(err.message);
  }
});
$("run-btn").addEventListener("click", async () => {
  const btn = $("run-btn"); busy(btn, "Running…");
  try {
    const data = await api("/api/execute", {question: $("question").value.trim(), sql: $("sql-editor").value});
    renderResults(data); $("validation-badge").textContent = "VALIDATED"; $("validation-badge").className = "badge";
    $("sql-message").className = "message good"; $("sql-message").textContent = "Query executed successfully in read-only mode.";
    toast("Query completed.");
  } catch (err) {
    $("sql-message").className = "message bad"; $("sql-message").textContent = err.message; toast(err.message);
  } finally { ready(btn); }
});
function renderResults(data) {
  latestRows = data.rows || []; latestColumns = data.columns || [];
  $("row-count").textContent = `${data.row_count ?? latestRows.length} rows`;
  $("result-subtitle").textContent = latestRows.length ? "Showing returned records (up to 500 rows)." : "Query completed with no matching records.";
  $("explanation").textContent = data.explanation || "No explanation available.";
  $("export-btn").disabled = latestRows.length === 0;
  if (!latestColumns.length) {
    $("results").innerHTML = '<div class="empty"><b>No tabular results</b><p>The query returned no columns.</p></div>'; return;
  }
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const head = latestColumns.map(c => `<th>${esc(c)}</th>`).join("");
  const body = latestRows.map(row => `<tr>${latestColumns.map(c => `<td>${esc(row[c])}</td>`).join("")}</tr>`).join("");
  $("results").innerHTML = `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body || `<tr><td colspan="${latestColumns.length}">No matching records.</td></tr>`}</tbody></table></div>`;
}
$("export-btn").addEventListener("click", () => {
  const quote = v => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const csv = [latestColumns.map(quote).join(","), ...latestRows.map(row => latestColumns.map(c => quote(row[c])).join(","))].join("\r\n");
  const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([csv], {type:"text/csv;charset=utf-8;"}));
  link.download = "querymind-results.csv"; link.click(); URL.revokeObjectURL(link.href);
});
async function loadSchema() {
  try {
    const tables = await api("/api/schema");
    $("schema-list").innerHTML = tables.map(t => `<div class="card schema-card"><h3>▦ ${t.table}<span>${t.columns.length} columns</span></h3>${t.columns.map(c => `<div class="column"><span>${c.name}${c.primary_key ? " 🔑" : ""}</span><small>${c.type || "TEXT"}</small></div>`).join("")}</div>`).join("");
  } catch (err) { toast(err.message); }
}
async function loadHistory() {
  try {
    const items = await api("/api/history");
    $("history-list").innerHTML = items.length ? items.map(item =>
      `<div class="history-item"><div><b>${escapeHtml(item.question)}</b><small>${escapeHtml(item.created_at)} · ${item.row_count} rows · ${escapeHtml(item.status)}</small></div><button data-sql="${encodeURIComponent(item.sql_text || "")}" data-question="${encodeURIComponent(item.question)}">Load SQL</button></div>`
    ).join("") : '<div class="list-empty">No queries have been run yet.</div>';
    $("history-list").querySelectorAll("button[data-sql]").forEach(btn => btn.addEventListener("click", () => {
      $("question").value = decodeURIComponent(btn.dataset.question);
      $("sql-editor").value = decodeURIComponent(btn.dataset.sql);
      showView("query");
    }));
  } catch (err) { toast(err.message); }
}
function escapeHtml(value) { return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
$("refresh-history").addEventListener("click", loadHistory);
$("mic-btn").addEventListener("click", () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return toast("Voice input is not supported in this browser. Try Chrome or Edge.");
  const recognition = new SpeechRecognition();
  recognition.lang = "en-IN"; recognition.interimResults = false; recognition.maxAlternatives = 1;
  const btn = $("mic-btn"); busy(btn, "Listening…");
  recognition.onresult = event => { $("question").value = event.results[0][0].transcript; toast("Voice captured. Review the question, then generate SQL."); };
  recognition.onerror = event => toast("Voice input issue: " + event.error);
  recognition.onend = () => ready(btn);
  recognition.start();
});
