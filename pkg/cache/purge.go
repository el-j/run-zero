package cache

import (
	"os"
	"path/filepath"
	"strings"
)

// Purge removes cached files based on category, repo scope, or entire host cache directory.
func Purge(hostCacheDir string, category, repo string, all bool) error {
	if strings.TrimSpace(hostCacheDir) == "" {
		return nil
	}

	if all {
		entries, err := os.ReadDir(hostCacheDir)
		if err != nil {
			return err
		}
		for _, e := range entries {
			_ = os.RemoveAll(filepath.Join(hostCacheDir, e.Name()))
		}
		return nil
	}

	if category != "" {
		target := filepath.Join(hostCacheDir, category)
		return os.RemoveAll(target)
	}

	if repo != "" {
		safeRepo := SanitizeScope(repo)
		target := filepath.Join(hostCacheDir, "build-cache", safeRepo)
		return os.RemoveAll(target)
	}

	return nil
}
