import ambientAndHeaderHtml from "./fragments/ambient-and-header.html?raw";
import dashboardMainHtml from "./fragments/dashboard-main.html?raw";
import dialogsAndToastHtml from "./fragments/dialogs-and-toast.html?raw";

export function renderDashboardShell() {
  if (document.body.dataset.shellRendered === "true") return;
  document.body.classList.add("theme-dark");
  const appIconUrl = `${import.meta.env.BASE_URL}icon.svg`;
  const shellHeaderHtml = ambientAndHeaderHtml.replaceAll("__APP_ICON_URL__", appIconUrl);
  document.body.innerHTML = `${shellHeaderHtml}\n${dashboardMainHtml}\n${dialogsAndToastHtml}`;
  document.body.dataset.shellRendered = "true";
}
