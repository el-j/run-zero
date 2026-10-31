package api

import (
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"testing"
)

var (
	tspRoute  = regexp.MustCompile(`@route\("([^"]+)"\)`)
	yamlPath  = regexp.MustCompile(`(?m)^  (/[^:\s]*):\s*$`)
	specRoot  = filepath.Join("..", "..", "spec")
	openapiFn = filepath.Join(specRoot, "tsp-output", "@typespec", "openapi3", "openapi.yaml")
)

// tspPaths composes the served paths declared in spec/main.tsp: the namespace
// @route prefix joined with each operation's @route.
func tspPaths(t *testing.T) map[string]bool {
	t.Helper()
	src, err := os.ReadFile(filepath.Join(specRoot, "main.tsp"))
	if err != nil {
		t.Fatalf("read spec: %v", err)
	}
	paths := map[string]bool{}
	prefix := ""
	for _, m := range tspRoute.FindAllStringSubmatch(string(src), -1) {
		if prefix == "" {
			prefix = m[1]
			continue
		}
		paths[prefix+m[1]] = true
	}
	return paths
}

// openapiPaths returns the paths of the generated OpenAPI document, or nil
// when the (gitignored) spec output has not been generated.
func openapiPaths(t *testing.T) map[string]bool {
	t.Helper()
	data, err := os.ReadFile(openapiFn)
	if err != nil {
		return nil
	}
	paths := map[string]bool{}
	for _, m := range yamlPath.FindAllStringSubmatch(string(data), -1) {
		paths[m[1]] = true
	}
	return paths
}

func specHas(paths map[string]bool, route string) bool {
	if paths[route] {
		return true
	}
	// A subtree pattern such as "/api/images/build/" is documented as "/api/images/build/{id}".
	if strings.HasSuffix(route, "/") {
		for p := range paths {
			if strings.HasPrefix(p, route) {
				return true
			}
		}
	}
	return false
}

// TestRoutesAreInSpec fails when the server serves an /api route that the
// TypeSpec (and its generated OpenAPI output, when present) does not describe.
func TestRoutesAreInSpec(t *testing.T) {
	srv, _, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(t.Context()) }()

	routes := srv.Routes()
	if len(routes) == 0 {
		t.Fatal("server registered no routes")
	}
	tsp := tspPaths(t)
	oapi := openapiPaths(t)
	if oapi == nil {
		t.Log("spec/tsp-output not generated; checking spec/main.tsp only (run `make build-spec`)")
	}

	for _, route := range routes {
		if !strings.HasPrefix(route, "/api/") {
			continue
		}
		if !specHas(tsp, route) {
			t.Errorf("route %s is served but missing from spec/main.tsp", route)
		}
		if oapi != nil && !specHas(oapi, route) {
			t.Errorf("route %s is served but missing from generated OpenAPI output; run `make build-spec`", route)
		}
	}
}

func TestSpecHas(t *testing.T) {
	paths := map[string]bool{"/api/a": true, "/api/b/{id}": true}
	for route, want := range map[string]bool{
		"/api/a":  true,
		"/api/b/": true,
		"/api/c":  false,
		"/api/c/": false,
	} {
		if got := specHas(paths, route); got != want {
			t.Errorf("specHas(%q) = %v, want %v", route, got, want)
		}
	}
}
