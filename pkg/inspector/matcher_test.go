package inspector

import (
	"testing"
)

func TestJobVMReason_FindsJobs(t *testing.T) {
	yamlContent := `
jobs:
  unit:
    name: "Unit Tests"
    steps: []
  e2e:
    name: "E2E Tests"
    services:
      redis:
        image: redis
`
	for _, c := range []struct {
		target, reason string
		found          bool
	}{
		{"Unit Tests", "", true},
		{"e2e", ReasonServices, true},
		{"E2E Tests (shard-1, shard-2)", ReasonServices, true},
		{"Non Existent", "", false},
		{"", "", false},
		{"  ", "", false},
	} {
		if reason, found := JobVMReason(yamlContent, c.target); reason != c.reason || found != c.found {
			t.Errorf("%q: got %q/%v, want %q/%v", c.target, reason, found, c.reason, c.found)
		}
	}
	if _, found := JobVMReason("", "test"); found {
		t.Error("an empty workflow has no jobs")
	}
	if _, found := JobVMReason("name: test", "test"); found {
		t.Error("a workflow without jobs: has no jobs")
	}
}

func TestJobVMReason_Steps(t *testing.T) {
	job := func(steps string) string {
		return "jobs:\n  build:\n    runs-on: self-hosted\n    steps:\n" + steps
	}
	for _, c := range []struct{ name, steps, want string }{
		{"plain build", "      - uses: actions/checkout@v4\n      - run: npm test\n      - run: docker build -t app .\n      - run: docker run --rm app npm test\n", ""},
		{"docker action", "      - uses: docker://alpine:3.20\n", ReasonDockerAction},
		{"quoted docker action", "      - name: x\n        uses: 'docker://alpine'\n", ReasonDockerAction},
		{"kind action", "      - uses: helm/kind-action@v1\n", ReasonKubernetes},
		{"k3d action", "      - uses: AbsaOSS/k3d-action@v2\n", ReasonKubernetes},
		{"kind cli", "      - run: kind create cluster --wait 60s\n", ReasonKubernetes},
		{"minikube", "      - run: |\n          minikube start\n", ReasonKubernetes},
		{"compose up", "      - run: docker compose up -d\n", ReasonDockerCompose},
		{"legacy compose run", "      - run: docker-compose -f ci.yml run tests\n", ReasonDockerCompose},
		{"compose build only", "      - run: docker compose build\n", ""},
		{"bind mount", "      - run: docker run --rm -v $PWD:/src app\n", ReasonDockerRun},
		{"published port", "      - run: docker run -d -p 5432:5432 postgres\n", ReasonDockerRun},
		{"volume flag", "      - run: docker container run --volume=x:/y app\n", ReasonDockerRun},
		{"mount flag", "      - run: docker run --mount type=bind,src=.,dst=/s app\n", ReasonDockerRun},
		{"host network", "      - run: docker run --network host app\n", ReasonDockerRun},
		{"host net", "      - run: docker run --net=host app\n", ReasonDockerRun},
		{"systemd", "      - run: sudo systemctl start postgresql\n", ReasonSystemd},
		{"commented out", "      # - run: sudo systemctl start postgresql\n", ""},
	} {
		if got, _ := JobVMReason(job(c.steps), "build"); got != c.want {
			t.Errorf("%s: got %q, want %q", c.name, got, c.want)
		}
	}
}

func TestJobVMReason_ServicesWinOverSteps(t *testing.T) {
	wf := "jobs:\n  it:\n    steps:\n      - run: sudo systemctl start x\n    services:\n      db:\n        image: postgres\n"
	if got, _ := JobVMReason(wf, "it"); got != ReasonServices {
		t.Fatalf("got %q", got)
	}
}

func TestJobVMReason_OnlyItsOwnSteps(t *testing.T) {
	wf := "jobs:\n  a:\n    steps:\n      - run: npm test\n  b:\n    steps:\n      - run: sudo systemctl start x\n"
	if got, _ := JobVMReason(wf, "a"); got != "" {
		t.Fatalf("job a must not inherit job b's needs, got %q", got)
	}
}

func TestDescribeVMReason(t *testing.T) {
	for _, r := range []string{ReasonServices, ReasonDockerAction, ReasonDockerRun, ReasonDockerCompose, ReasonKubernetes, ReasonSystemd} {
		if DescribeVMReason(r) == r {
			t.Errorf("%s has no description", r)
		}
	}
	if DescribeVMReason("label:vm") != "label:vm" {
		t.Error("an unknown reason is returned as is")
	}
}
