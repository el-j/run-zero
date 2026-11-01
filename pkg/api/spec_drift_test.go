package api

import (
	"context"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"testing"
	"time"
)

var (
	tspRoute  = regexp.MustCompile(`@route\("([^"]+)"\)`)
	tspOp     = regexp.MustCompile(`@(get|post|put|delete|patch)\s+@route\("([^"]+)"\)`)
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

// tspMethods maps each operation path in spec/main.tsp (with the namespace
// prefix) to its declared HTTP methods.
func tspMethods(t *testing.T) map[string]map[string]bool {
	t.Helper()
	src, err := os.ReadFile(filepath.Join(specRoot, "main.tsp"))
	if err != nil {
		t.Fatalf("read spec: %v", err)
	}
	prefix := tspRoute.FindStringSubmatch(string(src))[1]
	methods := map[string]map[string]bool{}
	for _, m := range tspOp.FindAllStringSubmatch(string(src), -1) {
		path := prefix + m[2]
		if methods[path] == nil {
			methods[path] = map[string]bool{}
		}
		methods[path][strings.ToUpper(m[1])] = true
	}
	return methods
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

// TestSpecPathsAreServed fails when spec/main.tsp documents a path the server
// does not register.
func TestSpecPathsAreServed(t *testing.T) {
	srv, _, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(t.Context()) }()

	served := map[string]bool{}
	for _, r := range srv.Routes() {
		served[r] = true
	}
	for path := range tspPaths(t) {
		if !specHas(map[string]bool{path: true}, servedPattern(path, served)) {
			t.Errorf("spec/main.tsp documents %s but the server does not serve it", path)
		}
	}
}

// servedPattern returns the registered pattern that serves a spec path: the
// path itself, or for "/x/{id}" the subtree pattern "/x/". It returns "" when
// nothing serves it.
func servedPattern(path string, served map[string]bool) string {
	if served[path] {
		return path
	}
	if i := strings.Index(path, "{"); i > 0 && served[path[:i]] {
		return path[:i]
	}
	return ""
}

// TestServedMethodsMatchSpec sends every HTTP method to every documented path.
// A method the spec does not declare must be rejected with 405 (before the
// handler acts, so the probe has no side effects). A declared GET must not be
// rejected as missing or not allowed; declared POSTs are exercised by the
// handler tests, which send valid bodies.
func TestServedMethodsMatchSpec(t *testing.T) {
	srv, _, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(t.Context()) }()
	handler := srv.httpServer.Handler

	// Server-sent event streams never end, so they are only probed with
	// methods that are rejected up front.
	streams := map[string]bool{"/api/stream": true, "/api/events": true}

	for path, declared := range tspMethods(t) {
		url := strings.ReplaceAll(path, "{id}", "spec-drift-probe")
		for _, method := range []string{http.MethodGet, http.MethodPost, http.MethodPut, http.MethodDelete, http.MethodPatch} {
			if declared[method] && (method != http.MethodGet || streams[path]) {
				continue
			}
			// A handler that wrongly accepts the method may start streaming; the
			// deadline makes it return so the mismatch is reported, not hung on.
			ctx, cancel := context.WithTimeout(t.Context(), 2*time.Second)
			req := httptest.NewRequest(method, "http://127.0.0.1"+url, nil).WithContext(ctx)
			rec := httptest.NewRecorder()
			handler.ServeHTTP(rec, req)
			cancel()

			switch {
			case !declared[method] && rec.Code != http.StatusMethodNotAllowed:
				t.Errorf("%s %s: got %d, want 405 (method not in spec/main.tsp)", method, path, rec.Code)
			case declared[method] && (rec.Code == http.StatusNotFound && !strings.Contains(url, "spec-drift-probe") || rec.Code == http.StatusMethodNotAllowed):
				t.Errorf("%s %s: got %d, but spec/main.tsp declares it", method, path, rec.Code)
			}
		}
	}
}

func TestServedPattern(t *testing.T) {
	served := map[string]bool{"/api/a": true, "/api/b/": true}
	for path, want := range map[string]string{
		"/api/a":      "/api/a",
		"/api/b/{id}": "/api/b/",
		"/api/c":      "",
		"/api/c/{id}": "",
	} {
		if got := servedPattern(path, served); got != want {
			t.Errorf("servedPattern(%q) = %q, want %q", path, got, want)
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
