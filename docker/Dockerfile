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

# 1. Minimal bootstrap packages needed before the shared provisioning script can
# run (sudo for the runner user; iptables for Docker's own networking needs
# when this container spawns sibling service containers via the host socket).
# Not proxied through apt-cacher-ng -- curl itself isn't installed yet at this
# point, so there's nothing to check reachability with (chicken-and-egg); small
# enough (~few MB) not to matter. Everything downstream of this IS proxied.
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends sudo iptables ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Route apt through the local apt-cacher-ng proxy (docker-compose.yml) if it's
# reachable during the build -- caches .deb packages across rebuilds of this
# image AND the OrbStack VM golden image (both run docker/provision-toolchain.sh).
# host.orb.internal resolves from a `docker build` RUN step under OrbStack;
# harmless no-op (and the build just falls through to the real mirrors) if
# apt-cacher-ng isn't running.
RUN if curl -fsS --connect-timeout 2 "http://host.orb.internal:49503/acng-report.html" >/dev/null 2>&1; then \
      echo 'Acquire::http::Proxy "http://host.orb.internal:49503";' > /etc/apt/apt.conf.d/01runzero-proxy; \
    fi

# 2. Install Docker CLI & Compose Plugin. CLI only, NOT the engine -- this
# container talks to the HOST's docker.sock via a bind mount (docker_driver.py),
# it never runs its own daemon. The OrbStack VM driver's golden base image
# installs the full engine instead, since a VM has no host socket to mount.
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# 3. Create runner user with passwordless sudo access & create tool cache directory
RUN useradd -m -s /bin/bash runner && \
    usermod -aG sudo runner && \
    echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    mkdir -p /opt/hostedtoolcache && \
    chown -R runner:runner /opt/hostedtoolcache

WORKDIR /home/runner

# 4. Shared toolchain provisioning: base OS packages, .NET 8 SDK, PostgreSQL
# client, Google Chrome, Node 20/22/24 + yarn/pnpm via nvm, and Playwright's
# OS-level deps. This is the SAME script src/drivers/orbstack_vm_driver.py runs
# to build its golden OrbStack VM base image -- one source of truth so the two
# execution engines (Docker container vs. VM) can't drift apart on versions.
COPY --chown=runner:runner provision-toolchain.sh /tmp/provision-toolchain.sh
USER runner
RUN chmod +x /tmp/provision-toolchain.sh && \
    /tmp/provision-toolchain.sh "${TARGETARCH:-amd64}"
USER root
RUN rm -f /tmp/provision-toolchain.sh && rm -rf /var/lib/apt/lists/*

# Ensure NVM is auto-loaded for all shells
RUN echo 'export NVM_DIR="/home/runner/.nvm"' >> /etc/profile.d/nvm.sh && \
    echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> /etc/profile.d/nvm.sh && \
    echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> /etc/profile.d/nvm.sh && \
    chmod +x /etc/profile.d/nvm.sh

# 5. Download and extract GitHub Actions runner package based on architecture
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
