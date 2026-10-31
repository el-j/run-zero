import { dom } from "../dom";

/**
 * Wires the mobile header menu toggle, backdrop, outside-click, resize and Escape handling.
 * Opening the menu closes the telemetry drawer.
 *
 * @param closeDrawer - Closes the telemetry drawer.
 */
export function initHeaderMenu(closeDrawer: () => void): void {
  const { btnHeaderMenu, headerMenuBackdrop } = dom;
  if (!btnHeaderMenu) return;

  /** Opens or closes the menu; on mobile it also shows/hides the right-hand panel. */
  const setHeaderMenuOpen = (open: boolean) => {
    const header = document.querySelector<HTMLElement>(".app-header");
    const panel = header?.querySelector<HTMLElement>(".header-right");
    const isMobile = window.matchMedia("(max-width: 900px)").matches;
    header?.classList.toggle("menu-open", open);
    document.body.classList.toggle("mobile-menu-open", open);
    headerMenuBackdrop?.classList.toggle("open", open);
    if (panel && isMobile) {
      panel.style.display = open ? "flex" : "none";
    } else if (panel) {
      panel.style.removeProperty("display");
    }
    btnHeaderMenu.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) {
      closeDrawer();
    }
  };
  const closeHeaderMenu = () => {
    setHeaderMenuOpen(false);
  };
  btnHeaderMenu.onclick = (event) => {
    event.stopPropagation();
    const header = document.querySelector<HTMLElement>(".app-header");
    const opened = !(header?.classList.contains("menu-open") ?? false);
    setHeaderMenuOpen(opened);
  };
  headerMenuBackdrop?.addEventListener("click", closeHeaderMenu);
  document.addEventListener("click", (event) => {
    if (!window.matchMedia("(max-width: 900px)").matches) return;
    const target = event.target as Node | null;
    const header = document.querySelector<HTMLElement>(".app-header");
    if (!header || !target) return;
    if (header.contains(target)) return;
    closeHeaderMenu();
  });
  window.addEventListener("resize", () => {
    if (window.matchMedia("(min-width: 901px)").matches) {
      closeHeaderMenu();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeHeaderMenu();
  });
}
