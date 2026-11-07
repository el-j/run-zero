package driver

import (
	"fmt"
	"regexp"
	"sort"
	"strings"
)

// envName matches a valid shell variable name.
var envName = regexp.MustCompile(`^[A-Za-z_][A-Za-z0-9_]*$`)

// RunnerVersion is the GitHub Actions runner release installed in stock VM
// guests (Multipass, WSL2); keep it in step with docker/Dockerfile.
const RunnerVersion = "2.337.0"

// guestScript describes the bootstrap of a stock Ubuntu guest that has no
// pre-baked runner (unlike OrbStack's golden image).
type guestScript struct {
	Name string // runner name to register
	Home string // directory holding actions-runner and the setup log
	Spec RunnerSpec
	// Finish runs after the runner's single job, e.g. power the VM off so the
	// prune pass removes it.
	Finish string
	// HostIPCmd prints the host's address as seen from the guest.
	HostIPCmd string
}

// script returns the whole bootstrap: install dependencies, download and
// register an ephemeral runner, run one job, then Finish. Every
// caller-supplied value is shell-quoted.
func (g guestScript) script() string {
	runnerArch := "arm64"
	if normalizeArch(g.Spec.Arch) == "amd64" {
		runnerArch = "x64"
	}
	tarball := fmt.Sprintf("actions-runner-linux-%s-%s.tar.gz", runnerArch, RunnerVersion)
	var b strings.Builder
	fmt.Fprintf(&b, "set -e\nexport DEBIAN_FRONTEND=noninteractive\n")
	if g.Spec.Proxies {
		b.WriteString(g.proxyEnv())
	}
	keys := make([]string, 0, len(g.Spec.Env))
	for k := range g.Spec.Env {
		if envName.MatchString(k) {
			keys = append(keys, k)
		}
	}
	sort.Strings(keys)
	for _, k := range keys {
		fmt.Fprintf(&b, "export %s=%s\n", k, shellQuote(g.Spec.Env[k]))
	}
	fmt.Fprintf(&b, `sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p %[1]s/actions-runner && cd %[1]s/actions-runner
curl -fsSL -O %[2]s
tar xzf %[3]s && rm %[3]s
sudo ./bin/installdependencies.sh
./config.sh --unattended --ephemeral --replace --url %[4]s --token %[5]s --name %[6]s --labels %[7]s --work _work
timeout 6h ./run.sh || true
%[8]s
`,
		shellQuote(g.Home),
		shellQuote(fmt.Sprintf("https://github.com/actions/runner/releases/download/v%s/%s", RunnerVersion, tarball)),
		shellQuote(tarball),
		shellQuote("https://github.com/"+g.Spec.Repo),
		shellQuote(g.Spec.Token),
		shellQuote(g.Name),
		shellQuote(runnerLabels(g.Spec)),
		g.Finish)
	return b.String()
}

// proxyEnv points package managers at the host's caching proxies.
func (g guestScript) proxyEnv() string {
	return fmt.Sprintf(`HOST_IP=$(%s)
export npm_config_registry="http://${HOST_IP}:49501/"
export YARN_REGISTRY="http://${HOST_IP}:49501/"
export GOPROXY="http://${HOST_IP}:49500,https://proxy.golang.org,direct"
export PIP_INDEX_URL="http://${HOST_IP}:49507/root/pypi/+simple/"
export UV_INDEX_URL="${PIP_INDEX_URL}"
export PIP_TRUSTED_HOST="${HOST_IP}"
echo "Acquire::http::Proxy \"http://${HOST_IP}:49503\";" | sudo tee /etc/apt/apt.conf.d/01runzero-proxy >/dev/null
mkdir -p "$HOME/.cargo"
printf '[source.crates-io]\nreplace-with = "kellnr-proxy"\n\n[source.kellnr-proxy]\nregistry = "sparse+http://%%s:49506/api/v1/cratesio/"\n' "$HOST_IP" > "$HOME/.cargo/config.toml"
`, g.HostIPCmd)
}

// detached wraps the bootstrap so it survives the CLI session that starts it
// and the caller returns at once (the bootstrap installs packages and runs a
// whole job). Output goes to <Home>/runzero-setup.log.
func (g guestScript) detached() string {
	return fmt.Sprintf("mkdir -p %[1]s && setsid nohup bash -c %[2]s > %[1]s/runzero-setup.log 2>&1 < /dev/null &",
		shellQuote(g.Home), shellQuote(g.script()))
}
