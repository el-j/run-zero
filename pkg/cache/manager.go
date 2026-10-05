package cache

import (
	"os"
	"path/filepath"
	"strings"
)

const (
	PnpmStorePath          = "/home/runner/.local/share/pnpm/store"
	PlaywrightBrowsersPath = "/home/runner/.cache/ms-playwright"
	ToolCachePath          = "/opt/hostedtoolcache"
)

// SanitizeScope cleans scope strings for safe directory naming.
func SanitizeScope(scope string) string {
	var b strings.Builder
	for _, r := range scope {
		if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '-' || r == '_' {
			b.WriteRune(r)
		} else {
			b.WriteRune('_')
		}
	}
	return strings.Trim(b.String(), "_")
}

func makeArchDir(hostCacheDir, name, arch string) string {
	path := filepath.Join(hostCacheDir, name, arch)
	_ = os.MkdirAll(path, 0777)
	_ = os.Chmod(filepath.Dir(path), 0777)
	_ = os.Chmod(path, 0777)
	return path
}

// InitCacheDirs creates host cache directories and returns host-path -> runner-path mount mappings.
func InitCacheDirs(hostCacheDir, arch string, cacheEnabled bool, scope string) map[string]string {
	if !cacheEnabled || strings.TrimSpace(hostCacheDir) == "" {
		return map[string]string{}
	}

	subdirs := []string{"npm", "pnpm", "yarn", "pip", "uv", "go-pkg", "dotnet", "rust", "hostedtoolcache"}
	for _, sub := range subdirs {
		p := filepath.Join(hostCacheDir, sub)
		_ = os.MkdirAll(p, 0777)
		_ = os.Chmod(p, 0777)
	}

	archToolcache := makeArchDir(hostCacheDir, "hostedtoolcache", arch)
	archPlaywright := makeArchDir(hostCacheDir, "ms-playwright", arch)

	var goBuildDir string
	if scope != "" {
		safeScope := SanitizeScope(scope)
		goBuildDir = filepath.Join(hostCacheDir, "build-cache", safeScope, "go-build")
	} else {
		goBuildDir = filepath.Join(hostCacheDir, "go-build")
	}
	_ = os.MkdirAll(goBuildDir, 0777)
	_ = os.Chmod(goBuildDir, 0777)

	return map[string]string{
		filepath.Join(hostCacheDir, "npm"):    "/home/runner/.npm",
		filepath.Join(hostCacheDir, "pnpm"):   PnpmStorePath,
		filepath.Join(hostCacheDir, "yarn"):   "/home/runner/.cache/yarn",
		filepath.Join(hostCacheDir, "pip"):    "/home/runner/.cache/pip",
		filepath.Join(hostCacheDir, "uv"):     "/home/runner/.cache/uv",
		filepath.Join(hostCacheDir, "go-pkg"): "/home/runner/go/pkg",
		goBuildDir:                            "/home/runner/.cache/go-build",
		filepath.Join(hostCacheDir, "dotnet"): "/home/runner/.nuget/packages",
		filepath.Join(hostCacheDir, "rust"):   "/home/runner/.cargo/registry",
		archToolcache:                         ToolCachePath,
		archPlaywright:                        PlaywrightBrowsersPath,
	}
}
