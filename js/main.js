(function () {
  "use strict";

  var root = document.documentElement;

  /* ---------- Footer year ---------- */
  var yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = String(new Date().getFullYear());
  }

  /* ---------- Theme toggle ---------- */
  var toggle = document.getElementById("theme-toggle");

  function applyToggleLabel(theme) {
    if (!toggle) return;
    var goingTo = theme === "dark" ? "light" : "dark";
    toggle.setAttribute("aria-label", "Switch to " + goingTo + " mode");
    toggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
  }

  applyToggleLabel(root.getAttribute("data-theme") || "light");

  if (toggle) {
    toggle.addEventListener("click", function () {
      var current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
      var next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try {
        localStorage.setItem("theme", next);
      } catch (e) {}
      applyToggleLabel(next);
    });
  }

  /* ---------- Academic / Personal view tabs ---------- */
  var tabs = [
    { tab: document.getElementById("tab-academic"), panel: document.getElementById("view-academic"), key: "academic" },
    { tab: document.getElementById("tab-personal"), panel: document.getElementById("view-personal"), key: "personal" }
  ];

  function selectView(key, updateHash) {
    tabs.forEach(function (t) {
      if (!t.tab || !t.panel) return;
      var active = t.key === key;
      t.tab.setAttribute("aria-selected", active ? "true" : "false");
      t.tab.tabIndex = active ? 0 : -1;
      t.panel.hidden = !active;
    });
    if (updateHash) {
      try {
        history.replaceState(null, "", "#" + key);
      } catch (e) {}
    }
  }

  tabs.forEach(function (t, i) {
    if (!t.tab) return;
    t.tab.addEventListener("click", function () {
      selectView(t.key, true);
    });
    // Arrow-key navigation between tabs
    t.tab.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault();
      var dir = e.key === "ArrowRight" ? 1 : -1;
      var next = tabs[(i + dir + tabs.length) % tabs.length];
      if (next && next.tab) {
        selectView(next.key, true);
        next.tab.focus();
      }
    });
  });

  // Honor an initial hash (#personal / #academic) on load
  var initial = (window.location.hash || "").replace("#", "");
  if (initial === "personal" || initial === "academic") {
    selectView(initial, false);
  }
})();
