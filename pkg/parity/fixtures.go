package parity

// BaselineScenarios returns canonical end-to-end test scenarios.
func BaselineScenarios() []TestCase {
	return []TestCase{
		{
			Name: "standard-docker-job",
			Repo: "el-j/run-zero",
			WorkflowYAML: `name: CI
jobs:
  test:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - run: npm test`,
			JobName:          "test",
			JobLabels:        []string{"self-hosted"},
			HostArch:         "arm64",
			ArchOverride:     "off",
			CapacityCPUs:     10,
			CapacityMemoryMB: 16384,
			MaxRunners:       2,
			Expected: Decision{
				Backend:      "docker",
				Arch:         "arm64",
				RequiresVM:   false,
				TriggerMatch: "",
				CPUs:         "4",
				MemoryMB:     7168,
			},
		},
		{
			Name: "service-container-routed-to-vm",
			Repo: "el-j/backend",
			WorkflowYAML: `name: Integration
jobs:
  integration:
    runs-on: self-hosted
    services:
      redis:
        image: redis:7
    steps:
      - run: make integration`,
			JobName:          "integration",
			JobLabels:        []string{"self-hosted"},
			HostArch:         "arm64",
			ArchOverride:     "off",
			CapacityCPUs:     8,
			CapacityMemoryMB: 8192,
			MaxRunners:       2,
			Expected: Decision{
				Backend:      "orbstack-vm",
				Arch:         "arm64",
				RequiresVM:   true,
				TriggerMatch: "services:",
				CPUs:         "3",
				MemoryMB:     3072,
			},
		},
		{
			Name: "native-arch-override-rosetta",
			Repo: "el-j/run-zero",
			WorkflowYAML: `name: Frontend
jobs:
  build:
    runs-on: [self-hosted, amd64]
    steps:
      - run: npm run build`,
			JobName:          "build",
			JobLabels:        []string{"self-hosted", "amd64"},
			HostArch:         "arm64",
			ArchOverride:     "all",
			CapacityCPUs:     8,
			CapacityMemoryMB: 8192,
			MaxRunners:       1,
			Expected: Decision{
				Backend:      "docker",
				Arch:         "arm64",
				RequiresVM:   false,
				TriggerMatch: "",
				CPUs:         "7",
				MemoryMB:     6144,
			},
		},
		{
			Name: "explicit-rosetta-emulation-preserved",
			Repo: "el-j/run-zero",
			WorkflowYAML: `name: Native C++ Build
jobs:
  compile:
    runs-on: [self-hosted, amd64, rosetta]
    steps:
      - run: make x86`,
			JobName:          "compile",
			JobLabels:        []string{"self-hosted", "amd64", "rosetta"},
			HostArch:         "arm64",
			ArchOverride:     "all",
			CapacityCPUs:     8,
			CapacityMemoryMB: 8192,
			MaxRunners:       1,
			Expected: Decision{
				Backend:      "docker",
				Arch:         "amd64",
				RequiresVM:   false,
				TriggerMatch: "",
				CPUs:         "7",
				MemoryMB:     6144,
			},
		},
	}
}
