package provider

import (
	"context"
	"os"
	"path/filepath"
	"testing"

	"github.com/el-j/run-zero/pkg/state"
)

func TestConfigMalformedJSONAndYAMLTransitions(t *testing.T) {
	dir := t.TempDir()
	bad := filepath.Join(dir, "bad.json")
	if err := os.WriteFile(bad, []byte("{bad"), 0600); err != nil {
		t.Fatal(err)
	}
	if _, err := LoadConfigFile(bad); err == nil {
		t.Fatal("expected JSON parse error")
	}
	yaml := filepath.Join(dir, "inline.yaml")
	content := "ignored: true\n- id: one\n  projects: first/project\n  projects: \n    - second/project\n  unknown: value\n- id: two\n"
	if err := os.WriteFile(yaml, []byte(content), 0600); err != nil {
		t.Fatal(err)
	}
	cfg, err := LoadConfigFile(yaml)
	if err != nil || len(cfg.Providers) != 2 || len(cfg.Providers[0].Projects) != 2 || cfg.Providers[0].Projects[0] != "first/project" || cfg.Providers[0].Projects[1] != "second/project" {
		t.Fatalf("config=%+v err=%v", cfg, err)
	}
}

func TestManagerEmptyAndMergeDuplicates(t *testing.T) {
	m := NewManager()
	if runners, errs := m.FetchAllRemoteRunners(context.Background()); runners != nil || errs != nil {
		t.Fatalf("empty results=%v errors=%v", runners, errs)
	}
	local := []state.RunnerInfo{{ID: "id", Name: "local"}}
	remote := []state.RunnerInfo{{ID: "other", Name: "local"}, {ID: "id", Name: "duplicate id"}, {ID: "new", Name: "new"}}
	got := MergeRunners(local, remote)
	if len(got) != 2 || got[0].Origin == nil || *got[0].Origin != "local" || got[1].Name != "new" {
		t.Fatalf("merged=%+v", got)
	}
}
