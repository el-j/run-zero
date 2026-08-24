FROM ubuntu:22.04

ARG RUNNER_VERSION="2.336.0"
ARG TARGETARCH

# Prevents debconf from prompting during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV RUNNER_TOOL_CACHE=/opt/hostedtoolcache

# Update system and install base dependencies
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    jq \
    git \
    tar \
    unzip \
    zip \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    sudo \
    iptables \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI so workflows can use docker when socket is mounted
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# Create runner user with passwordless sudo access & create tool cache directory
RUN useradd -m -s /bin/bash runner && \
    usermod -aG sudo runner && \
    echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    mkdir -p /opt/hostedtoolcache && \
    chown -R runner:runner /opt/hostedtoolcache

WORKDIR /home/runner

# Download and extract GitHub Actions runner package based on architecture
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

WORKDIR /home/runner/actions-runner

COPY start.sh start.sh
RUN chmod +x start.sh && chown runner:runner start.sh

USER runner

ENTRYPOINT ["./start.sh"]
