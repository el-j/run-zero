package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadDotEnvFile_EmptyQuotedValue(t *testing.T) {
	path := filepath.Join(t.TempDir(), ".env")
	_ = os.WriteFile(path, []byte("A=\"\"\nB='x'\nC=\"\n"), 0o644)
	env, err := LoadDotEnvFile(path)
	if err != nil || env["A"] != "" || env["B"] != "x" || env["C"] != `"` {
		t.Fatalf("got %v, err %v", env, err)
	}
}

func TestParseInt_ValuesAndLimits(t *testing.T) {
	max := 10
	for raw, want := range map[string]int{"5": 5, "1": 1, "10": 10} {
		if got, err := parseInt(MapEnv{"N": raw}, "N", 3, 1, &max); err != nil || got != want {
			t.Errorf("%q: got %d, err %v", raw, got, err)
		}
	}
	for _, raw := range []string{"0", "11", "x"} {
		if _, err := parseInt(MapEnv{"N": raw}, "N", 3, 1, &max); err == nil {
			t.Errorf("%q must be rejected", raw)
		}
	}
}

func TestLoadConfig_MinRunnersMayEqualMaxRunners(t *testing.T) {
	if _, err := LoadConfig(MapEnv{"MIN_RUNNERS": "4", "MAX_RUNNERS": "4"}); err != nil {
		t.Fatalf("MIN_RUNNERS == MAX_RUNNERS must be valid: %v", err)
	}
}
