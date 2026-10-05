package settings

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/el-j/run-zero/pkg/config"
)

func TestSettingsManager_LifecycleAndApply(t *testing.T) {
	tmpDir, err := os.MkdirTemp("", "runzero-settings-*")
	if err != nil {
		t.Fatalf("failed temp dir: %v", err)
	}
	defer os.RemoveAll(tmpDir)

	envPath := filepath.Join(tmpDir, ".env")
	initialContent := "# System configuration\nMAX_RUNNERS=4\nPOLL_INTERVAL=10\n"
	_ = os.WriteFile(envPath, []byte(initialContent), 0644)

	cfg := &config.Config{
		MaxRunners:   4,
		MinRunners:   1,
		PollInterval: 10,
	}

	mgr := NewManager(cfg, envPath)
	if mgr.Get().MaxRunners != 4 {
		t.Fatalf("expected 4 max runners")
	}

	notified := false
	mgr.Subscribe(func(newCfg *config.Config) {
		if newCfg.MaxRunners == 8 {
			notified = true
		}
	})

	newMax := 8
	newMin := 2
	newPoll := 15
	trueVal := true

	updated, err := mgr.Apply(SettingsUpdate{
		MaxRunners:     &newMax,
		MinRunners:     &newMin,
		PollInterval:   &newPoll,
		AutoDiscover:   &trueVal,
		AutoRouteVM:    &trueVal,
		ProxiesEnabled: &trueVal,
		CacheEnabled:   &trueVal,
	})
	if err != nil {
		t.Fatalf("unexpected apply error: %v", err)
	}
	if updated.MaxRunners != 8 || updated.MinRunners != 2 || updated.PollInterval != 15 {
		t.Errorf("unexpected updated values: %+v", updated)
	}
	if !notified {
		t.Errorf("expected subscriber to be notified")
	}

	// Verify .env file updated
	data, _ := os.ReadFile(envPath)
	content := string(data)
	if !strings.Contains(content, "MAX_RUNNERS=8") || !strings.Contains(content, "POLL_INTERVAL=15") {
		t.Errorf("expected updated values in .env: %s", content)
	}
	if !strings.Contains(content, "AUTO_DISCOVER_REPOS=true") {
		t.Errorf("expected new key appended to .env: %s", content)
	}
}

func TestSettingsManager_ValidationErrors(t *testing.T) {
	cfg := &config.Config{MaxRunners: 4, MinRunners: 1}
	mgr := NewManager(cfg, "")

	badMax := 0
	if _, err := mgr.Apply(SettingsUpdate{MaxRunners: &badMax}); err == nil {
		t.Error("expected error for max_runners < 1")
	}

	badMinNeg := -1
	if _, err := mgr.Apply(SettingsUpdate{MinRunners: &badMinNeg}); err == nil {
		t.Error("expected error for min_runners < 0")
	}

	badMinExceed := 10
	if _, err := mgr.Apply(SettingsUpdate{MinRunners: &badMinExceed}); err == nil {
		t.Error("expected error for min_runners > max_runners")
	}

	badPollLow := 0
	if _, err := mgr.Apply(SettingsUpdate{PollInterval: &badPollLow}); err == nil {
		t.Error("expected error for poll_interval < 1")
	}
}

func TestUpdateDotEnv_Empty(t *testing.T) {
	if err := UpdateDotEnv("", nil); err != nil {
		t.Errorf("expected nil on empty path")
	}
}
