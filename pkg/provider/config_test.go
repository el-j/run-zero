package provider

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadConfigFile_YAML(t *testing.T) {
	tmpDir := t.TempDir()
	yamlPath := filepath.Join(tmpDir, "providers.yaml")

	yamlContent := `
# Multi-platform provider configuration
providers:
  - id: gitlab-eckelmann
    type: gitlab
    name: "Eckelmann On-Premise GitLab"
    url: https://git.eckelmann.de
    token: glpat-secret123
    group: rex-at
    projects:
      - rex-at/web/rex-working-time-tool
      - rex-at/embedded/controller
  - id: gitlab-saas
    type: gitlab
    name: "GitLab.com SaaS"
    url: https://gitlab.com
    token: glpat-saas456
    group: my-cloud-org
  - id: github-org
    type: github
    owner: el-j
    org: my-org
    token: ghp_token789
`
	if err := os.WriteFile(yamlPath, []byte(yamlContent), 0644); err != nil {
		t.Fatalf("failed writing test yaml: %v", err)
	}

	cfg, err := LoadConfigFile(yamlPath)
	if err != nil {
		t.Fatalf("unexpected error loading yaml: %v", err)
	}

	if len(cfg.Providers) != 3 {
		t.Fatalf("expected 3 providers, got %d", len(cfg.Providers))
	}

	p1 := cfg.Providers[0]
	if p1.ID != "gitlab-eckelmann" || p1.Type != "gitlab" || p1.URL != "https://git.eckelmann.de" {
		t.Errorf("unexpected p1: %+v", p1)
	}
	if len(p1.Projects) != 2 || p1.Projects[0] != "rex-at/web/rex-working-time-tool" {
		t.Errorf("unexpected p1 projects: %v", p1.Projects)
	}

	p2 := cfg.Providers[1]
	if p2.ID != "gitlab-saas" || p2.Group != "my-cloud-org" {
		t.Errorf("unexpected p2: %+v", p2)
	}

	p3 := cfg.Providers[2]
	if p3.ID != "github-org" || p3.Owner != "el-j" {
		t.Errorf("unexpected p3: %+v", p3)
	}
}

func TestLoadConfigFile_JSON(t *testing.T) {
	tmpDir := t.TempDir()
	jsonPath := filepath.Join(tmpDir, "providers.json")

	jsonContent := `{
		"providers": [
			{
				"id": "gitlab-test",
				"type": "gitlab",
				"url": "https://gitlab.example.com",
				"token": "tok123",
				"group": "group1",
				"projects": ["proj1"]
			}
		]
	}`

	if err := os.WriteFile(jsonPath, []byte(jsonContent), 0644); err != nil {
		t.Fatalf("failed writing test json: %v", err)
	}

	cfg, err := LoadConfigFile(jsonPath)
	if err != nil {
		t.Fatalf("unexpected error loading json: %v", err)
	}

	if len(cfg.Providers) != 1 || cfg.Providers[0].ID != "gitlab-test" {
		t.Errorf("unexpected parsed json: %+v", cfg)
	}
}

func TestLoadConfigFile_NotFound(t *testing.T) {
	_, err := LoadConfigFile("/non/existent/path/providers.yaml")
	if err == nil {
		t.Errorf("expected error for non-existent file")
	}
}
