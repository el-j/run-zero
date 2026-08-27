import"./hoisted.BwSBHmzc.js";const s={quickstart:`# 1. Clone repository and run interactive setup wizard
❯ git clone git@github.com:el-j/run-zero.git
❯ cd run-zero && make env

# 2. Launch Autoscaler & local proxy registries
❯ make start

# 3. Stream real-time ephemeral runner telemetry
❯ make logs`,orbstack:`# Configure OrbStack macOS Linux VM backend
# Inside .env:
RUNNER_BACKEND=orbstack-vm
RUNNER_ARCH=both
AUTO_ROUTE_VM=true

# Build golden base VM image for instant spins:
❯ make build-vm-base

# Launch runners:
❯ make start`,wsl:`# Configure Windows WSL2 Linux VM backend
# Inside .env:
RUNNER_BACKEND=wsl2
RUNNER_ARCH=amd64

# Launch runners:
❯ make start`,multipass:`# Configure Cross-Platform Multipass Ubuntu VMs
# Inside .env:
RUNNER_BACKEND=multipass

# Launch runners:
❯ make start`},a=document.querySelectorAll(".wtab-btn"),r=document.getElementById("terminal-code"),t=document.getElementById("btn-copy-code");a&&r&&a.forEach(n=>{n.addEventListener("click",()=>{a.forEach(o=>o.classList.remove("active")),n.classList.add("active");const e=n.getAttribute("data-tab");e&&s[e]&&(r.innerHTML=s[e].replace(/^(#.*)$/gm,'<span class="c">$1</span>').replace(/^(❯)/gm,'<span class="prompt">❯</span>'))})});t&&r&&t.addEventListener("click",()=>{const n=r.textContent?r.textContent.replace(/^❯ /gm,""):"";navigator.clipboard.writeText(n).then(()=>{const e=t.querySelector(".copy-text");e&&(e.textContent="COPIED!",t.style.color="var(--crimson-light)",t.style.borderColor="var(--border-crimson)",setTimeout(()=>{e.textContent="COPY",t.style.color="",t.style.borderColor=""},2e3))})});
