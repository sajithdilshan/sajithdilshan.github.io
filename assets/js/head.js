/* Resolves the theme before the first paint, so a dark visitor never
   sees a flash of the light palette. Loaded synchronously in <head>. */
(function () {
  try {
    var saved = localStorage.getItem("theme");
    document.documentElement.dataset.theme =
      saved || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  } catch (e) {
    document.documentElement.dataset.theme = "light";
  }
})();
