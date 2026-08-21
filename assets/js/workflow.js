/* Scroll-driven workflow rail: steps light up as they pass the middle of
   the viewport and the progress line grows to the active step. */
(function () {
  var workflow = document.querySelector(".workflow");
  if (!workflow) return;

  var steps = [].slice.call(workflow.querySelectorAll(".wf-step"));
  var progress = workflow.querySelector(".wf-progress");

  if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
    steps.forEach(function (step) {
      step.classList.add("is-active");
    });
    if (progress) progress.style.height = "100%";
    return;
  }

  function centreOf(step) {
    var rect = step.querySelector(".wf-icon").getBoundingClientRect();
    return { top: rect.top, centre: rect.top + rect.height / 2, height: rect.height };
  }

  function update() {
    var middle = window.innerHeight / 2;
    var active = -1;
    var nearest = Infinity;

    steps.forEach(function (step, index) {
      var box = centreOf(step);
      var distance = Math.abs(box.centre - middle);
      if (box.top < middle && distance < nearest) {
        nearest = distance;
        active = index;
      }
    });

    steps.forEach(function (step, index) {
      step.classList.toggle("is-active", index <= active);
    });

    if (!progress) return;
    if (active < 0) {
      progress.style.height = "0px";
      return;
    }
    progress.style.height =
      Math.max(0, centreOf(steps[active]).centre - centreOf(steps[0]).centre) + "px";
  }

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      update();
      ticking = false;
    });
  }

  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);
  update();
})();
