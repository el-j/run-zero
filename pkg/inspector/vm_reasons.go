package inspector

import (
	"regexp"
	"strings"
)

// Reasons a job needs a VM instead of a container runner. Container runners
// reach the host's Docker daemon through its socket, so Docker resolves bind
// mounts against the host's filesystem (not the job's workspace), publishes
// ports on the host (not the job's localhost), and the container has no init
// system. Jobs that depend on any of that work in a VM, which runs its own
// Docker daemon.
const (
	ReasonServices      = "services"
	ReasonDockerAction  = "docker-action"
	ReasonDockerRun     = "docker-run"
	ReasonDockerCompose = "docker-compose"
	ReasonKubernetes    = "kubernetes"
	ReasonSystemd       = "systemd"
)

var reasonText = map[string]string{
	ReasonServices:      "its workflow gives it services: or a container:",
	ReasonDockerAction:  "it uses a docker:// action",
	ReasonDockerRun:     "it runs docker with bind mounts, published ports or host networking",
	ReasonDockerCompose: "it starts a docker compose stack",
	ReasonKubernetes:    "it starts a local Kubernetes cluster (kind, minikube or k3d)",
	ReasonSystemd:       "it uses systemd (systemctl)",
}

// DescribeVMReason explains a reason returned by JobVMReason.
func DescribeVMReason(reason string) string {
	if text, ok := reasonText[reason]; ok {
		return text
	}
	return reason
}

// stepRules match a lower-cased line of a job's steps. The first match wins.
var stepRules = []struct {
	reason string
	re     *regexp.Regexp
}{
	{ReasonDockerAction, regexp.MustCompile(`^(-\s*)?uses:\s*['"]?docker://`)},
	{ReasonKubernetes, regexp.MustCompile(`^(-\s*)?uses:\s*['"]?(helm/kind-action|medyagh/setup-minikube|absaoss/k3d-action|nolar/setup-k3d-k3s)@`)},
	{ReasonKubernetes, regexp.MustCompile(`\b(kind\s+create\s+cluster|minikube\s+start|k3d\s+cluster\s+create)\b`)},
	{ReasonDockerCompose, regexp.MustCompile(`\bdocker[\s-]compose\b.*\s(up|run)\b`)},
	{ReasonDockerRun, regexp.MustCompile(`\bdocker\s+(container\s+)?run\b.*(\s(-v|-p)\s|\s--(volume|mount|publish)\b|\s--net(work)?[=\s]host\b)`)},
	{ReasonSystemd, regexp.MustCompile(`\bsystemctl\b`)},
}

// stepVMReason returns the reason a line of a job's steps needs a VM, or "".
func stepVMReason(line string) string {
	lower := strings.ToLower(line)
	for _, rule := range stepRules {
		if rule.re.MatchString(lower) {
			return rule.reason
		}
	}
	return ""
}
