const lightbox = document.querySelector("[data-lightbox]");
const lightboxImage = document.querySelector("[data-lightbox-image]");
const lightboxCaption = document.querySelector("[data-lightbox-caption]");
const closeButton = document.querySelector("[data-lightbox-close]");

const openLightbox = (src, alt, caption) => {
  if (!lightbox) return;
  lightboxImage.src = src;
  lightboxImage.alt = alt || "";
  lightboxCaption.textContent = caption || "";
  lightbox.removeAttribute("hidden");
  lightbox.classList.add("lightbox--open");
  document.body.style.overflow = "hidden";
};

const closeLightbox = () => {
  if (!lightbox) return;
  lightbox.classList.remove("lightbox--open");
  document.body.style.overflow = "";
  setTimeout(() => {
    if (!lightbox.classList.contains("lightbox--open")) {
      lightbox.setAttribute("hidden", "");
      lightboxImage.src = "";
      lightboxCaption.textContent = "";
    }
  }, 300);
};

const galleryItems = document.querySelectorAll(".gallery-item");

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.2 }
);

galleryItems.forEach((figure) => {
  observer.observe(figure);
  figure.addEventListener("click", () => {
    const img = figure.querySelector("img");
    const caption = figure.querySelector("figcaption");
    if (!img) return;
    openLightbox(img.src, img.alt, caption ? caption.textContent : "");
  });
});

closeButton?.addEventListener("click", closeLightbox);

lightbox?.addEventListener("click", (event) => {
  if (event.target === lightbox) {
    closeLightbox();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && lightbox?.classList.contains("lightbox--open")) {
    closeLightbox();
  }
});
