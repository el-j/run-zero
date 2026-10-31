import { client, type QueuedJob } from "../api/client";
import { dom } from "../dom";
import { compareValues, escapeHtml } from "../format";
import { state } from "../state";
import { showToast } from "../ui";

/**
 * Renders the repository priority list and table, and binds pause/reorder buttons and drag-and-drop.
 *
 * @param repos - All monitored repositories.
 * @param queuedJobs - Queued jobs, used for per-repo counts.
 * @param repoPriority - Priority order; falls back to `repos` when empty.
 * @param pausedRepos - Repositories that are paused.
 */
export function renderRepos(
  repos: string[],
  queuedJobs: QueuedJob[],
  repoPriority: string[],
  pausedRepos: Set<string>,
) {
  const { tabReposCount, reposTableBody, reposCountBadge, repoSearchInput, reposList } = dom;
  if (tabReposCount) tabReposCount.textContent = String(repos.length);
  if (reposCountBadge) reposCountBadge.textContent = `${repos.length} REPOSITORIES`;
  if (!reposList) return;

  const query = repoSearchInput ? repoSearchInput.value.trim().toLowerCase() : "";
  const ordered = repoPriority.length > 0 ? repoPriority : repos;
  const filtered = ordered.filter((r) => r.toLowerCase().includes(query));

  if (repos.length === 0) {
    reposList.innerHTML = '<div class="empty-substate">Discovering active repositories...</div>';
    if (reposTableBody)
      reposTableBody.innerHTML =
        '<tr><td colspan="5" class="empty-substate">Discovering active repositories...</td></tr>';
    return;
  }
  if (filtered.length === 0) {
    reposList.innerHTML = `<div class="empty-substate">No repositories matching "${escapeHtml(query)}"</div>`;
    if (reposTableBody)
      reposTableBody.innerHTML = `<tr><td colspan="5" class="empty-substate">No repositories matching "${escapeHtml(query)}"</td></tr>`;
    return;
  }

  const queuedByRepo: Record<string, number> = {};
  queuedJobs.forEach((j) => {
    if (j.repo) queuedByRepo[j.repo] = (queuedByRepo[j.repo] || 0) + 1;
  });

  // 1. Render Cards / List View
  reposList.innerHTML = filtered
    .map((repo, idx) => {
      const qCount = queuedByRepo[repo] || 0;
      const isPaused = pausedRepos.has(repo);

      let badge = '<span class="repo-queue-badge queue-idle">idle</span>';
      if (isPaused) {
        badge = '<span class="repo-queue-badge queue-paused">PAUSED</span>';
      } else if (qCount > 0) {
        badge = `<span class="repo-queue-badge queue-active">${qCount} queued</span>`;
      }

      return `
        <div class="repo-row ${isPaused ? "repo-row-paused" : ""}" draggable="true" data-repo="${escapeHtml(repo)}" data-index="${idx}">
          <div class="repo-prio-left">
            <span class="drag-handle" title="Drag to reorder priority">⠿</span>
            <span class="priority-rank-badge font-mono" title="Priority #${idx + 1}">#${idx + 1}</span>
            <div class="repo-main">
              <span class="repo-name font-mono">${escapeHtml(repo)}</span>
            </div>
          </div>
          <div class="repo-prio-right">
            ${badge}
            <button class="btn btn-xs ${isPaused ? "btn-resume-repo" : "btn-pause-repo"}" data-action="toggle-pause" data-repo="${escapeHtml(repo)}">
              ${isPaused ? "RESUME" : "PAUSE"}
            </button>
            <div class="prio-move-btns">
              <button class="btn btn-xs btn-move" data-action="move-up" data-repo="${escapeHtml(repo)}" ${idx === 0 ? "disabled" : ""}>▲</button>
              <button class="btn btn-xs btn-move" data-action="move-down" data-repo="${escapeHtml(repo)}" ${idx === filtered.length - 1 ? "disabled" : ""}>▼</button>
            </div>
          </div>
        </div>
      `;
    })
    .join("");

  // 2. Render Table View
  if (reposTableBody) {
    const sortedReposForTable = [...filtered].sort((aRepo, bRepo) => {
      const aQueued = queuedByRepo[aRepo] || 0;
      const bQueued = queuedByRepo[bRepo] || 0;
      const aPaused = pausedRepos.has(aRepo) ? "PAUSED" : "ACTIVE";
      const bPaused = pausedRepos.has(bRepo) ? "PAUSED" : "ACTIVE";
      const aRank = ordered.indexOf(aRepo) + 1;
      const bRank = ordered.indexOf(bRepo) + 1;
      const map: Record<typeof state.reposSort.key, [string | number, string | number]> = {
        rank: [aRank, bRank],
        repo: [aRepo, bRepo],
        status: [aPaused, bPaused],
        queued: [aQueued, bQueued],
      };
      const [av, bv] = map[state.reposSort.key];
      const diff = compareValues(av, bv);
      return state.reposSort.dir === "asc" ? diff : -diff;
    });

    reposTableBody.innerHTML = sortedReposForTable
      .map((repo) => {
        const qCount = queuedByRepo[repo] || 0;
        const isPaused = pausedRepos.has(repo);
        const rank = ordered.indexOf(repo) + 1;

        return `
          <tr>
            <td>
              <span class="priority-rank-badge font-mono">#${rank}</span>
            </td>
            <td>
              <span class="repo-name font-mono" style="font-weight: 700;">${escapeHtml(repo)}</span>
            </td>
            <td>
              <span class="badge ${isPaused ? "badge-danger" : "badge-live"} font-mono" style="font-size: 10px;">
                ${isPaused ? "PAUSED" : "ACTIVE"}
              </span>
            </td>
            <td>
              <span class="font-mono" style="color: ${qCount > 0 ? "var(--solar)" : "var(--text-muted)"};">
                ${qCount > 0 ? `${qCount} queued` : "idle"}
              </span>
            </td>
            <td style="text-align: right; white-space: nowrap;">
              <button class="btn btn-xs ${isPaused ? "btn-resume-repo" : "btn-pause-repo"}" data-action="toggle-pause" data-repo="${escapeHtml(repo)}">
                ${isPaused ? "RESUME" : "PAUSE"}
              </button>
              <button class="btn btn-xs btn-move" data-action="move-up" data-repo="${escapeHtml(repo)}" ${rank <= 1 ? "disabled" : ""}>▲</button>
              <button class="btn btn-xs btn-move" data-action="move-down" data-repo="${escapeHtml(repo)}" ${rank >= ordered.length ? "disabled" : ""}>▼</button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  // Attach priority handlers across both list and table
  document.querySelectorAll<HTMLButtonElement>("button[data-action]").forEach((btn) => {
    const action = btn.dataset.action;
    if (action !== "toggle-pause" && action !== "move-up" && action !== "move-down") return;

    btn.onclick = async (e) => {
      e.stopPropagation();
      const repo = btn.dataset.repo!;
      const newPrio = [...ordered];
      const newPaused = new Set(pausedRepos);

      if (action === "toggle-pause") {
        if (newPaused.has(repo)) newPaused.delete(repo);
        else newPaused.add(repo);
      } else if (action === "move-up") {
        const i = newPrio.indexOf(repo);
        if (i > 0) {
          const tmp = newPrio[i - 1];
          newPrio[i - 1] = newPrio[i];
          newPrio[i] = tmp;
        }
      } else {
        const i = newPrio.indexOf(repo);
        if (i >= 0 && i < newPrio.length - 1) {
          const tmp = newPrio[i + 1];
          newPrio[i + 1] = newPrio[i];
          newPrio[i] = tmp;
        }
      }

      state.currentRepoPriority = newPrio;
      state.currentPausedRepos = newPaused;
      renderRepos(state.currentRepos, state.currentQueuedJobs, state.currentRepoPriority, state.currentPausedRepos);
      try {
        await client.updateRepoPriority(newPrio, Array.from(newPaused));
        showToast("Priority updated");
      } catch (err) {
        showToast(`Failed updating priority: ${(err as Error).message}`, true);
      }
    };
  });

  // Drag and drop support
  reposList.querySelectorAll<HTMLElement>(".repo-row").forEach((row) => {
    row.ondragstart = () => {
      state.draggedRepo = row.dataset.repo || null;
      row.classList.add("repo-row-dragging");
    };
    row.ondragend = () => {
      state.draggedRepo = null;
      reposList
        .querySelectorAll(".repo-row")
        .forEach((r) => r.classList.remove("repo-row-dragging", "repo-row-drag-over"));
    };
    row.ondragover = (e) => {
      e.preventDefault();
      row.classList.add("repo-row-drag-over");
    };
    row.ondragleave = () => {
      row.classList.remove("repo-row-drag-over");
    };
    row.ondrop = async (e) => {
      e.preventDefault();
      row.classList.remove("repo-row-drag-over");
      const targetRepo = row.dataset.repo;
      if (!state.draggedRepo || state.draggedRepo === targetRepo) return;
      const newPrio = [...ordered];
      const fromIdx = newPrio.indexOf(state.draggedRepo);
      const toIdx = newPrio.indexOf(targetRepo!);
      if (fromIdx >= 0 && toIdx >= 0) {
        newPrio.splice(fromIdx, 1);
        newPrio.splice(toIdx, 0, state.draggedRepo);
        state.currentRepoPriority = newPrio;
        renderRepos(state.currentRepos, state.currentQueuedJobs, state.currentRepoPriority, state.currentPausedRepos);
        try {
          await client.updateRepoPriority(newPrio, Array.from(state.currentPausedRepos));
          showToast("Priority reordered");
        } catch (err) {
          showToast(`Error saving priority: ${(err as Error).message}`, true);
        }
      }
    };
  });
}
