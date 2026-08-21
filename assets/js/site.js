/* Theme switch, footer year, and the obfuscated email link.
   Loaded on every page with `defer`. */
(function () {
  var root = document.documentElement;
  var button = document.querySelector(".theme");

  function label() {
    if (!button) return;
    var next = root.dataset.theme === "dark" ? "light" : "dark";
    button.setAttribute("aria-label", "Switch to " + next + " theme");
    button.setAttribute("title", "Switch to " + next + " theme");
  }

  label();

  if (button) {
    button.addEventListener("click", function () {
      root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
      try {
        localStorage.setItem("theme", root.dataset.theme);
      } catch (e) {}
      label();
    });
  }

  // keep following the system until the visitor picks a side
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (event) {
    try {
      if (localStorage.getItem("theme")) return;
    } catch (e) {}
    root.dataset.theme = event.matches ? "dark" : "light";
    label();
  });

  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  var email = document.querySelector(".email-link");
  if (email) email.href = "mailto:" + email.dataset.email + "@" + email.dataset.domain;
})();
