const { invoke } = window.__TAURI__.core;

const list = document.getElementById("list");
const statusEl = document.getElementById("status");
const refreshBtn = document.getElementById("refresh");

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle("error", isError);
}

function formatTime(iso) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("fa-IR", { dateStyle: "short", timeStyle: "short" });
}

// Always textContent (never innerHTML): message text is untrusted.
function card(m) {
  const li = document.createElement("li");
  li.className = "msg";

  const head = document.createElement("div");
  head.className = "head";
  const sender = document.createElement("span");
  sender.className = "sender";
  sender.dir = "auto";
  sender.textContent = m.sender;
  const time = document.createElement("time");
  time.dateTime = m.date;
  time.textContent = formatTime(m.date);
  head.append(sender, time);

  const text = document.createElement("p");
  text.className = "text";
  text.dir = "auto"; // each message picks its own direction (fa/en mixed feeds)
  if (m.text) {
    text.textContent = m.text;
  } else {
    text.classList.add("media");
    text.textContent = m.has_media ? "📎 پیام رسانه‌ای" : "(بدون متن)";
  }

  li.append(head, text);
  return li;
}

async function load() {
  refreshBtn.disabled = true;
  setStatus("در حال دریافت…");
  try {
    const messages = await invoke("fetch_messages", { limit: 20 });
    list.replaceChildren(...messages.map(card));
    setStatus(
      messages.length
        ? `${messages.length} پیام آخر`
        : "پیامی وجود ندارد."
    );
  } catch (err) {
    setStatus(String(err), true);
  } finally {
    refreshBtn.disabled = false;
  }
}

refreshBtn.addEventListener("click", load);
load();
