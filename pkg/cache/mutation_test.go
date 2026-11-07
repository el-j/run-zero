package cache

import (
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestSanitizeScope_KeepsOnlySafeCharacters(t *testing.T) {
	// Every boundary of the allowed ranges, and the characters just outside them.
	if got := SanitizeScope("az AZ 09-_`{@[/:"); got != "az_AZ_09-" {
		t.Fatalf("got %q", got)
	}
}

func TestFormatBytes_UnitBoundaries(t *testing.T) {
	for b, want := range map[int64]string{
		1023:        "1023 B",
		1024:        "1.0 KB",
		1024 * 1024: "1.0 MB",
		1536 * 1024: "1.5 MB",
	} {
		if got := FormatBytes(b); got != want {
			t.Errorf("FormatBytes(%d) = %q, want %q", b, got, want)
		}
	}
}

func writeBytes(t *testing.T, path string, n int) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, make([]byte, n), 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestCalculateStats_CachesNonEmptyResultsFor30Seconds(t *testing.T) {
	dir := t.TempDir()
	InvalidateStatsCache()
	writeBytes(t, filepath.Join(dir, "npm", "a"), 10)
	if got := CalculateStats(dir).TotalBytes; got != 10 {
		t.Fatalf("first scan: %d", got)
	}

	writeBytes(t, filepath.Join(dir, "npm", "b"), 5)
	if got := CalculateStats(dir).TotalBytes; got != 10 {
		t.Fatalf("a repeat scan within 30s must be served from the cache, got %d", got)
	}

	statsMu.Lock()
	lastStatsTime = time.Now().Add(-31 * time.Second)
	statsMu.Unlock()
	if got := CalculateStats(dir).TotalBytes; got != 15 {
		t.Fatalf("an expired cache must rescan, got %d", got)
	}

	other := t.TempDir()
	writeBytes(t, filepath.Join(other, "pip", "a"), 3)
	if got := CalculateStats(other).TotalBytes; got != 3 {
		t.Fatalf("another directory must not use the cache, got %d", got)
	}
}

func TestCalculateStats_DoesNotCacheAnEmptyResult(t *testing.T) {
	dir := t.TempDir()
	InvalidateStatsCache()
	if got := CalculateStats(dir).TotalBytes; got != 0 {
		t.Fatalf("empty dir: %d", got)
	}
	writeBytes(t, filepath.Join(dir, "go", "a"), 7)
	if got := CalculateStats(dir).TotalBytes; got != 7 {
		t.Fatalf("an empty result must not be cached, got %d", got)
	}
}
