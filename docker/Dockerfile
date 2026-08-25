FROM ubuntu:22.04

ARG RUNNER_VERSION="2.336.0"
ARG TARGETARCH

# Prevents debconf from prompting during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV RUNNER_TOOL_CACHE=/opt/hostedtoolcache
ENV DOTNET_ROOT=/usr/share/dotnet
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1
ENV NVM_DIR=/home/runner/.nvm
ENV PATH="/home/runner/.local/bin:/home/runner/go/bin:/usr/share/dotnet:/usr/share/dotnet/tools:${PATH}"

# 1. Update system and install essential tools & libraries
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    rsync \
    gnupg \
    lsb-release \
    jq \
    git \
    git-lfs \
    tar \
    unzip \
    zip \
    bzip2 \
    zstd \
    xz-utils \
    build-essential \
    cmake \
    pkg-config \
    libssl-dev \
    libffi-dev \
    libicu-dev \
    libsqlite3-dev \
    zlib1g-dev \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    sudo \
    iptables \
    software-properties-common \
    && git lfs install --system \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Docker CLI & Compose Plugin
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# 3. Install .NET SDK 8.0 & Configure Microsoft Repository
RUN curl -fsSL https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -o /tmp/packages-microsoft-prod.deb && \
    dpkg -i /tmp/packages-microsoft-prod.deb && \
    rm /tmp/packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y --no-install-recommends dotnet-sdk-8.0 && \
    rm -rf /var/lib/apt/lists/*

# 4. Create runner user with passwordless sudo access & create tool cache directory
RUN useradd -m -s /bin/bash runner && \
    usermod -aG sudo runner && \
    echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    mkdir -p /opt/hostedtoolcache && \
    chown -R runner:runner /opt/hostedtoolcache

WORKDIR /home/runner

# 5. Install NVM and pre-bake Node.js 20 (LTS), 22 (LTS), and 24 (Current) with yarn & pnpm
USER runner
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash && \
    . $NVM_DIR/nvm.sh && \
    nvm install 20 && \
    nvm install 22 && \
    nvm install 24 && \
    nvm alias default 20 && \
    nvm use 20 && \
    npm install -g yarn pnpm && \
    nvm use 22 && \
    npm install -g yarn pnpm && \
    nvm use 24 && \
    npm install -g yarn pnpm && \
    nvm use default

USER root

# Ensure NVM is auto-loaded for all shells
RUN echo 'export NVM_DIR="/home/runner/.nvm"' >> /etc/profile.d/nvm.sh && \
    echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> /etc/profile.d/nvm.sh && \
    echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> /etc/profile.d/nvm.sh && \
    chmod +x /etc/profile.d/nvm.sh

# 6. Download and extract GitHub Actions runner package based on architecture
RUN case "${TARGETARCH:-$(dpkg --print-architecture)}" in \
      "arm64") RUNNER_ARCH="arm64" ;; \
      "amd64"|"x86_64") RUNNER_ARCH="x64" ;; \
      *) echo "Unsupported architecture: ${TARGETARCH}" && exit 1 ;; \
    esac && \
    echo "Downloading runner version ${RUNNER_VERSION} for ${RUNNER_ARCH}..." && \
    mkdir -p actions-runner && cd actions-runner && \
    curl -O -L "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz" && \
    tar xzf "./actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz" && \
    rm "./actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz" && \
    ./bin/installdependencies.sh && \
    chown -R runner:runner /home/runner

# 7. Install PostgreSQL client (`psql`, used by workflows to seed test data)
# and Google Chrome (needed by lhci autorun's headless browser audits) — both
# ship on GitHub-hosted ubuntu-latest by default; this image needs them added
# explicitly to run those steps natively instead of failing on a missing binary.
# Chrome is amd64-only from Google's own repo (no arm64 build exists), so it's
# skipped on arm64 builds — Playwright-driven jobs still get their own bundled
# Chromium per-job via `playwright install`, this only affects Lighthouse CI.
RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    if [ "${TARGETARCH:-$(dpkg --print-architecture)}" = "amd64" ]; then \
      curl -fsSL https://dl.google.com/linux/linux_signing_key.pub -o /etc/apt/keyrings/google-chrome.asc && \
      chmod a+r /etc/apt/keyrings/google-chrome.asc && \
      echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.asc] http://dl.google.com/linux/chrome/deb/ stable main" | \
        tee /etc/apt/sources.list.d/google-chrome.list > /dev/null && \
      apt-get update && \
      apt-get install -y --no-install-recommends google-chrome-stable && \
      rm -rf /var/lib/apt/lists/*; \
    fi

# 8. Pre-bake Playwright's OS-level dependencies (xvfb, GTK, gstreamer, PulseAudio,
# etc.) so the per-job `playwright install --with-deps` step only has to fetch the
# small browser-binary delta, not apt-get ~50 packages from scratch every run.
# GitHub-hosted ubuntu-latest images ship these system libs pre-baked already —
# without this, jobs on a fresh/cold local runner regularly blow their
# timeout-minutes budget on apt work alone before a single test executes.
# Browsers themselves are intentionally NOT baked here (version-fragile — each
# repo pins its own @playwright/test version); those are still fetched per-job
# and should be cached via actions/cache keyed on the lockfile, same as on
# GitHub-hosted runners.
USER runner
RUN . $NVM_DIR/nvm.sh && \
    npx --yes playwright install-deps chromium webkit firefox
USER root
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /home/runner/actions-runner

COPY start.sh start.sh
RUN chmod +x start.sh && chown runner:runner start.sh

USER runner

ENTRYPOINT ["./start.sh"]
