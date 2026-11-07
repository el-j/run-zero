package settings

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/el-j/run-zero/pkg/config"
)

func intp(v int) *int    { return &v }
func boolp(v bool) *bool { return &v }

func TestApply_AcceptsLimitValues(t *testing.T) {
	cases := []SettingsUpdate{
		{MaxRunners: intp(1)},
		{MinRunners: intp(0)},
		{MinRunners: intp(4)}, // equal to MaxRunners
		{PollInterval: intp(1)},
		{PollInterval: intp(3600)},
	}
	for _, u := range cases {
		m := NewManager(&config.Config{MaxRunners: 4}, "")
		if _, err := m.Apply(u); err != nil {
			t.Errorf("%+v: limit value rejected: %v", u, err)
		}
	}
	for _, u := range []SettingsUpdate{{MaxRunners: intp(0)}, {MinRunners: intp(-1)}, {MinRunners: intp(5)}, {PollInterval: intp(0)}, {PollInterval: intp(3601)}} {
		if _, err := NewManager(&config.Config{MaxRunners: 4}, "").Apply(u); err == nil {
			t.Errorf("%+v: out-of-range value accepted", u)
		}
	}
}

func TestApply_TogglesOnlyWhatIsSet(t *testing.T) {
	env := filepath.Join(t.TempDir(), ".env")
	cfg := &config.Config{MaxRunners: 4, AutoRouteVM: true, ProxiesEnabled: true, CacheEnabled: true}
	m := NewManager(cfg, env)

	got, err := m.Apply(SettingsUpdate{AutoRouteVM: boolp(false), ProxiesEnabled: boolp(false), CacheEnabled: boolp(false)})
	if err != nil || got.AutoRouteVM || got.ProxiesEnabled || got.CacheEnabled {
		t.Fatalf("toggles not applied: %+v %v", got, err)
	}
	data, _ := os.ReadFile(env)
	for _, want := range []string{"AUTO_ROUTE_VM=false", "PROXIES_ENABLED=false", "CACHE_ENABLED=false"} {
		if !strings.Contains(string(data), want) {
			t.Errorf(".env missing %s:\n%s", want, data)
		}
	}

	cfg2 := &config.Config{MaxRunners: 4, AutoRouteVM: true, ProxiesEnabled: true, CacheEnabled: true}
	got, _ = NewManager(cfg2, "").Apply(SettingsUpdate{MaxRunners: intp(4)})
	if !got.AutoRouteVM || !got.ProxiesEnabled || !got.CacheEnabled {
		t.Fatalf("unset toggles must not change: %+v", got)
	}
}

func TestApply_EmptyUpdateDoesNotWriteDotEnv(t *testing.T) {
	env := filepath.Join(t.TempDir(), ".env")
	if _, err := NewManager(&config.Config{MaxRunners: 4}, env).Apply(SettingsUpdate{}); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(env); !os.IsNotExist(err) {
		t.Fatal("an empty update must not create or touch .env")
	}
}

func TestUpdateDotEnv_EmptyFileStaysEmpty(t *testing.T) {
	env := filepath.Join(t.TempDir(), ".env")
	if err := UpdateDotEnv(env, map[string]string{}); err != nil {
		t.Fatal(err)
	}
	if data, _ := os.ReadFile(env); len(data) != 0 {
		t.Fatalf("expected an empty file, got %q", data)
	}
}

func TestUpdateDotEnv_FailsWhenTheDirectoryCannotBeCreated(t *testing.T) {
	parent := filepath.Join(t.TempDir(), "file")
	_ = os.WriteFile(parent, nil, 0o644)
	if err := UpdateDotEnv(filepath.Join(parent, "sub", ".env"), map[string]string{"A": "1"}); err == nil {
		t.Fatal("expected an error when the parent is a file")
	}
}
