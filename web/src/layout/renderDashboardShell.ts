import ambientAndHeaderHtml from "./fragments/ambient-and-header.html?raw";
import dashboardMainHtml from "./fragments/dashboard-main.html?raw";
import dialogsAndToastHtml from "./fragments/dialogs-and-toast.html?raw";

export function renderDashboardShell() {
  if (document.body.dataset.shellRendered === "true") return;
  document.body.classList.add("theme-dark");
  document.body.innerHTML = `${ambientAndHeaderHtml}\n${dashboardMainHtml}\n${dialogsAndToastHtml}`;
  document.body.dataset.shellRendered = "true";
}
