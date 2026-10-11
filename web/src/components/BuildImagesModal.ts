import type { ImagesStatusResponse, ImageBuildProgress, InfrastructureImageStatus } from "../api/client";

export class BuildImagesModal {
  private dialog: HTMLDialogElement | null = null;
  private statusGrid: HTMLElement | null = null;
  private progressPanel: HTMLElement | null = null;
  private stepText: HTMLElement | null = null;
  private pctText: HTMLElement | null = null;
  private progressBar: HTMLElement | null = null;
  private buildLog: HTMLElement | null = null;
  private headerBadge: HTMLElement | null = null;
  private headerIcon: HTMLElement | null = null;
  private isBuilding = false;
  private pollTimer: number | null = null;

  constructor() {
    this.initElements();
    this.bindEvents();
    this.refresh();
  }

  private initElements(): void {
    this.dialog = document.getElementById("images-modal") as HTMLDialogElement | null;
    this.statusGrid = document.getElementById("images-status-grid");
    this.progressPanel = document.getElementById("images-build-progress-panel");
    this.stepText = document.getElementById("images-build-step-text");
    this.pctText = document.getElementById("images-build-pct");
    this.progressBar = document.getElementById("images-build-progress-bar");
    this.buildLog = document.getElementById("images-build-log");
    this.headerBadge = document.getElementById("badge-images-status");
    this.headerIcon = document.getElementById("badge-images-icon");
  }

  private bindEvents(): void {
    const btnOpen = document.getElementById("btn-open-images");
    if (btnOpen) {
      btnOpen.addEventListener("click", () => this.open());
    }

    const btnClose = document.getElementById("images-modal-close");
    if (btnClose) {
      btnClose.addEventListener("click", () => this.close());
    }

    const btnDone = document.getElementById("images-modal-done");
    if (btnDone) {
      btnDone.addEventListener("click", () => this.close());
    }

    const btnAll = document.getElementById("btn-build-all-images");
    if (btnAll) {
      btnAll.addEventListener("click", () => this.triggerBuild("all", "all"));
    }

    const btnVm = document.getElementById("btn-build-vm-images");
    if (btnVm) {
      btnVm.addEventListener("click", () => this.triggerBuild("vm", "all"));
    }

    const btnContainer = document.getElementById("btn-build-container-images");
    if (btnContainer) {
      btnContainer.addEventListener("click", () => this.triggerBuild("container", "all"));
    }

    const btnCancel = document.getElementById("btn-cancel-image-build");
    if (btnCancel) {
      btnCancel.addEventListener("click", () => this.cancelBuild());
    }
  }

  public open(): void {
    if (this.dialog && !this.dialog.open) {
      this.dialog.showModal();
      this.refresh();
    }
  }

  public close(): void {
    if (this.dialog && this.dialog.open) {
      this.dialog.close();
    }
  }

  public async refresh(): Promise<void> {
    try {
      const res = await fetch("/api/images");
      if (!res.ok) return;
      const data: ImagesStatusResponse = await res.json();
      this.renderStatus(data);

      if (data.active_build && data.active_build.status === "building") {
        this.updateBuildProgress(data.active_build);
        this.startPolling();
      } else if (this.isBuilding) {
        this.stopPolling();
        if (data.active_build) {
          this.updateBuildProgress(data.active_build);
        }
      }
    } catch (err) {
      console.warn("Failed fetching image status:", err);
    }
  }

  public handleProgressEvent(p: ImageBuildProgress): void {
    this.updateBuildProgress(p);
    if (p.status === "building") {
      this.startPolling();
    } else {
      this.stopPolling();
      this.refresh();
    }
  }

  private renderStatus(data: ImagesStatusResponse): void {
    if (!this.statusGrid) return;

    const allImages = [...(data.vm_images || []), ...(data.container_images || [])];
    const readyCount = allImages.filter(img => img.status === "ready").length;
    const totalCount = allImages.length;

    // Update Header Badge
    if (this.headerBadge) {
      this.headerBadge.textContent = `${readyCount}/${totalCount}`;
      if (data.all_ready) {
        this.headerBadge.className = "badge badge-success font-mono";
        this.headerBadge.style.color = "var(--accent-emerald, #10b981)";
        if (this.headerIcon) this.headerIcon.textContent = "✓";
      } else {
        this.headerBadge.className = "badge badge-warning font-mono";
        this.headerBadge.style.color = "var(--solar, #f59e0b)";
        if (this.headerIcon) this.headerIcon.textContent = "⚡";
      }
    }

    // Render Grid Cards
    let html = "";

    // VMs Section
    for (const vm of data.vm_images || []) {
      html += this.renderImageCard(vm);
    }

    // Containers Section
    for (const c of data.container_images || []) {
      html += this.renderImageCard(c);
    }

    this.statusGrid.innerHTML = html;
  }

