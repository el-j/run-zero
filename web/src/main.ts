import "./styles/theme.css";
import { client, type FleetState } from "./api/client";
import { HeaderComponent } from "./components/Header";
import { CapacityMeterComponent } from "./components/CapacityMeter";
import { QueueViewComponent } from "./components/QueueView";
import { PriorityManagerComponent } from "./components/PriorityManager";
import { RunnerFleetComponent } from "./components/RunnerFleet";
import { SettingsPanelComponent } from "./components/SettingsPanel";
import { CachePanelComponent } from "./components/CachePanel";

type ActiveTab = "fleet" | "settings" | "cache";

class App {
  private activeTab: ActiveTab = "fleet";
  private state?: FleetState;

  private header: HeaderComponent;
  private capacity: CapacityMeterComponent;
  private queue: QueueViewComponent;
  private priority: PriorityManagerComponent;
  private fleet: RunnerFleetComponent;
  private settings: SettingsPanelComponent;
  private cache: CachePanelComponent;

  constructor() {
    const headerEl = document.getElementById("header-root")!;
    const capacityEl = document.getElementById("capacity-root")!;
    const queueEl = document.getElementById("queue-root")!;
    const priorityEl = document.getElementById("priority-root")!;
    const fleetEl = document.getElementById("fleet-root")!;
    const settingsEl = document.getElementById("settings-root")!;
    const cacheEl = document.getElementById("cache-root")!;

    this.header = new HeaderComponent(headerEl);
    this.capacity = new CapacityMeterComponent(capacityEl);
    this.queue = new QueueViewComponent(queueEl);
    this.priority = new PriorityManagerComponent(priorityEl, () => this.refresh());
    this.fleet = new RunnerFleetComponent(fleetEl);
    this.settings = new SettingsPanelComponent(settingsEl);
    this.cache = new CachePanelComponent(cacheEl);

    this.bindNavigation();
  }

  private bindNavigation() {
    document.addEventListener("click", (e) => {
      const target = e.target as HTMLElement;
      if (target.id === "nav-fleet") {
        this.setTab("fleet");
      } else if (target.id === "nav-settings") {
        this.setTab("settings");
      } else if (target.id === "nav-cache") {
        this.setTab("cache");
      }
    });
  }

  private setTab(tab: ActiveTab) {
    this.activeTab = tab;
    const fleetSection = document.getElementById("tab-fleet-section")!;
    const settingsSection = document.getElementById("settings-root")!;
    const cacheSection = document.getElementById("cache-root")!;

    fleetSection.style.display = tab === "fleet" ? "block" : "none";
    settingsSection.style.display = tab === "settings" ? "block" : "none";
    cacheSection.style.display = tab === "cache" ? "block" : "none";

    if (tab === "settings") {
      this.settings.load();
    } else if (tab === "cache") {
      this.cache.load();
    }

    this.updateNavButtons();
  }

  private updateNavButtons() {
    const navFleet = document.getElementById("nav-fleet");
    const navSettings = document.getElementById("nav-settings");
    const navCache = document.getElementById("nav-cache");

    if (navFleet) navFleet.className = `btn ${this.activeTab === "fleet" ? "btn-primary" : ""}`;
    if (navSettings) navSettings.className = `btn ${this.activeTab === "settings" ? "btn-primary" : ""}`;
    if (navCache) navCache.className = `btn ${this.activeTab === "cache" ? "btn-primary" : ""}`;
  }

  async start() {
    this.header.render(undefined, false);
    this.capacity.render(undefined);
    this.setTab("fleet");

    // Initial state fetch
    await this.refresh();

    // Subscribe to real-time SSE stream
    client.subscribeSSE({
      onFleet: (newState) => {
        this.updateState(newState, true);
      },
      onError: () => {
        this.header.render(this.state, false);
      },
    });

    // Fallback poll every 10s
    window.setInterval(() => {
      this.refresh();
    }, 10000);
  }

  private async refresh() {
    try {
      const state = await client.getFleet();
      this.updateState(state, true);
    } catch (err) {
      console.warn("Could not fetch fleet state", err);
      this.header.render(this.state, false);
    }
  }

  private updateState(state: FleetState, connected: boolean) {
    this.state = state;
    this.header.render(state, connected);
    this.capacity.render(state);
    this.queue.setJobs(state.queued_jobs || []);
    this.priority.setState(state.repo_priority || [], state.paused_repos || []);
    this.fleet.setRunners(state.runners || []);
  }
}

const app = new App();
app.start();
