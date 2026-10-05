package builder

import (
	"fmt"
	"strings"
)

// DockerEngineSnippet generates the shell script to install dockerd with cgroupfs driver.
func DockerEngineSnippet() string {
	return `sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /tmp/docker.asc
sudo install -m 0644 /tmp/docker.asc /etc/apt/keyrings/docker.asc
DOCKER_APT_ARCH=$(dpkg --print-architecture)
DOCKER_APT_CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")
echo "deb [arch=$DOCKER_APT_ARCH signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $DOCKER_APT_CODENAME stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker runner
sudo tee /etc/docker/daemon.json > /dev/null <<'DAEMONJSON'
{
  "exec-opts": ["native.cgroupdriver=cgroupfs"],
  "registry-mirrors": ["http://host.orb.internal:49502"],
  "insecure-registries": ["host.orb.internal:49502"]
}
DAEMONJSON
sudo systemctl enable docker`
}

// RunnerDownloadSnippet generates the download and unpack script for the Actions runner.
func RunnerDownloadSnippet(arch, runnerVersion string) string {
	tarArch := "arm64"
	if arch == "amd64" || arch == "x64" || arch == "x86_64" {
		tarArch = "x64"
	}
	if runnerVersion == "" {
		runnerVersion = DefaultRunnerVersion
	}
	url := fmt.Sprintf("https://github.com/actions/runner/releases/download/v%s/actions-runner-linux-%s-%s.tar.gz",
		runnerVersion, tarArch, runnerVersion)

	return fmt.Sprintf(`mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
curl -fsSL -O %q
tar xzf "./actions-runner-linux-%s-%s.tar.gz"
rm -f "./actions-runner-linux-%s-%s.tar.gz"
sudo ./bin/installdependencies.sh`, url, tarArch, runnerVersion, tarArch, runnerVersion)
}

// FullProvisionScript combines logging, env vars, docker, toolchain, and runner download.
func FullProvisionScript(arch, runnerVersion, customScript string) string {
	var sb strings.Builder
	sb.WriteString("exec > /home/runner/provision.log 2>&1\n")
	sb.WriteString("set -e\n")
	sb.WriteString(fmt.Sprintf("export ARCH=%q\n", arch))
	sb.WriteString(DockerEngineSnippet() + "\n")
	if strings.TrimSpace(customScript) != "" {
		sb.WriteString(customScript + "\n")
	}
	sb.WriteString(RunnerDownloadSnippet(arch, runnerVersion) + "\n")
	sb.WriteString("echo \"Base image provisioning complete.\"\n")
	return sb.String()
}