  private renderImageCard(img: InfrastructureImageStatus): string {
    const isVm = img.kind === "orbstack-vm";
    const statusColor = img.status === "ready"
      ? "var(--accent-emerald, #10b981)"
      : img.status === "stale"
      ? "var(--solar, #f59e0b)"
      : "var(--crimson, #ef4444)";

    const statusBadgeClass = img.status === "ready"
      ? "tag-emerald"
      : img.status === "stale"
      ? "tag-amber"
      : "tag-crimson";

    const subtitle = isVm
      ? `OrbStack Linux VM • ${img.version ? `Runner v${img.version}` : "Ubuntu Noble base"}`
      : `Docker Runner • ${img.size_human ? `Size: ${img.size_human}` : "Static runner image"}`;

    return `
      <div class="glass-panel" style="padding: 12px 14px; border-left: 3px solid ${statusColor};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            <div style="display: flex; align-items: center; gap: 6px;">
              <span class="font-mono" style="font-weight: 600; font-size: 13px;">${img.name}</span>
              <span class="tech-chip ${isVm ? "purple" : "cyan"} font-mono" style="font-size: 10px;">${img.arch.toUpperCase()}</span>
            </div>
            <div class="font-mono text-muted" style="font-size: 11px; margin-top: 4px;">${subtitle}</div>
          </div>
          <span class="tech-chip ${statusBadgeClass} font-mono" style="font-size: 11px; text-transform: uppercase;">
            ${img.status}
          </span>
        </div>
      </div>
    `;
  }

  private async triggerBuild(target: "all" | "vm" | "container", arch: "all" | "arm64" | "amd64"): Promise<void> {
    try {
      this.isBuilding = true;
      if (this.progressPanel) this.progressPanel.classList.remove("hidden");
      if (this.buildLog) this.buildLog.textContent = "[BUILD] Initializing build request...\n";

      const res = await fetch("/api/actions/build-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target, arch }),
      });

      if (!res.ok) {
        const err = await res.json();
        alert(`Build failed to start: ${err.error || res.statusText}`);
        this.isBuilding = false;
        return;
      }

      const p: ImageBuildProgress = await res.json();
      this.updateBuildProgress(p);
      this.startPolling();
    } catch (err) {
      alert(`Network error triggering build: ${err}`);
      this.isBuilding = false;
    }
  }

  private async cancelBuild(): Promise<void> {
    try {
      await fetch("/api/actions/build-image/cancel", { method: "POST" });
      if (this.stepText) this.stepText.textContent = "Cancelling build...";
    } catch (err) {
      console.warn("Cancel build error:", err);
    }
  }

  private updateBuildProgress(p: ImageBuildProgress): void {
    if (!this.progressPanel) return;

    this.progressPanel.classList.remove("hidden");
    if (this.stepText) this.stepText.textContent = p.current_step || "Building...";
    if (this.pctText) this.pctText.textContent = `${p.progress_pct}%`;
    if (this.progressBar) this.progressBar.style.width = `${p.progress_pct}%`;

    if (this.buildLog && p.log_lines && p.log_lines.length > 0) {
      this.buildLog.textContent = p.log_lines.join("\n");
      this.buildLog.scrollTop = this.buildLog.scrollHeight;
    }

    if (p.status === "building") {
      this.isBuilding = true;
    } else {
      this.isBuilding = false;
      if (p.status === "success") {
        if (this.progressBar) this.progressBar.style.background = "var(--accent-emerald, #10b981)";
      } else if (p.status === "failed") {
        if (this.progressBar) this.progressBar.style.background = "var(--crimson, #ef4444)";
      }
    }
  }

  private startPolling(): void {
    if (this.pollTimer) return;
    this.pollTimer = window.setInterval(async () => {
      try {
        const res = await fetch("/api/images/build/active");
        if (res.ok) {
          const p: ImageBuildProgress = await res.json();
          this.updateBuildProgress(p);
          if (p.status !== "building") {
            this.stopPolling();
            this.refresh();
          }
        }
      } catch {
        // Poll failed
      }
    }, 1500);
  }

  private stopPolling(): void {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }
}
