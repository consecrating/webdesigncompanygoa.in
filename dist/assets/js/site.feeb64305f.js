"use strict";

document.documentElement.classList.remove("no-js");
document.documentElement.classList.add("js");

const menuButton = document.querySelector(".menu-button");
const navigation = document.querySelector("#primary-navigation");
const infoButton = document.querySelector(".info-button");
const infoPanel = document.querySelector("#header-information");
const infoClose = document.querySelector(".header-panel__close");

const closeMenu = () => {
  if (menuButton instanceof HTMLButtonElement && navigation instanceof HTMLElement) {
    menuButton.setAttribute("aria-expanded", "false");
    navigation.classList.remove("is-open");
  }
};

const closeInfoPanel = () => {
  if (infoButton instanceof HTMLButtonElement && infoPanel instanceof HTMLElement) {
    infoButton.setAttribute("aria-expanded", "false");
    infoPanel.hidden = true;
  }
};

if (menuButton instanceof HTMLButtonElement && navigation instanceof HTMLElement) {
  menuButton.addEventListener("click", () => {
    const isOpen = menuButton.getAttribute("aria-expanded") === "true";
    closeInfoPanel();
    menuButton.setAttribute("aria-expanded", String(!isOpen));
    navigation.classList.toggle("is-open", !isOpen);
  });

  navigation.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) closeMenu();
  });
}

if (infoButton instanceof HTMLButtonElement && infoPanel instanceof HTMLElement) {
  infoButton.addEventListener("click", () => {
    const isOpen = infoButton.getAttribute("aria-expanded") === "true";
    closeMenu();
    infoButton.setAttribute("aria-expanded", String(!isOpen));
    infoPanel.hidden = isOpen;
    if (!isOpen) infoClose?.focus();
  });

  infoClose?.addEventListener("click", () => {
    closeInfoPanel();
    infoButton.focus();
  });
}

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (menuButton?.getAttribute("aria-expanded") === "true") {
    closeMenu();
    menuButton.focus();
  }
  if (infoButton?.getAttribute("aria-expanded") === "true") {
    closeInfoPanel();
    infoButton.focus();
  }
});

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const revealItems = document.querySelectorAll("[data-reveal]");

if (reduceMotion || !("IntersectionObserver" in window) || revealItems.length === 0) {
  revealItems.forEach((item) => item.classList.add("is-visible"));
} else {
  try {
    const observer = new IntersectionObserver(
      (entries, currentObserver) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const element = entry.target;
          if (element instanceof HTMLElement) {
            element.style.setProperty("--reveal-order", String(element.dataset.revealOrder ?? "0"));
          }
          element.classList.add("is-visible");
          currentObserver.unobserve(element);
        });
      },
      { rootMargin: "0px 0px -8%", threshold: 0.12 },
    );

    revealItems.forEach((item) => observer.observe(item));
    document.documentElement.classList.add("reveal-ready");
  } catch {
    revealItems.forEach((item) => item.classList.add("is-visible"));
  }
}

const progressBar = document.querySelector(".scroll-progress span");
let progressFrame = 0;

const updateScrollProgress = () => {
  progressFrame = 0;
  if (!(progressBar instanceof HTMLElement)) return;
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? Math.min(window.scrollY / scrollable, 1) : 0;
  progressBar.style.transform = `scaleX(${progress})`;
};

if (progressBar instanceof HTMLElement && !reduceMotion) {
  window.addEventListener(
    "scroll",
    () => {
      if (progressFrame === 0) progressFrame = window.requestAnimationFrame(updateScrollProgress);
    },
    { passive: true },
  );
  updateScrollProgress();
}
