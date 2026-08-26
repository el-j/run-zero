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
  const statUptime = document.getElementById('stat-uptime');
  const statEngine = document.getElementById('stat-default-engine');
  const statVersion = document.getElementById('stat-version');

  const kpiActiveRunners = document.getElementById('kpi-active-runners');
  const kpiMaxRunners = document.getElementById('kpi-max-runners');
  const kpiMinRunnersText = document.getElementById('kpi-min-runners-text');
  const kpiQueuedJobs = document.getElementById('kpi-queued-jobs');
  const kpiReposMonitored = document.getElementById('kpi-repos-monitored');
  const kpiVmRatio = document.getElementById('kpi-vm-ratio');
  const kpiCacheSize = document.getElementById('kpi-cache-size');

  const runnersGrid = document.getElementById('runners-grid');
  const runnersEmptyState = document.getElementById('runners-empty-state');
  const runnersCountBadge = document.getElementById('runners-count-badge');
  const reposList = document.getElementById('repos-list');
  const reposCountBadge = document.getElementById('repos-count-badge');

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

  const szNpm = document.getElementById('sz-npm');
  const szPip = document.getElementById('sz-pip');
  const szGo = document.getElementById('sz-go');
  const szCargo = document.getElementById('sz-cargo');
  const szToolcache = document.getElementById('sz-toolcache');
  const driversStatusList = document.getElementById('drivers-status-list');

  let eventSource = null;
  let retryTimeout = null;

  // Initialize SSE Connection
  function connectSSE() {
    if (eventSource) {
      eventSource.close();
    }

    setConnectionStatus('connecting', 'CONNECTING...');

    eventSource = new EventSource('/api/events');

    eventSource.onopen = function () {
      setConnectionStatus('online', 'LIVE OBSERVABILITY');
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
      setConnectionStatus('error', 'RECONNECTING');
      eventSource.close();
      if (!retryTimeout) {
        retryTimeout = setTimeout(connectSSE, 3000);
      }
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

  // Render complete state snapshot
  function renderState(state) {
    if (!state) return;

    // Header & KPIs
    statVersion.textContent = `v${state.version || '0.1.0'}`;
    statEngine.textContent = (state.default_engine || 'DOCKER').toUpperCase();
    statUptime.textContent = state.uptime || '00:00:00';

    const github = state.github || {};
    const rateLimitRem = github.rate_limit_remaining || 0;
    const rateLimitTot = github.rate_limit_total || 5000;
    statRateLimit.textContent = `${rateLimitRem}/${rateLimitTot}`;
    const pct = Math.min(100, Math.max(0, (rateLimitRem / rateLimitTot) * 100));
    statRateLimitBar.style.width = `${pct}%`;
    if (pct < 20) {
      statRateLimitBar.style.backgroundColor = 'var(--accent-red)';
    } else if (pct < 50) {
      statRateLimitBar.style.backgroundColor = 'var(--accent-amber)';
    } else {
      statRateLimitBar.style.backgroundColor = 'var(--accent-emerald)';
    }

    const concurrency = state.concurrency || {};
    kpiActiveRunners.textContent = concurrency.active || 0;
    kpiMaxRunners.textContent = `/ ${concurrency.max || 4} max`;
    kpiMinRunnersText.textContent = `${concurrency.min || 0} standby min`;

    kpiQueuedJobs.textContent = github.queued_jobs_count || 0;
    const repos = github.monitored_repos || [];
    kpiReposMonitored.textContent = `Across ${repos.length} tracked repo(s)`;

    // Routing ratio
    const rstats = state.routing_stats || {};
    const dJobs = rstats.docker_jobs || 0;
    const vJobs = rstats.vm_jobs || 0;
    const totalJobs = dJobs + vJobs;
    const vmRatio = totalJobs > 0 ? Math.round((vJobs / totalJobs) * 100) : 0;
    kpiVmRatio.textContent = `${vmRatio}%`;

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

    // Cache metrics
    const cache = state.cache || {};
    const sizes = cache.sizes || {};
    kpiCacheSize.textContent = sizes.total_host || '0 B';
    szNpm.textContent = sizes.npm || '0 B';
    szPip.textContent = sizes.pip || '0 B';
    szGo.textContent = sizes['go-mod'] || '0 B';
    szCargo.textContent = sizes.cargo || '0 B';
    szToolcache.textContent = sizes.toolcache || '0 B';

    // Active Runners Grid
    renderRunners(state.runners || []);

    // Repositories List
    renderRepos(repos, github.queued_jobs || []);

    // Driver availability
    renderDrivers(state.available_drivers || []);

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
            <span>📦</span>
            <span>${escapeHtml(r.target_repo || 'Standby Pool')}</span>
          </div>
          <div class="runner-card-top">
            <span class="stat-label">STATUS: <b>${escapeHtml((r.state || 'running').toUpperCase())}</b></span>
            <span class="runner-duration font-mono">⏱️ ${escapeHtml(r.duration || 'active')}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderRepos(repos, queuedJobs) {
    reposCountBadge.textContent = `${repos.length} REPOSITORIES`;
    if (repos.length === 0) {
      reposList.innerHTML = '<div class="empty-substate">No active repositories detected.</div>';
      return;
    }

    const queuedByRepo = {};
    queuedJobs.forEach(j => {
      const repo = j.repo || '';
      queuedByRepo[repo] = (queuedByRepo[repo] || 0) + 1;
    });

    reposList.innerHTML = repos.map(repo => {
      const qCount = queuedByRepo[repo] || 0;
      const qClass = qCount > 0 ? 'queue-active' : 'queue-idle';
      const qText = qCount > 0 ? `${qCount} queued job(s)` : 'idle';

      return `
        <div class="repo-row">
          <span class="repo-name font-mono">${escapeHtml(repo)}</span>
          <span class="repo-queue-badge ${qClass}">${qText}</span>
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
      const statusClass = isOnline ? 'online' : '';
      const statusText = isOnline ? 'Available' : 'Inactive';

      return `
        <div class="cache-row">
          <div class="cache-info">
            <span class="cache-name">${d.icon} ${d.name}</span>
            <span class="stat-label">${d.id}</span>
          </div>
          <span class="badge ${isOnline ? 'badge-pulse' : 'badge-neutral'}">${statusText}</span>
        </div>
      `;
    }).join('');
  }

  // Live Terminal Log Streamer
  function appendLog(entry) {
    if (!logTerminal || !entry) return;
    const ts = entry.timestamp || new Date().toLocaleTimeString();
    const msg = entry.message || '';

    const lineEl = document.createElement('div');
    lineEl.className = 'log-line';
    lineEl.innerHTML = `<span class="log-ts">[${escapeHtml(ts)}]</span>${escapeHtml(msg)}`;

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
      toast.style.borderColor = 'var(--accent-red)';
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
})();
