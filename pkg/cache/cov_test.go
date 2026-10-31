package cache

import (
	"os"
	"path/filepath"
	"testing"
)

func TestCoverageGaps(t *testing.T) {
	dir := t.TempDir()
	m := InitCacheDirs(dir, "arm64", true, "")
	if _, ok := m[filepath.Join(dir, "go-build")]; !ok {
		t.Errorf("expected unscoped go-build mount: %v", m)
	}

	if got := FormatBytes(5 * 1024 * 1024); got != "5.0 MB" {
		t.Errorf("got %s", got)
	}

	if s := CalculateStats(""); s.TotalHuman != "0 B" {
		t.Errorf("empty dir stats %v", s)
	}
	InvalidateStatsCache()
	if s := CalculateStats(filepath.Join(dir, "missing")); s.TotalBytes != 0 {
		t.Errorf("missing dir stats %v", s)
	}

	stats := t.TempDir()
	_ = os.WriteFile(filepath.Join(stats, "file.txt"), []byte("x"), 0o644)
	_ = os.MkdirAll(filepath.Join(stats, "cat"), 0o755)
	_ = os.WriteFile(filepath.Join(stats, "cat", "a"), []byte("hello"), 0o644)
	InvalidateStatsCache()
	first := CalculateStats(stats)
	second := CalculateStats(stats)
	if first.TotalBytes != 5 || second.TotalBytes != 5 || len(second.Categories) != 1 {
		t.Errorf("stats %v %v", first, second)
	}
	InvalidateStatsCache()
}

func TestPurgeGaps(t *testing.T) {
	if err := Purge(filepath.Join(t.TempDir(), "missing"), "", "", true); err == nil {
		t.Error("expected ReadDir error")
	}
	dir := t.TempDir()
	if err := Purge(dir, "", "", false); err != nil {
		t.Error(err)
	}
}
