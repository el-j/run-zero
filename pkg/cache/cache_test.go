package cache

import (
	"os"
	"path/filepath"
	"testing"
)

func TestCache_InitDirsAndMounts(t *testing.T) {
	tmpDir, err := os.MkdirTemp("", "runzero-cache-*")
	if err != nil {
		t.Fatalf("failed temp dir: %v", err)
	}
	defer os.RemoveAll(tmpDir)

	mounts := InitCacheDirs(tmpDir, "arm64", true, "my-org/my-repo")
	if len(mounts) == 0 {
		t.Fatalf("expected non-empty mounts")
	}

	if mounts[filepath.Join(tmpDir, "pnpm")] != PnpmStorePath {
		t.Errorf("expected pnpm mount mapping")
	}
	if mounts[filepath.Join(tmpDir, "hostedtoolcache", "arm64")] != ToolCachePath {
		t.Errorf("expected hostedtoolcache arm64 mount")
	}

	scopedBuildDir := filepath.Join(tmpDir, "build-cache", "my-org_my-repo", "go-build")
	if mounts[scopedBuildDir] != "/home/runner/.cache/go-build" {
		t.Errorf("expected scoped go-build mount mapping: %s not in mounts", scopedBuildDir)
	}

	// Disabled or empty
	if len(InitCacheDirs("", "arm64", true, "")) != 0 {
		t.Errorf("expected empty mounts for empty dir")
	}
	if len(InitCacheDirs(tmpDir, "arm64", false, "")) != 0 {
		t.Errorf("expected empty mounts for disabled cache")
	}
}

func TestCache_StatsAndFormatBytes(t *testing.T) {
	if FormatBytes(500) != "500 B" {
		t.Errorf("expected 500 B, got %s", FormatBytes(500))
	}
	if FormatBytes(1024) != "1.0 KB" {
		t.Errorf("expected 1.0 KB, got %s", FormatBytes(1024))
	}

	tmpDir, err := os.MkdirTemp("", "runzero-cache-stats-*")
	if err != nil {
		t.Fatalf("failed temp dir: %v", err)
	}
	defer os.RemoveAll(tmpDir)

	sub := filepath.Join(tmpDir, "npm")
	_ = os.MkdirAll(sub, 0755)
	_ = os.WriteFile(filepath.Join(sub, "pkg.tgz"), make([]byte, 2048), 0644)

	stats := CalculateStats(tmpDir)
	if stats.TotalBytes != 2048 || len(stats.Categories) != 1 {
		t.Fatalf("unexpected stats: %+v", stats)
	}
	if stats.Categories[0].Category != "npm" || stats.Categories[0].Bytes != 2048 {
		t.Errorf("unexpected category usage: %+v", stats.Categories[0])
	}

	// Empty dir stats
	emptyStats := CalculateStats("")
	if emptyStats.TotalBytes != 0 {
		t.Errorf("expected 0 bytes for empty dir")
	}
}

func TestCache_Purge(t *testing.T) {
	tmpDir, err := os.MkdirTemp("", "runzero-purge-*")
	if err != nil {
		t.Fatalf("failed temp dir: %v", err)
	}
	defer os.RemoveAll(tmpDir)

	npmDir := filepath.Join(tmpDir, "npm")
	_ = os.MkdirAll(npmDir, 0755)
	_ = os.WriteFile(filepath.Join(npmDir, "file.txt"), []byte("123"), 0644)

	repoDir := filepath.Join(tmpDir, "build-cache", "org_repo")
	_ = os.MkdirAll(repoDir, 0755)
	_ = os.WriteFile(filepath.Join(repoDir, "file.txt"), []byte("123"), 0644)

	// Purge category
	if err := Purge(tmpDir, "npm", "", false); err != nil {
		t.Fatalf("unexpected purge error: %v", err)
	}
	if _, err := os.Stat(npmDir); !os.IsNotExist(err) {
		t.Errorf("expected npmDir to be removed")
	}

	// Purge repo
	if err := Purge(tmpDir, "", "org/repo", false); err != nil {
		t.Fatalf("unexpected purge error: %v", err)
	}
	if _, err := os.Stat(repoDir); !os.IsNotExist(err) {
		t.Errorf("expected repoDir to be removed")
	}

	// Purge all
	subDir := filepath.Join(tmpDir, "pip")
	_ = os.MkdirAll(subDir, 0755)
	if err := Purge(tmpDir, "", "", true); err != nil {
		t.Fatalf("unexpected purge all: %v", err)
	}
	entries, _ := os.ReadDir(tmpDir)
	if len(entries) != 0 {
		t.Errorf("expected 0 entries after purge all, got %d", len(entries))
	}

	// Empty path
	if err := Purge("", "", "", true); err != nil {
		t.Errorf("expected nil error on empty dir")
	}
}
