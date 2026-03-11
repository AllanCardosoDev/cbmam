(function () {
  const root = document.documentElement;
  const body = document.body;

  // -------- Menu mobile --------
  const toggle = document.querySelector(".menuToggle");
  const menu = document.querySelector("#menu");

  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const open = menu.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  // -------- Dropdowns (desktop e mobile) --------
  document.querySelectorAll(".nav__item--hasSub").forEach((item) => {
    const btn = item.querySelector(".nav__linkBtn");
    const sub = item.querySelector(".subnav");
    if (!btn || !sub) return;

    btn.addEventListener("click", () => {
      const isOpen = item.classList.toggle("nav__item--open");
      btn.setAttribute("aria-expanded", String(isOpen));
    });

    // Fecha ao clicar fora (só em telas maiores)
    document.addEventListener("click", (ev) => {
      const isMobile = window.matchMedia("(max-width: 720px)").matches;
      if (isMobile) return;
      if (!item.contains(ev.target)) {
        item.classList.remove("nav__item--open");
        btn.setAttribute("aria-expanded", "false");
      }
    });
  });

  // -------- Acessibilidade: contraste + fonte --------
  const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

  // Estado inicial (persistência)
  const savedContrast = localStorage.getItem("contrast") === "1";
  if (savedContrast) body.classList.add("is-contrast");

  const savedScale = parseFloat(localStorage.getItem("fontScale") || "1");
  root.style.setProperty("--fontScale", String(clamp(savedScale, 0.85, 1.25)));

  function setContrast(on) {
    body.classList.toggle("is-contrast", on);
    localStorage.setItem("contrast", on ? "1" : "0");
    const btn = document.querySelector('[data-action="toggle-contrast"]');
    if (btn) btn.setAttribute("aria-pressed", String(on));
  }

  function setScale(scale) {
    const s = clamp(scale, 0.85, 1.25);
    root.style.setProperty("--fontScale", String(s));
    localStorage.setItem("fontScale", String(s));
  }

  document.querySelectorAll("[data-action]").forEach((el) => {
    el.addEventListener("click", () => {
      const action = el.getAttribute("data-action");
      const currentScale = parseFloat(getComputedStyle(root).getPropertyValue("--fontScale")) || 1;

      if (action === "toggle-contrast") setContrast(!body.classList.contains("is-contrast"));
      if (action === "font-plus") setScale(currentScale + 0.05);
      if (action === "font-minus") setScale(currentScale - 0.05);
      if (action === "font-reset") setScale(1);
    });
  });

  // -------- Carrossel (scroll-snap com botões) --------
  const wrap = document.querySelector('[data-carousel="wrap"]');
  const track = document.querySelector('[data-carousel="track"]');

  function scrollByCard(dir) {
    if (!track) return;
    const card = track.querySelector(".cardNews");
    const step = card ? (card.getBoundingClientRect().width + 12) : 280;
    track.scrollBy({ left: dir * step, behavior: "smooth" });
  }

  document.querySelectorAll("[data-carousel]").forEach((btn) => {
    const kind = btn.getAttribute("data-carousel");
    if (kind === "prev") btn.addEventListener("click", () => scrollByCard(-1));
    if (kind === "next") btn.addEventListener("click", () => scrollByCard(1));
  });

  // Autoplay opcional (desligado se usuário preferir menos movimento)
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (wrap && track && !reduceMotion) {
    let timer = setInterval(() => scrollByCard(1), 5000);

    // Pausa ao interagir
    ["pointerenter", "focusin"].forEach((evt) => wrap.addEventListener(evt, () => clearInterval(timer)));
  }
})();
