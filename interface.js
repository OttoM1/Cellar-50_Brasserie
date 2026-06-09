const Cellar50 = (() => {

  const toastStack = () => document.getElementById("toast-stack");

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function showAlert(message) {
    const overlay = document.getElementById("custom-alert-overlay"),
          msgBox = document.getElementById("custom-alert-msg");
    if (!overlay || !msgBox) return;

    msgBox.textContent = message;
    overlay.style.display = "flex";
    requestAnimationFrame(() => overlay.classList.add("active"));
  }

  function closeAlert() {
    const overlay = document.getElementById("custom-alert-overlay");
    if (!overlay) return;
    overlay.classList.remove("active");
    setTimeout(() => { overlay.style.display = "none"; }, 300);
  }


  function toast(message, type = "success", duration = 2800) {
    const stack = toastStack();
    if (!stack) return;

    const el = document.createElement("div");
    el.className = `toast toast--${type}`;
    el.textContent = message;
    stack.appendChild(el);

    setTimeout(() => {
      el.classList.add("toast--out");
      setTimeout(() => el.remove(), 300);
    }, duration);
  }

  async function api(url, options = {}) {
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json", ...options.headers },
      ...options,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.message || "Request failed");
    return data;
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      toast("Copied to clipboard");
      return true;
    } catch {
      showAlert("Could not copy — select the text manually.");
      return false;
    }
  }

  function debounce(fn, ms = 200) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }

  function initGlobal() {
    window.alert = showAlert;
    scrollToTop();
  }

  document.addEventListener("DOMContentLoaded", initGlobal);

  return {
    showAlert, closeAlert, toast, api,
    copyText, debounce, scrollToTop
  };
})();
