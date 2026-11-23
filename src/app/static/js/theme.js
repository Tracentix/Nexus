// Dark/light theme toggle, persisted per browser.
(function () {
  function apply(theme) {
    document.documentElement.classList.toggle("dark", theme === "dark");
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.textContent = theme === "dark" ? "Light mode" : "Dark mode";
      btn.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    }
  }

  window.toggleTheme = function () {
    var next = document.documentElement.classList.contains("dark")
      ? "light" : "dark";
    localStorage.setItem("nexus-theme", next);
    apply(next);
  };

  document.addEventListener("DOMContentLoaded", function () {
    var saved = localStorage.getItem("nexus-theme");
    if (!saved) {
      saved = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark" : "light";
    }
    apply(saved);
  });
})();
