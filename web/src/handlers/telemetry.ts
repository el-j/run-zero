import { dom } from "../dom";
import { setActiveTab } from "../view";

const MOBILE_QUERY = "(max-width: 900px)";

/** Maps a KPI drawer target to the id of the drawer panel to scroll to. */
const DRAWER_PANELS: Record<string, string> = {
  routing: "panel-routing-telemetry",
  cache: "panel-cache-analytics",
};

/**
 * Wires the telemetry drawer: open/close buttons, backdrop, Escape key, resize handling and
 * the clickable KPI cards that switch tabs or open the drawer at a panel.
 *
 * @returns A function that closes the drawer (reused by the header menu).
 */
export function initTelemetryDrawer(): () => void {
  const { btnHeaderMenu, headerMenuBackdrop } = dom;
  const workspace = document.querySelector<HTMLElement>(".main-workspace-full");
  const drawer = document.getElementById("telemetry-drawer");
  const backdrop = document.getElementById("drawer-backdrop");

  /** Opens the drawer and optionally scrolls to the panel for `section`. */
  const openDrawer = (section?: string) => {
    drawer?.classList.add("open");
    workspace?.classList.add("drawer-open");
    if (window.matchMedia(MOBILE_QUERY).matches) {
      backdrop?.classList.add("open");
    }
    if (section) {
      const el = document.getElementById(DRAWER_PANELS[section] || "");
      if (el) setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "start" }), 120);
    }
  };
  const closeDrawer = () => {
    drawer?.classList.remove("open");
    workspace?.classList.remove("drawer-open");
    backdrop?.classList.remove("open");
  };
  /** Collapses the mobile header menu without touching the drawer. */
  const closeHeaderMenu = () => {
    const header = document.querySelector<HTMLElement>(".app-header");
    const panel = header?.querySelector<HTMLElement>(".header-right");
    header?.classList.remove("menu-open");
    document.body.classList.remove("mobile-menu-open");
    headerMenuBackdrop?.classList.remove("open");
    btnHeaderMenu?.setAttribute("aria-expanded", "false");
    if (panel) panel.style.display = "";
  };
  document.getElementById("btn-open-drawer")?.addEventListener("click", () => {
    if (drawer?.classList.contains("open")) closeDrawer();
    else {
      closeHeaderMenu();
      openDrawer();
    }
  });
  document.getElementById("btn-close-drawer")?.addEventListener("click", closeDrawer);
  backdrop?.addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeDrawer();
  });
  window.addEventListener("resize", () => {
    if (!window.matchMedia(MOBILE_QUERY).matches) {
      backdrop?.classList.remove("open");
    }
  });
  document.querySelectorAll<HTMLElement>("[data-kpi-target]").forEach((card) => {
    card.addEventListener("click", () => {
      const target = card.dataset.kpiTarget!;
      if (target === "runners" || target === "queue") setActiveTab(target);
      else openDrawer(target);
    });
  });
  return closeDrawer;
}
