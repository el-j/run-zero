// Package traceability checks that TRACEABILITY.md and the README's
// configuration table stay in step with the code they describe.
package traceability

import (
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"testing"
)

const repoRoot = "../.."

var (
	// A cited repo path: a backticked path under one of the source roots, or a
	// top-level file such as `docker-compose.yml`.
	citedPath = regexp.MustCompile("`((?:pkg|cmd|web|website|spec|docker|test|scripts)/[^`*\\s]+|[A-Za-z0-9_.-]+\\.(?:yml|yaml|md))`")
	// An environment variable name passed as a string literal in pkg/config.
	envLiteral = regexp.MustCompile(`"([A-Z][A-Z0-9_]{2,})"`)
	// A row of the README's configuration table.
	readmeRow = regexp.MustCompile("(?m)^\\| `([A-Z][A-Z0-9_]+)` \\|")
)

func read(t *testing.T, rel string) string {
	t.Helper()
	data, err := os.ReadFile(filepath.Join(repoRoot, rel))
	if err != nil {
		t.Fatalf("read %s: %v", rel, err)
	}
	return string(data)
}

// TestMatrixPathsExist fails when TRACEABILITY.md cites code, tests or docs
// that were moved or deleted.
func TestMatrixPathsExist(t *testing.T) {
	matrix := read(t, "TRACEABILITY.md")
	cited := citedPath.FindAllStringSubmatch(matrix, -1)
	if len(cited) < 50 {
		t.Fatalf("found only %d cited paths in TRACEABILITY.md; did the format change?", len(cited))
	}
	for _, m := range cited {
		if _, err := os.Stat(filepath.Join(repoRoot, m[1])); err != nil {
			t.Errorf("TRACEABILITY.md cites %s, which does not exist", m[1])
		}
	}
}

// configVars returns the environment variables the daemon reads in pkg/config.
func configVars(t *testing.T) []string {
	t.Helper()
	seen := map[string]bool{}
	for _, f := range []string{"pkg/config/config.go", "pkg/config/loader.go"} {
		for _, m := range envLiteral.FindAllStringSubmatch(read(t, f), -1) {
			seen[m[1]] = true
		}
	}
	vars := make([]string, 0, len(seen))
	for v := range seen {
		vars = append(vars, v)
	}
	sort.Strings(vars)
	return vars
}

// TestConfigVarsDocumented fails when the daemon reads a setting the README's
// configuration table does not list, or the table lists one nothing reads.
func TestConfigVarsDocumented(t *testing.T) {
	vars := configVars(t)
	if len(vars) < 30 {
		t.Fatalf("found only %d settings in pkg/config; did the loader change?", len(vars))
	}

	documented := map[string]bool{}
	for _, m := range readmeRow.FindAllStringSubmatch(read(t, "README.md"), -1) {
		documented[m[1]] = true
	}
	inConfig := map[string]bool{}
	for _, v := range vars {
		inConfig[v] = true
		if !documented[v] {
			t.Errorf("pkg/config reads %s, but README.md's configuration table does not list it", v)
		}
	}
	for v := range documented {
		if !inConfig[v] {
			t.Errorf("README.md's configuration table lists %s, but pkg/config never reads it", v)
		}
	}
}
