/**
 * RunZero Real-Time Observability Web Dashboard Client
 * EventSource SSE real-time streaming, interactive telemetry, and control dispatch.
 */

(function () {
  'use strict';

  // DOM Elements
  const connectionBadge = document.getElementById('connection-status-badge');
  const connectionText = document.getElementById('connection-status-text');
  const statRateLimit = document.getElementById('stat-rate-limit');
  const statRateLimitBar = document.getElementById('stat-rate-limit-bar');
  const statRateMeta = document.getElementById('stat-rate-meta');
  const statUptime = document.getElementById('stat-uptime');
  const statEngine = document.getElementById('stat-default-engine');
  const statVersion = document.getElementById('stat-version');

  const kpiActiveRunners = document.getElementById('kpi-active-runners');
  const kpiMaxRunners = document.getElementById('kpi-max-runners');
  const kpiMinRunnersText = document.getElementById('kpi-min-runners-text');
  const kpiRunnerSizing = document.getElementById('kpi-runner-sizing');
  const bridgeDriftBox = document.getElementById('bridge-drift-box');
  const statBridgeDrift = document.getElementById('stat-bridge-drift');
  const kpiQueuedJobs = document.getElementById('kpi-queued-jobs');
  const kpiReposMonitored = document.getElementById('kpi-repos-monitored');
  const kpiVmRatio = document.getElementById('kpi-vm-ratio');
  const kpiRoutingSub = document.getElementById('kpi-routing-sub');
  const kpiCacheSize = document.getElementById('kpi-cache-size');

  const runnersGrid = document.getElementById('runners-grid');
  const runnersEmptyState = document.getElementById('runners-empty-state');
  const runnersCountBadge = document.getElementById('runners-count-badge');
  const reposList = document.getElementById('repos-list');
  const reposCountBadge = document.getElementById('repos-count-badge');
  const imageBuildsList = document.getElementById('image-builds-list');
  const imageBuildsEmptyState = document.getElementById('image-builds-empty-state');
  const imageBuildsCountBadge = document.getElementById('image-builds-count-badge');

  const logTerminal = document.getElementById('log-terminal');
  const autoScrollToggle = document.getElementById('auto-scroll-toggle');
  const btnClearLogs = document.getElementById('btn-clear-logs');
  const btnPruneRunners = document.getElementById('btn-prune-runners');
  const btnPurgeAllCaches = document.getElementById('btn-purge-all-caches');

  const barDockerJobs = document.getElementById('bar-docker-jobs');
  const barVmJobs = document.getElementById('bar-vm-jobs');
  const cntDockerJobs = document.getElementById('cnt-docker-jobs');
  const cntVmJobs = document.getElementById('cnt-vm-jobs');

  const trigServices = document.getElementById('trig-services');
  const trigDind = document.getElementById('trig-dind');
  const trigBrowser = document.getElementById('trig-browser');
  const trigE2e = document.getElementById('trig-e2e');
  const trigSystemd = document.getElementById('trig-systemd');
  const trigCustom = document.getElementById('trig-custom');

  // Host cache rows: element id suffix -> key in state.cache.sizes.
  const CACHE_ROWS = [
    ['npm', 'npm'],
    ['pnpm', 'pnpm'],
    ['pip', 'pip'],
    ['go', 'go-mod'],
    ['cargo', 'cargo'],
    ['toolcache', 'toolcache'],
    ['playwright', 'playwright'],
  ];

  const kpiRunnersBar = document.getElementById('kpi-runners-bar');
  const kpiQueueBar = document.getElementById('kpi-queue-bar');
  const kpiRoutingBar = document.getElementById('kpi-routing-bar');
  const repoSearchInput = document.getElementById('repo-search-input');

  const driversStatusList = document.getElementById('drivers-status-list');
  const actionsScope = document.getElementById('actions-scope');
  const actionsIncluded = document.getElementById('actions-included');
  const actionsTotalUsed = document.getElementById('actions-total-used');
  const actionsPaidUsed = document.getElementById('actions-paid-used');
  const actionsRemaining = document.getElementById('actions-remaining');
  const actionsUpdated = document.getElementById('actions-updated');
  const actionsStatus = document.getElementById('actions-status');

  const queueSlotsBadge = document.getElementById('queue-slots-badge');
  const queueBusySlots = document.getElementById('queue-busy-slots');
  const queueMaxSlots = document.getElementById('queue-max-slots');
  const queueFreeSlots = document.getElementById('queue-free-slots');
  const queueTotalJobs = document.getElementById('queue-total-jobs');
  const queueJobsView = document.getElementById('queue-jobs-view');
  const queueJobsCountTag = document.getElementById('queue-jobs-count-tag');

  let eventSource = null;
  let retryTimeout = null;
  let reconnectAttempt = 0;
  let statusProbeTimer = null;
  let currentRepos = [];
  let currentQueuedJobs = [];
  let currentRepoPriority = [];
  let currentPausedRepos = new Set();
  let currentConcurrency = { active: 0, max: 4, min: 0 };
  let draggedRepo = null;

  function backoffMs(attempt) {
    const base = Math.min(30000, 1000 * Math.pow(2, Math.max(0, attempt - 1)));
    const jitter = Math.floor(Math.random() * 500);
    return base + jitter;
  }

  function stopStatusProbe() {
    if (statusProbeTimer) {
      clearInterval(statusProbeTimer);
      statusProbeTimer = null;
    }
  }

  function startStatusProbe() {
    if (statusProbeTimer) {
      return;
    }
    statusProbeTimer = setInterval(function () {
      fetch('/api/status', { cache: 'no-store' })
        .then(function (res) {
          if (!res.ok) {
            throw new Error(`status ${res.status}`);
          }
          return res.json();
        })
        .then(function (state) {
          renderState(state);
          if (!eventSource || eventSource.readyState === EventSource.CLOSED) {
            connectSSE();
          }
        })
        .catch(function () {
          // keep waiting for stack recovery
        });
    }, 4000);
  }

  function scheduleReconnect() {
    if (retryTimeout) {
      return;
    }
    reconnectAttempt += 1;
    const waitMs = backoffMs(reconnectAttempt);
    const seconds = (waitMs / 1000).toFixed(1);
    setConnectionStatus('error', `RECONNECTING IN ${seconds}s`);
    startStatusProbe();
    retryTimeout = setTimeout(function () {
      retryTimeout = null;
      connectSSE();
    }, waitMs);
  }

  // Initialize SSE Connection
  function connectSSE() {
    if (eventSource) {
      eventSource.close();
    }

    setConnectionStatus('connecting', 'CONNECTING...');

    eventSource = new EventSource('/api/events');

    eventSource.onopen = function () {
      setConnectionStatus('online', 'LIVE OBSERVABILITY');
      reconnectAttempt = 0;
      stopStatusProbe();
      if (retryTimeout) {
        clearTimeout(retryTimeout);
        retryTimeout = null;
      }
    };

    eventSource.addEventListener('state', function (e) {
      try {
        const state = JSON.parse(e.data);
        renderState(state);
      } catch (err) {
        console.error('[Dashboard] Error parsing state snapshot:', err);
      }
    });

    eventSource.addEventListener('log', function (e) {
      try {
        const logEntry = JSON.parse(e.data);
        appendLog(logEntry);
      } catch (err) {
        console.error('[Dashboard] Error parsing log event:', err);
      }
    });

    eventSource.onerror = function () {
      if (eventSource) {
        eventSource.close();
      }
      scheduleReconnect();
    };
  }

  function setConnectionStatus(status, text) {
    connectionText.textContent = text;
    connectionBadge.className = 'badge badge-pulse';
    if (status === 'connecting') {
      connectionBadge.classList.add('connecting');
    } else if (status === 'error') {
      connectionBadge.classList.add('error');
    }
  }

  function toRepoUrl(repoFullName) {
    const repo = String(repoFullName || '').trim();
    if (!repo || !repo.includes('/')) {
      return '';
    }
    return `https://github.com/${repo}`;
  }

  function toSafeGithubUrl(url) {
    const u = String(url || '');
    return u.startsWith('https://github.com/') ? u : '';
  }

  function formatReset(resetEpoch) {
    const epoch = Number(resetEpoch || 0);
    if (!epoch || Number.isNaN(epoch)) {
      return '--:--:--';
    }
    const remainingSec = Math.max(0, Math.floor(epoch - (Date.now() / 1000)));
    const h = Math.floor(remainingSec / 3600);
    const m = Math.floor((remainingSec % 3600) / 60);
    const s = remainingSec % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  function toNullableNumber(value) {
    if (value === null || value === undefined || value === '') {
      return null;
    }
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
  }

  function formatInteger(value) {
    const n = toNullableNumber(value);
    return n === null ? '--' : n.toLocaleString();
  }

  function formatUnixTimestamp(value) {
    const n = toNullableNumber(value);
    if (n === null || n <= 0) {
      return '--';
    }
    return new Date(n * 1000).toLocaleString();
  }

  function parseByteString(str) {
    if (!str || typeof str !== 'string') return 0;
    const match = str.trim().match(/^([0-9.]+)\s*([A-Za-z]+)?$/);
    if (!match) return 0;
    const val = parseFloat(match[1]);
    const unit = (match[2] || 'B').toUpperCase();
    const multipliers = {
      'B': 1,
      'KB': 1024,
      'KIB': 1024,
      'MB': 1024 * 1024,
      'MIB': 1024 * 1024,
      'GB': 1024 * 1024 * 1024,
      'GIB': 1024 * 1024 * 1024,
      'TB': 1024 * 1024 * 1024 * 1024,
    };
    return val * (multipliers[unit] || 1);
  }

  function renderActionsBilling(actionsBilling) {
    if (!actionsScope) return;

    const data = actionsBilling || {};
    const scopeType = String(data.scope_type || 'unknown').toUpperCase();
    const scopeName = String(data.scope_name || 'unknown');
    const status = String(data.status || 'unknown').toLowerCase();
    const errorMsg = data.error ? String(data.error) : '';

    actionsScope.textContent = `${scopeType}:${scopeName}`;
    actionsIncluded.textContent = formatInteger(data.included_minutes);
    actionsTotalUsed.textContent = formatInteger(data.total_minutes_used);
    actionsPaidUsed.textContent = formatInteger(data.total_paid_minutes_used);
    actionsRemaining.textContent = formatInteger(data.minutes_remaining);
    actionsUpdated.textContent = formatUnixTimestamp(data.updated_at);

    if (status === 'ok') {
      actionsStatus.textContent = 'Billing synced from GitHub.';
      actionsStatus.classList.remove('error');
      actionsStatus.classList.add('ok');
    } else {
      actionsStatus.textContent = errorMsg || 'Billing unavailable. Check token scopes/permissions.';
      actionsStatus.classList.remove('ok');
      actionsStatus.classList.add('error');
    }
  }

  // Per-runner CPU/memory limit, flagged when MAX_RUNNERS x limit oversubscribes the host (#71)
  function renderSizing(sizing) {
    if (!kpiRunnerSizing) return;
    if (!sizing.source) {
      kpiRunnerSizing.textContent = '// sizing unknown';
      return;
    }
    const cpus = sizing.cpus ? `${sizing.cpus} CPU` : 'unlimited CPU';
    const mem = sizing.memory_mib ? `${(sizing.memory_mib / 1024).toFixed(1)} GiB` : 'unlimited mem';
    const warnings = sizing.warnings || [];
    kpiRunnerSizing.textContent = `// ${cpus} · ${mem} each${warnings.length ? ' ⚠ oversubscribed' : ''}`;
    kpiRunnerSizing.title = warnings.length ? warnings.join('\n') : `${sizing.source} sizing on ${sizing.host_cpus} CPU / ${sizing.host_memory_mib} MiB`;
    kpiRunnerSizing.classList.toggle('text-danger', warnings.length > 0);
  }

  // Render complete state snapshot
  function renderState(state) {
    if (!state) return;

    // Header & KPIs
    statVersion.textContent = state.version ? `v${state.version}` : 'v…';
    statEngine.textContent = (state.default_engine || 'DOCKER').toUpperCase();
    statUptime.textContent = state.uptime || '00:00:00';

    const github = state.github || {};
    const rateLimitRem = toNullableNumber(github.rate_limit_remaining);
    const rateLimitTot = toNullableNumber(github.rate_limit_total);
    const rateLimitUsed = toNullableNumber(github.rate_limit_used);
    const rateLimitResource = github.rate_limit_resource || 'unknown';
    const rateLimitReset = toNullableNumber(github.rate_limit_reset);
    if (rateLimitRem === null || rateLimitTot === null) {
      statRateLimit.textContent = '--/--';
    } else {
      statRateLimit.textContent = `${rateLimitRem}/${rateLimitTot}`;
    }
    if (statRateMeta) {
      const usedText = rateLimitUsed === null ? '--' : String(rateLimitUsed);
      statRateMeta.textContent = `used ${usedText} • reset ${formatReset(rateLimitReset)} • ${rateLimitResource}`;
    }
    const pct = (rateLimitRem === null || rateLimitTot === null || rateLimitTot <= 0)
      ? 0
      : Math.min(100, Math.max(0, (rateLimitRem / rateLimitTot) * 100));
    statRateLimitBar.style.width = `${pct}%`;
    if (rateLimitRem === null || rateLimitTot === null) {
      statRateLimitBar.style.backgroundColor = 'var(--text-dim)';
    } else if (pct < 20) {
      statRateLimitBar.style.backgroundColor = 'var(--crimson)';
    } else if (pct < 50) {
      statRateLimitBar.style.backgroundColor = 'var(--solar)';
    } else {
      statRateLimitBar.style.backgroundColor = 'var(--emerald)';
    }

    const concurrency = state.concurrency || {};
    const activeRunners = concurrency.active || 0;
    const maxRunners = concurrency.max || 4;
    kpiActiveRunners.textContent = activeRunners;
    kpiMaxRunners.textContent = `/ ${maxRunners} max`;
    kpiMinRunnersText.textContent = `// ${concurrency.min || 0} standby min`;
    renderSizing(state.runner_sizing || {});
    if (bridgeDriftBox) {
      bridgeDriftBox.hidden = !state.bridge_drift;
      statBridgeDrift.title = state.bridge_drift || '';
    }
    if (kpiRunnersBar) {
      const runnersPct = Math.min(100, Math.round((activeRunners / Math.max(1, maxRunners)) * 100));
      kpiRunnersBar.style.width = `${runnersPct}%`;
    }

    const queuedCount = github.queued_jobs_count || 0;
    kpiQueuedJobs.textContent = queuedCount;
    const repos = github.monitored_repos || [];
    kpiReposMonitored.textContent = `// Across ${repos.length} tracked repo(s)`;
    if (kpiQueueBar) {
      const queuePct = Math.min(100, queuedCount * 25);
      kpiQueueBar.style.width = `${queuePct}%`;
    }

    // Routing ratio
    const rstats = state.routing_stats || {};
    const dJobs = rstats.docker_jobs || 0;
    const vJobs = rstats.vm_jobs || 0;
    const totalJobs = dJobs + vJobs;
    const vmRatio = totalJobs > 0 ? Math.round((vJobs / totalJobs) * 100) : 0;
    kpiVmRatio.textContent = `${vmRatio}%`;
    if (kpiRoutingBar) {
      kpiRoutingBar.style.width = `${vmRatio}%`;
    }
    if (kpiRoutingSub) {
      const native = rstats.native_arch_overrides || 0;
      kpiRoutingSub.textContent = native > 0
        ? `// ${native} amd64 job(s) run natively`
        : '// Auto-detect DIND & Services';
    }

    // Routing breakdown
    cntDockerJobs.textContent = dJobs;
    cntVmJobs.textContent = vJobs;
    const dPct = totalJobs > 0 ? Math.round((dJobs / totalJobs) * 100) : 50;
    barDockerJobs.style.width = `${dPct}%`;
    barVmJobs.style.width = `${100 - dPct}%`;

    const triggers = rstats.vm_triggers_breakdown || {};
    trigServices.textContent = triggers.services || 0;
    trigDind.textContent = triggers.dind || 0;
    trigBrowser.textContent = triggers.browser || 0;
    trigE2e.textContent = triggers.e2e || 0;
    trigSystemd.textContent = triggers.systemd || 0;
    trigCustom.textContent = triggers.custom_label || 0;

    // Cache metrics & bars
    const cache = state.cache || {};
    const sizes = cache.sizes || {};
    kpiCacheSize.textContent = sizes.total_host || '0 B';
    // Size labels plus fill bars relative to the largest category
    const cacheBytes = CACHE_ROWS.map(([, key]) => parseByteString(sizes[key]));
    const maxCacheCat = Math.max(1, ...cacheBytes);
    CACHE_ROWS.forEach(([id, key], i) => {
      const label = document.getElementById(`sz-${id}`);
      const bar = document.getElementById(`bar-cache-${id}`);
      if (label) label.textContent = sizes[key] || '0 B';
      if (bar) bar.style.width = `${Math.max(5, Math.min(100, Math.round((cacheBytes[i] / maxCacheCat) * 100)))}%`;
    });

    // Active Runners Grid
    renderRunners(state.runners || []);

    // Repositories List & Live Queue Steering
    currentRepos = repos;
    currentRepoPriority = state.repo_priority || [];
    currentPausedRepos = new Set(state.paused_repos || []);
    currentQueuedJobs = github.queued_jobs || [];
    currentConcurrency = concurrency;
    renderRepos(currentRepos, currentQueuedJobs, currentRepoPriority, currentPausedRepos);
    renderQueue(currentQueuedJobs, currentRepoPriority, currentPausedRepos, currentConcurrency);

    // Golden image build status
    renderImageBuilds(state.image_builds || []);

    // Driver availability
    renderDrivers(state.available_drivers || []);

    // Actions billing
    renderActionsBilling(github.actions_billing || {});

    // Render recent logs if empty
    if (logTerminal.children.length === 0 && state.recent_logs && state.recent_logs.length > 0) {
      state.recent_logs.forEach(appendLog);
    }
  }

  function renderRunners(runners) {
    runnersCountBadge.textContent = `${runners.length} RUNNING`;
    if (runners.length === 0) {
      runnersEmptyState.classList.remove('hidden');
      runnersGrid.classList.add('hidden');
      runnersGrid.innerHTML = '';
      return;
    }

    runnersEmptyState.classList.add('hidden');
    runnersGrid.classList.remove('hidden');

    runnersGrid.innerHTML = runners.map(r => {
      const isVm = (r.backend || '').toLowerCase().includes('vm') || (r.backend || '').toLowerCase().includes('orb') || (r.backend || '').toLowerCase().includes('wsl') || (r.backend || '').toLowerCase().includes('multipass');
      const engineTagClass = isVm ? 'tag-vm' : 'tag-docker';
      const engineName = isVm ? (r.backend || 'VM').toUpperCase() : 'DOCKER';
      const archName = (r.target_arch || 'ARM64').toUpperCase();
      const repoUrl = toRepoUrl(r.target_repo);
      const runUrl = toSafeGithubUrl(r.run_url);
      const jobUrl = toSafeGithubUrl(r.job_url);
      let runnerLinks = '';
      if (repoUrl || runUrl || jobUrl) {
        const links = [];
        if (repoUrl) {
          links.push(`<a class="quick-link" href="${escapeHtml(repoUrl)}" target="_blank" rel="noopener noreferrer">Repository</a>`);
        }
        if (runUrl) {
          links.push(`<a class="quick-link" href="${escapeHtml(runUrl)}" target="_blank" rel="noopener noreferrer">Workflow run</a>`);
        }
        if (jobUrl) {
          links.push(`<a class="quick-link" href="${escapeHtml(jobUrl)}" target="_blank" rel="noopener noreferrer">Queued job</a>`);
        }
        runnerLinks = `<div class="runner-links">${links.join('<span class="link-sep">•</span>')}</div>`;
      }

      return `
        <div class="runner-card">
          <div class="runner-card-top">
            <div class="runner-id-wrap">
              <span class="runner-pulse"></span>
              <span class="runner-id font-mono">${escapeHtml(r.name || r.id)}</span>
            </div>
            <div class="runner-badges">
              <span class="tag-engine ${engineTagClass}">${engineName}</span>
              <span class="tag-arch font-mono">${archName}</span>
            </div>
          </div>
          <div class="runner-repo">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
            </svg>
            <span>${escapeHtml(r.target_repo || 'Standby Pool')}</span>
          </div>
          ${runnerLinks}
          <div class="runner-card-bottom">
            <span class="stat-label">STATUS: <b class="runner-status-val">${escapeHtml((r.state || 'running').toUpperCase())}</b></span>
            <span class="runner-duration font-mono">⏱️ ${escapeHtml(r.duration || 'active')}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  function formatWaitTime(isoCreated, isoStarted, status) {
    const ts = status === 'in_progress' && isoStarted ? Date.parse(isoStarted) : (isoCreated ? Date.parse(isoCreated) : null);
    if (!ts || isNaN(ts)) {
      return status === 'in_progress' ? 'running' : 'waiting';
    }
    const elapsedSecs = Math.max(0, Math.floor((Date.now() - ts) / 1000));
    const mins = Math.floor(elapsedSecs / 60);
    const secs = elapsedSecs % 60;
    const hrs = Math.floor(mins / 60);
    const m = mins % 60;
    const prefix = status === 'in_progress' ? 'Running' : 'Waited';
    if (hrs > 0) {
      return `${prefix} ${hrs}h ${m}m`;
    }
    if (mins > 0) {
      return `${prefix} ${mins}m ${secs}s`;
    }
    return `${prefix} ${secs}s`;
  }

  function getOrderedRepos(repos, priorityList) {
    const prio = priorityList || [];
    const set = new Set(repos);
    const result = [];
    prio.forEach(r => {
      if (set.has(r) && !result.includes(r)) {
        result.push(r);
      }
    });
    repos.forEach(r => {
      if (!result.includes(r)) {
        result.push(r);
      }
    });
    return result;
  }

  function updateRepoPriorityState(newPriority, newPaused) {
    const payload = {
      priority: newPriority,
      paused: Array.from(newPaused),
    };
    fetch('/api/actions/repo-priority', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        currentRepoPriority = data.priority || newPriority;
        currentPausedRepos = new Set(data.paused || newPaused);
        renderRepos(currentRepos, currentQueuedJobs, currentRepoPriority, currentPausedRepos);
        renderQueue(currentQueuedJobs, currentRepoPriority, currentPausedRepos, currentConcurrency);
        showToast('Repository priority & pause state saved');
      })
      .catch(err => {
        showToast(`Failed to save repository settings: ${err.message}`, true);
      });
  }

  function attachRepoControlListeners(repos) {
    if (!reposList) return;

    reposList.querySelectorAll('button[data-action]').forEach(btn => {
      btn.onclick = function (e) {
        e.stopPropagation();
        const action = this.getAttribute('data-action');
        const repo = this.getAttribute('data-repo');
        if (!repo) return;

        let newPriority = getOrderedRepos(currentRepos, currentRepoPriority);
        const newPaused = new Set(currentPausedRepos);

        if (action === 'toggle-pause') {
          if (newPaused.has(repo)) {
            newPaused.delete(repo);
          } else {
            newPaused.add(repo);
          }
        } else if (action === 'move-up') {
          const idx = newPriority.indexOf(repo);
          if (idx > 0) {
            const temp = newPriority[idx - 1];
            newPriority[idx - 1] = newPriority[idx];
            newPriority[idx] = temp;
          }
        } else if (action === 'move-down') {
          const idx = newPriority.indexOf(repo);
          if (idx >= 0 && idx < newPriority.length - 1) {
            const temp = newPriority[idx + 1];
            newPriority[idx + 1] = newPriority[idx];
            newPriority[idx] = temp;
          }
        }

        currentRepoPriority = newPriority;
        currentPausedRepos = newPaused;
        renderRepos(currentRepos, currentQueuedJobs, currentRepoPriority, currentPausedRepos);
        renderQueue(currentQueuedJobs, currentRepoPriority, currentPausedRepos, currentConcurrency);
        updateRepoPriorityState(newPriority, newPaused);
      };
    });

    reposList.querySelectorAll('.repo-row').forEach(row => {
      row.ondragstart = function (e) {
        draggedRepo = this.getAttribute('data-repo');
        e.dataTransfer.effectAllowed = 'move';
        this.classList.add('repo-row-dragging');
      };
      row.ondragend = function () {
        draggedRepo = null;
        reposList.querySelectorAll('.repo-row').forEach(r => {
          r.classList.remove('repo-row-dragging', 'repo-row-drag-over');
        });
      };
      row.ondragover = function (e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        this.classList.add('repo-row-drag-over');
      };
      row.ondragleave = function () {
        this.classList.remove('repo-row-drag-over');
      };
      row.ondrop = function (e) {
        e.preventDefault();
        this.classList.remove('repo-row-drag-over');
        const targetRepo = this.getAttribute('data-repo');
        if (!draggedRepo || draggedRepo === targetRepo) return;

        const newPriority = getOrderedRepos(currentRepos, currentRepoPriority);
        const fromIdx = newPriority.indexOf(draggedRepo);
        const toIdx = newPriority.indexOf(targetRepo);

        if (fromIdx >= 0 && toIdx >= 0) {
          newPriority.splice(fromIdx, 1);
          newPriority.splice(toIdx, 0, draggedRepo);
          currentRepoPriority = newPriority;
          renderRepos(currentRepos, currentQueuedJobs, currentRepoPriority, currentPausedRepos);
          renderQueue(currentQueuedJobs, currentRepoPriority, currentPausedRepos, currentConcurrency);
          updateRepoPriorityState(newPriority, currentPausedRepos);
        }
      };
    });
  }

  function renderRepos(repos, queuedJobs, repoPriority, pausedRepos) {
    const query = repoSearchInput ? repoSearchInput.value.trim().toLowerCase() : '';
    const ordered = getOrderedRepos(repos, repoPriority);
    const filteredRepos = query
      ? ordered.filter(r => r.toLowerCase().includes(query))
      : ordered;

    reposCountBadge.textContent = `${repos.length} REPOSITORIES`;

    if (repos.length === 0) {
      reposList.innerHTML = '<div class="empty-substate">No active repositories detected.</div>';
      return;
    }

    if (filteredRepos.length === 0) {
      reposList.innerHTML = `<div class="empty-substate">No repositories matching "${escapeHtml(query)}"</div>`;
      return;
    }

    const queuedByRepo = {};
    queuedJobs.forEach(j => {
      const repo = j.repo || '';
      if (!queuedByRepo[repo]) {
        queuedByRepo[repo] = { queued: 0, running: 0, sample: j };
      }
      if (j.status === 'in_progress') {
        queuedByRepo[repo].running += 1;
      } else {
        queuedByRepo[repo].queued += 1;
      }
    });

    reposList.innerHTML = filteredRepos.map((repo, idx) => {
      const info = queuedByRepo[repo] || { queued: 0, running: 0, sample: null };
      const qCount = info.queued;
      const rCount = info.running;
      const isPaused = pausedRepos && pausedRepos.has(repo);

      let qBadge = '';
      if (isPaused) {
        qBadge = '<span class="repo-queue-badge queue-paused">PAUSED</span>';
      } else if (qCount > 0) {
        qBadge = `<span class="repo-queue-badge queue-active">${qCount} queued</span>`;
      } else if (rCount > 0) {
        qBadge = `<span class="repo-queue-badge queue-running">${rCount} running</span>`;
      } else {
        qBadge = '<span class="repo-queue-badge queue-idle">idle</span>';
      }

      const repoUrl = toRepoUrl(repo);
      const sample = info.sample || {};
      const runUrl = toSafeGithubUrl(sample.run_url);
      const jobUrl = toSafeGithubUrl(sample.job_url);
      const linkChunks = [];
      if (repoUrl) {
        linkChunks.push(`<a class="quick-link" href="${escapeHtml(repoUrl)}" target="_blank" rel="noopener noreferrer">Repo</a>`);
      }
      if (runUrl) {
        linkChunks.push(`<a class="quick-link" href="${escapeHtml(runUrl)}" target="_blank" rel="noopener noreferrer">Run</a>`);
      }
      if (jobUrl) {
        linkChunks.push(`<a class="quick-link" href="${escapeHtml(jobUrl)}" target="_blank" rel="noopener noreferrer">Job</a>`);
      }
      const quickLinks = linkChunks.length > 0
        ? `<div class="repo-links">${linkChunks.join('<span class="link-sep">•</span>')}</div>`
        : '';

      const pauseBtnClass = isPaused ? 'btn-resume-repo' : 'btn-pause-repo';
      const pauseBtnText = isPaused ? 'RESUME' : 'PAUSE';
      const pauseBtnTitle = isPaused ? 'Resume runner allocation for this repository' : 'Pause runner allocation for this repository';

      return `
        <div class="repo-row ${isPaused ? 'repo-row-paused' : ''}" draggable="true" data-repo="${escapeHtml(repo)}" data-index="${idx}">
          <div class="repo-prio-left">
            <span class="drag-handle" title="Drag to reorder priority">⠿</span>
            <span class="priority-rank-badge font-mono" title="Priority #${idx + 1}">#${idx + 1}</span>
            <div class="repo-main">
              <span class="repo-name font-mono">${escapeHtml(repo)}</span>
              ${quickLinks}
            </div>
          </div>
          <div class="repo-prio-right">
            ${qBadge}
            <button class="btn btn-xs ${pauseBtnClass}" data-action="toggle-pause" data-repo="${escapeHtml(repo)}" title="${pauseBtnTitle}">
              ${pauseBtnText}
            </button>
            <div class="prio-move-btns">
              <button class="btn btn-xs btn-move" data-action="move-up" data-repo="${escapeHtml(repo)}" title="Increase priority" ${idx === 0 ? 'disabled' : ''}>▲</button>
              <button class="btn btn-xs btn-move" data-action="move-down" data-repo="${escapeHtml(repo)}" title="Decrease priority" ${idx === filteredRepos.length - 1 ? 'disabled' : ''}>▼</button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    attachRepoControlListeners(filteredRepos);
  }

  function renderQueue(queuedJobs, repoPriority, pausedRepos, concurrency) {
    const activeRunners = (concurrency && concurrency.active) || 0;
    const maxRunners = (concurrency && concurrency.max) || 4;
    const queuedOnly = queuedJobs.filter(j => j.status !== 'in_progress');
    const freeSlots = Math.max(0, maxRunners - activeRunners);

    if (queueBusySlots) queueBusySlots.textContent = activeRunners;
    if (queueMaxSlots) queueMaxSlots.textContent = maxRunners;
    if (queueFreeSlots) queueFreeSlots.textContent = freeSlots;
    if (queueTotalJobs) queueTotalJobs.textContent = queuedOnly.length;
    if (queueSlotsBadge) {
      queueSlotsBadge.textContent = `${activeRunners}/${maxRunners} SLOTS BUSY • ${freeSlots} FREE`;
      if (freeSlots === 0) {
        queueSlotsBadge.className = 'panel-badge font-mono badge-danger';
      } else {
        queueSlotsBadge.className = 'panel-badge font-mono badge-cyan';
      }
    }
    if (queueJobsCountTag) {
      queueJobsCountTag.textContent = `${queuedJobs.length} JOBS`;
    }

    if (!queueJobsView) return;

    if (queuedJobs.length === 0) {
      queueJobsView.innerHTML = `
        <div class="empty-substate empty-queue-clean">
          <div class="clean-check-icon">✓</div>
          <div class="clean-text font-mono">ALL WORKFLOW QUEUES ARE CLEAR</div>
          <div class="clean-subtext">Waiting jobs will appear here in real-time as GitHub Actions workflows trigger.</div>
        </div>
      `;
      return;
    }

    const jobsByRepo = {};
    queuedJobs.forEach(job => {
      const repo = job.repo || 'unknown';
      if (!jobsByRepo[repo]) {
        jobsByRepo[repo] = [];
      }
      jobsByRepo[repo].push(job);
    });

    const orderedRepoNames = getOrderedRepos(Object.keys(jobsByRepo), repoPriority);

    queueJobsView.innerHTML = orderedRepoNames.map((repo, rIdx) => {
      const jobs = jobsByRepo[repo] || [];
      const isPaused = pausedRepos && pausedRepos.has(repo);
      const queuedCount = jobs.filter(j => j.status !== 'in_progress').length;
      const runningCount = jobs.filter(j => j.status === 'in_progress').length;

      const jobsCards = jobs.map(job => {
        const isRunning = job.status === 'in_progress';
        const statusBadge = isRunning
          ? '<span class="job-status-badge badge-running"><span class="beacon-dot"></span>IN PROGRESS</span>'
          : '<span class="job-status-badge badge-queued">QUEUED</span>';
        const posBadge = job.queue_position !== null && job.queue_position !== undefined
          ? `<span class="job-pos-badge font-mono">#${job.queue_position} IN QUEUE</span>`
          : (isRunning ? '<span class="job-pos-badge pos-running font-mono">RUNNING</span>' : '');

        const waitText = formatWaitTime(job.created_at, job.started_at, job.status);
        const labels = Array.isArray(job.labels) ? job.labels : [];
        const labelChips = labels.map(l => `<span class="tech-chip chip-mini font-mono">${escapeHtml(l)}</span>`).join('');

        let reasonBanner = '';
        if (job.waiting_reason) {
          let reasonClass = 'reason-normal';
          if (job.waiting_reason.includes('waiting behind')) reasonClass = 'reason-priority';
          else if (job.waiting_reason.includes('paused')) reasonClass = 'reason-paused';
          else if (job.waiting_reason.includes('free runner slot')) reasonClass = 'reason-busy';
          else if (job.waiting_reason === 'running') reasonClass = 'reason-active';

          reasonBanner = `
            <div class="queue-reason-banner ${reasonClass}">
              <span class="reason-indicator">●</span>
              <span class="reason-text font-mono">${escapeHtml(job.waiting_reason)}</span>
            </div>
          `;
        }

        const jobUrl = toSafeGithubUrl(job.job_url);
        const runUrl = toSafeGithubUrl(job.run_url);
        const links = [];
        if (jobUrl) links.push(`<a class="quick-link font-mono" href="${escapeHtml(jobUrl)}" target="_blank" rel="noopener noreferrer">View Job ↗</a>`);
        if (runUrl) links.push(`<a class="quick-link font-mono" href="${escapeHtml(runUrl)}" target="_blank" rel="noopener noreferrer">View Run ↗</a>`);
        const linksRow = links.length > 0 ? `<div class="job-links">${links.join('<span class="link-sep">•</span>')}</div>` : '';

        return `
          <div class="queue-job-card ${isRunning ? 'job-running-card' : ''}">
            <div class="job-card-header">
              <div class="job-header-left">
                ${posBadge}
                ${statusBadge}
                <span class="job-wf-name font-mono">${escapeHtml(job.workflow_name || job.workflow_path || 'Workflow')}</span>
              </div>
              <span class="job-wait-time font-mono">${escapeHtml(waitText)}</span>
            </div>
            <div class="job-card-title">
              <span class="job-title-name">${escapeHtml(job.name || 'Unnamed Job')}</span>
            </div>
            <div class="job-card-meta">
              <span class="meta-tag font-mono">🌿 ${escapeHtml(job.head_branch || 'main')}</span>
              <span class="meta-tag font-mono">⚡ ${escapeHtml(job.event || 'push')}</span>
              <span class="meta-tag font-mono">Attempt ${escapeHtml(job.run_attempt || 1)}</span>
            </div>
            ${labelChips ? `<div class="job-card-labels">${labelChips}</div>` : ''}
            ${reasonBanner}
            ${linksRow}
          </div>
        `;
      }).join('');

      return `
        <div class="repo-queue-group">
          <div class="repo-queue-group-header">
            <div class="group-header-left">
              <span class="group-prio-tag font-mono">PRIORITY #${rIdx + 1}</span>
              <span class="group-repo-name font-mono">${escapeHtml(repo)}</span>
              ${isPaused ? '<span class="panel-badge badge-paused-tag font-mono">PAUSED</span>' : ''}
            </div>
            <div class="group-header-right font-mono">
              ${queuedCount > 0 ? `<span class="group-count-queued">${queuedCount} queued</span>` : ''}
              ${runningCount > 0 ? `<span class="group-count-running">${runningCount} in-progress</span>` : ''}
              ${queuedCount === 0 && runningCount === 0 ? '<span class="group-count-idle">idle</span>' : ''}
            </div>
          </div>
          <div class="repo-queue-group-jobs">
            ${jobsCards}
          </div>
        </div>
      `;
    }).join('');
  }

  // Filter input event listener
  if (repoSearchInput) {
    repoSearchInput.addEventListener('input', function () {
      renderRepos(currentRepos, currentQueuedJobs, currentRepoPriority, currentPausedRepos);
    });
  }

  function renderImageBuilds(imageBuilds) {
    imageBuildsCountBadge.textContent = `${imageBuilds.length} TRACKED`;
    if (imageBuilds.length === 0) {
      imageBuildsEmptyState.classList.remove('hidden');
      imageBuildsList.classList.add('hidden');
      imageBuildsList.innerHTML = '';
      return;
    }

    imageBuildsEmptyState.classList.add('hidden');
    imageBuildsList.classList.remove('hidden');

    const statusClass = {
      building: 'image-status-building',
      ready: 'image-status-ready',
      failed: 'image-status-failed',
      cooldown: 'image-status-cooldown',
    };

    const sorted = imageBuilds.slice().sort((a, b) => (b.ts || 0) - (a.ts || 0));

    imageBuildsList.innerHTML = sorted.map(build => {
      const driver = (build.driver || 'unknown').toUpperCase();
      const arch = (build.arch || '?').toUpperCase();
      const profile = build.profile ? ` / ${escapeHtml(build.profile)}` : '';
      const status = (build.status || 'unknown').toLowerCase();
      const pillClass = statusClass[status] || 'image-status-cooldown';

      return `
        <div class="image-build-row">
          <div class="image-build-main">
            <span class="image-build-name font-mono">${escapeHtml(driver)} · ${escapeHtml(arch)}${profile}</span>
            <span class="image-build-detail">${escapeHtml(build.detail || '')}</span>
          </div>
          <span class="image-status-pill ${pillClass}">${escapeHtml(status)}</span>
        </div>
      `;
    }).join('');
  }

  function renderDrivers(availableDrivers) {
    if (!driversStatusList) return;
    const knownDrivers = [
      { id: 'docker', name: 'Docker Containers', icon: '🐳' },
      { id: 'orbstack-vm', name: 'OrbStack macOS VM', icon: '🍎' },
      { id: 'multipass', name: 'Canonical Multipass', icon: '🐧' },
      { id: 'wsl2', name: 'Windows WSL2', icon: '🪟' }
    ];

    driversStatusList.innerHTML = knownDrivers.map(d => {
      const isOnline = availableDrivers.includes(d.id);
      const statusText = isOnline ? 'Available' : 'Inactive';

      return `
        <div class="cache-row">
          <div class="cache-info">
            <span class="cache-name">${d.icon} ${d.name}</span>
            <span class="stat-label font-mono">${d.id}</span>
          </div>
          <span class="badge ${isOnline ? 'badge-pulse' : 'badge-neutral'}">${statusText}</span>
        </div>
      `;
    }).join('');
  }

  // Live Terminal Log Streamer with Syntax Highlighting
  function formatLogMessage(msg) {
    let safe = escapeHtml(msg);

    // Format tags like [Autoscaler], [Spawn], [Reconciler], [Prune], [Error]
    safe = safe.replace(/\[(Autoscaler|Reconciler|DockerDriver|OrbStackDriver|WSL2Driver|MultipassDriver)\]/g,
      '<span class="log-tag tag-cyan">[$1]</span>');
    safe = safe.replace(/\[(Spawn|ScaleUp|Ready|Started)\]/gi,
      '<span class="log-tag tag-emerald">[$1]</span>');
    safe = safe.replace(/\[(ScaleDown|Prune|Terminated|Stopped)\]/gi,
      '<span class="log-tag tag-amber">[$1]</span>');
    safe = safe.replace(/\[(Error|Failed|Exception|Timeout)\]/gi,
      '<span class="log-tag tag-crimson">[$1]</span>');
    safe = safe.replace(/\[(Bridge|VM|Routing)\]/gi,
      '<span class="log-tag tag-purple">[$1]</span>');

    return safe;
  }

  function appendLog(entry) {
    if (!logTerminal || !entry) return;
    const ts = entry.timestamp || new Date().toLocaleTimeString();
    const msg = entry.message || '';

    const lineEl = document.createElement('div');
    lineEl.className = 'log-line';
    lineEl.innerHTML = `<span class="log-ts font-mono">[${escapeHtml(ts)}]</span> <span class="log-content">${formatLogMessage(msg)}</span>`;

    logTerminal.appendChild(lineEl);

    // Limit buffer length in DOM
    if (logTerminal.children.length > 500) {
      logTerminal.removeChild(logTerminal.firstChild);
    }

    if (autoScrollToggle && autoScrollToggle.checked) {
      logTerminal.scrollTop = logTerminal.scrollHeight;
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Toast Notification Manager
  function showToast(message, isError = false) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    if (isError) {
      toast.style.borderColor = 'var(--crimson)';
    }
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // Interactive Actions
  window.cleanCacheCategory = function (category) {
    fetch('/api/actions/clean-cache', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category })
    })
      .then(res => res.json())
      .then(data => {
        showToast(`Cache cleaned: ${category}`);
      })
      .catch(err => {
        showToast(`Error cleaning cache: ${err}`, true);
      });
  };

  if (btnPurgeAllCaches) {
    btnPurgeAllCaches.addEventListener('click', function () {
      if (confirm('Are you sure you want to clear all host package caches?')) {
        cleanCacheCategory('all');
      }
    });
  }

  if (btnPruneRunners) {
    btnPruneRunners.addEventListener('click', function () {
      fetch('/api/actions/prune', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      })
        .then(res => res.json())
        .then(data => {
          showToast('Triggered fleet runner prune');
        })
        .catch(err => {
          showToast(`Prune failed: ${err}`, true);
        });
    });
  }

  if (btnClearLogs) {
    btnClearLogs.addEventListener('click', function () {
      if (logTerminal) {
        logTerminal.innerHTML = '';
      }
    });
  }

  // Start SSE connection on load
  connectSSE();

  window.addEventListener('beforeunload', function () {
    if (eventSource) {
      eventSource.close();
    }
    if (retryTimeout) {
      clearTimeout(retryTimeout);
      retryTimeout = null;
    }
    stopStatusProbe();
  });
})();

