(function () {
  "use strict";

  var root = document.documentElement;

  /* ---------- Footer year ---------- */
  var yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = String(new Date().getFullYear());
  }

  /* ---------- Theme toggle ---------- */
  var themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
      var next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try {
        localStorage.setItem("theme", next);
      } catch (e) {}
    });
  }

  /* ---------- Language toggle (button label swaps via CSS) ---------- */
  var langToggle = document.getElementById("lang-toggle");
  if (langToggle) {
    langToggle.addEventListener("click", function () {
      var current = root.getAttribute("data-lang") === "es" ? "es" : "en";
      var next = current === "es" ? "en" : "es";
      root.setAttribute("data-lang", next);
      root.setAttribute("lang", next);
      try {
        localStorage.setItem("lang", next);
      } catch (e) {}
    });
  }

  /* ---------- Academic / Personal view tabs + section sub-nav ---------- */
  var tabs = [
    {
      tab: document.getElementById("tab-academic"),
      panel: document.getElementById("view-academic"),
      subnav: document.getElementById("subnav-academic"),
      key: "academic"
    },
    {
      tab: document.getElementById("tab-personal"),
      panel: document.getElementById("view-personal"),
      subnav: document.getElementById("subnav-personal"),
      key: "personal"
    }
  ];

  function selectView(key, updateHash) {
    tabs.forEach(function (t) {
      if (!t.tab || !t.panel) return;
      var active = t.key === key;
      t.tab.setAttribute("aria-selected", active ? "true" : "false");
      t.tab.tabIndex = active ? 0 : -1;
      t.panel.hidden = !active;
      if (t.subnav) t.subnav.hidden = !active;
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

  // Honor an initial hash. Accept #academic / #personal, or a section id that
  // lives inside one of the views (so a sub-nav deep link selects the right tab).
  if (tabs[0].tab) {
    var hash = (window.location.hash || "").replace("#", "");
    if (hash === "personal" || hash === "academic") {
      selectView(hash, false);
    } else if (hash) {
      var target = document.getElementById(hash);
      if (target) {
        var inPersonal = document.getElementById("view-personal");
        if (inPersonal && inPersonal.contains(target)) {
          selectView("personal", false);
        }
      }
    }
  }
})();
