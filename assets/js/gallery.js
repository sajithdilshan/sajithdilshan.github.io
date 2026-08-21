/* Lightbox + reveal-on-scroll, shared by the city galleries and the
   figures inside blog posts. Loaded with `defer` only where needed.

   Gallery figures carry data-full (and data-type="video" for clips);
   post figures are plain <figure class="post-figure"><img>. */
(function () {
  var box = document.querySelector("[data-lightbox]");
  var boxImage = document.querySelector("[data-lightbox-image]");
  var boxVideo = document.querySelector("[data-lightbox-video]");
  var boxCaption = document.querySelector("[data-lightbox-caption]");
  var closeButton = document.querySelector("[data-lightbox-close]");

  var figures = [].slice.call(document.querySelectorAll(".gallery-item, .post-figure"));
  if (!figures.length) return;

  // one flat list of everything the lightbox can step through
  var slides = figures.map(function (figure) {
    var image = figure.querySelector("img");
    var caption = figure.querySelector("figcaption");
    return {
      figure: figure,
      src: figure.dataset.full || (image && image.src) || "",
      alt: (image && image.alt) || "",
      caption: caption ? caption.textContent.trim() : "",
      video: figure.dataset.type === "video"
    };
  });

  var at = -1;

  function show(index) {
    if (!box) return;
    at = (index + slides.length) % slides.length;
    var slide = slides[at];

    if (slide.video && boxVideo) {
      boxVideo.src = slide.src;
      boxVideo.hidden = false;
      boxImage.hidden = true;
      boxImage.src = "";
      boxVideo.play().catch(function () {});
    } else {
      boxImage.src = slide.src;
      boxImage.alt = slide.alt;
      boxImage.hidden = false;
      if (boxVideo) {
        boxVideo.pause();
        boxVideo.hidden = true;
        boxVideo.src = "";
      }
    }

    if (boxCaption) {
      boxCaption.textContent =
        slide.caption || (slides.length > 1 ? at + 1 + " / " + slides.length : "");
    }
  }

  function open(index) {
    box.removeAttribute("hidden");
    show(index);
    box.classList.add("lightbox--open");
    document.body.style.overflow = "hidden";
    if (closeButton) closeButton.focus();
  }

  function close() {
    box.classList.remove("lightbox--open");
    document.body.style.overflow = "";
    if (boxVideo) boxVideo.pause();
    var previous = at > -1 ? slides[at].figure : null;
    window.setTimeout(function () {
      if (box.classList.contains("lightbox--open")) return;
      box.setAttribute("hidden", "");
      boxImage.src = "";
      if (boxVideo) boxVideo.src = "";
      if (boxCaption) boxCaption.textContent = "";
    }, 300);
    if (previous) previous.focus({ preventScroll: true });
  }

  slides.forEach(function (slide, index) {
    var target = slide.figure.classList.contains("post-figure")
      ? slide.figure.querySelector("img")
      : slide.figure;
    if (!target) return;
    slide.figure.tabIndex = 0;
    slide.figure.setAttribute("role", "button");
    target.addEventListener("click", function () {
      if (box) open(index);
    });
    slide.figure.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        if (box) open(index);
      }
    });
  });

  if (box) {
    if (closeButton) closeButton.addEventListener("click", close);
    box.addEventListener("click", function (event) {
      if (event.target === box) close();
    });
    document.addEventListener("keydown", function (event) {
      if (!box.classList.contains("lightbox--open")) return;
      if (event.key === "Escape") close();
      if (event.key === "ArrowLeft") show(at - 1);
      if (event.key === "ArrowRight") show(at + 1);
    });
  }

  // fade each tile in as it arrives, then warm the full-size file
  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        var full = entry.target.dataset.full;
        if (full && entry.target.dataset.type !== "video") new Image().src = full;
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.15, rootMargin: "120px" }
  );

  figures.forEach(function (figure) {
    if (figure.classList.contains("gallery-item")) observer.observe(figure);
  });
})();
