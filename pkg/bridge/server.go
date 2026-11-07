package bridge

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"strings"

	"github.com/el-j/run-zero/pkg/builder"
	"github.com/el-j/run-zero/pkg/driver"
)

// Server coordinates HTTP API routing for the Host VM Bridge.
type Server struct {
	port         int
	host         string
	token        string
	version      string
	gitSHA       string
	driverMap    map[string]driver.RunnerDriver
	httpSrv      *http.Server
	gb           *builder.GoldenBuilder
	imgInspector *builder.ImageInspector
	buildMgr     *builder.BuildManager
}

// NewServer creates a new Host VM Bridge server instance.
func NewServer(port int, host, token, version, gitSHA string, drivers map[string]driver.RunnerDriver) *Server {
	if port <= 0 {
		port = 49504
	}
	if host == "" {
		host = "127.0.0.1"
	}
	if gitSHA == "" {
		gitSHA = os.Getenv("RUNZERO_GIT_SHA")
	}

	stateDir := os.Getenv("RUNZERO_STATE_DIR")
	if stateDir == "" {
		stateDir = ".runzero-state"
	}
	provisionScript := os.Getenv("PROVISION_SCRIPT")
	bCfg := builder.Config{
		Distro:              "ubuntu:noble",
		RunnerVersion:       builder.DefaultRunnerVersion,
		StateDir:            stateDir,
		ProvisionScriptPath: provisionScript,
	}
	gb := builder.NewGoldenBuilder(bCfg, nil)
	inspector := builder.NewImageInspector(gb, nil)
	mgr := builder.NewBuildManager(gb, nil, nil, nil)

	return &Server{
		port:         port,
		host:         host,
		token:        token,
		version:      version,
		gitSHA:       gitSHA,
		driverMap:    drivers,
		gb:           gb,
		imgInspector: inspector,
		buildMgr:     mgr,
	}
}

// stopGoldenTemplates stops golden base VM templates left running (e.g. by an
// interrupted build) and logs which ones it stopped.
func (s *Server) stopGoldenTemplates(ctx context.Context) {
	if s.gb == nil {
		return
	}
	if stopped, err := s.gb.EnsureBaseImagesStopped(ctx); err == nil && len(stopped) > 0 {
		log.Printf("[bridge] Stopped running golden base VM templates on startup: %v", stopped)
	}
}

func (s *Server) resolveDriver(name string) driver.RunnerDriver {
	key := strings.ToLower(strings.TrimSpace(name))
	if d, ok := s.driverMap[key]; ok {
		return d
	}
	if key == "orbstack-vm" || key == "vm" || key == "orb" {
		return s.driverMap["orbstack"]
	}
	return nil
}

func (s *Server) writeJSON(w http.ResponseWriter, code int, val any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(val)
}

func (s *Server) checkAuth(r *http.Request) bool {
	if s.token == "" {
		return true
	}
	auth := r.Header.Get("Authorization")
	parts := strings.SplitN(auth, " ", 2)
	return len(parts) == 2 && strings.ToLower(parts[0]) == "bearer" && parts[1] == s.token
}

// ServeHTTP handles requests according to VM bridge specification.
func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	path := strings.TrimSuffix(r.URL.Path, "/")
	get, post := r.Method == http.MethodGet, r.Method == http.MethodPost
	switch {
	case path == "" || path == "/health" || path == "/api/health":
		s.handleHealth(w, r)
	case path == "/api/status":
		s.handleStatus(w, r)
	case path == "/api/images" && get:
		s.writeJSON(w, http.StatusOK, s.imgInspector.Inspect(r.Context()))
	case path == "/api/actions/build-image" && post:
		s.handleTriggerBuild(w, r)
	case path == "/api/actions/build-image/cancel" && post:
		s.handleCancelBuild(w, r)
	case path == "/api/actions/open-terminal" && post:
		s.handleOpenTerminal(w, r)
	case strings.HasPrefix(path, "/api/images/build/") && get:
		s.handleGetBuild(w, strings.TrimPrefix(path, "/api/images/build/"))
	case strings.HasPrefix(path, "/api/drivers/") && !s.checkAuth(r):
		s.writeUnauthorized(w)
	case strings.HasPrefix(path, "/api/drivers/") && s.routeDriverAction(w, r, strings.TrimPrefix(path, "/api/drivers/")):
	default:
		s.writeJSON(w, http.StatusNotFound, map[string]string{"error": "Endpoint not found: " + path})
	}
}

func (s *Server) writeUnauthorized(w http.ResponseWriter) {
	s.writeJSON(w, http.StatusUnauthorized, map[string]string{"error": "Unauthorized"})
}

func (s *Server) handleTriggerBuild(w http.ResponseWriter, r *http.Request) {
	if !s.checkAuth(r) {
		s.writeUnauthorized(w)
		return
	}
	var req builder.ImageBuildRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		s.writeJSON(w, http.StatusBadRequest, map[string]string{"error": "Invalid JSON: " + err.Error()})
		return
	}
	prog, err := s.buildMgr.TriggerBuild(r.Context(), req)
	if err != nil {
		s.writeJSON(w, http.StatusConflict, map[string]string{"error": err.Error()})
		return
	}
	s.writeJSON(w, http.StatusAccepted, prog)
}

func (s *Server) handleCancelBuild(w http.ResponseWriter, r *http.Request) {
	if !s.checkAuth(r) {
		s.writeUnauthorized(w)
		return
	}
	// CancelBuild is idempotent and currently never returns an error.
	_ = s.buildMgr.CancelBuild()
	s.writeJSON(w, http.StatusOK, map[string]string{"status": "cancelled"})
}

func (s *Server) handleGetBuild(w http.ResponseWriter, id string) {
	prog, ok := s.buildMgr.GetBuildByID(id)
	if !ok {
		s.writeJSON(w, http.StatusNotFound, map[string]string{"error": "Build not found"})
		return
	}
	s.writeJSON(w, http.StatusOK, prog)
}

// routeDriverAction dispatches an authenticated /api/drivers/{driver}/{action}
// request. It returns false when no handler matches.
func (s *Server) routeDriverAction(w http.ResponseWriter, r *http.Request, rest string) bool {
	parts := strings.Split(rest, "/")
	if len(parts) < 2 {
		return false
	}
	driverName, action := parts[0], parts[1]
	switch {
	case r.Method == http.MethodGet && action == "runners":
		s.handleGetDriverRunners(w, r, driverName)
	case r.Method != http.MethodPost:
		return false
	case action == "spawn":
		s.handlePostDriverSpawn(w, r, driverName)
	case action == "stop" || action == "destroy":
		s.handlePostDriverStop(w, r, driverName)
	case action == "prune":
		s.handlePostDriverPrune(w, r, driverName)
	case action == "cleanup":
		s.handlePostDriverCleanup(w, r, driverName)
	default:
		return false
	}
	return true
}

// Run listens and serves incoming bridge requests until ctx is done.
func (s *Server) Run(ctx context.Context) error {
	addr := fmt.Sprintf("%s:%d", s.host, s.port)
	s.httpSrv = &http.Server{
		Addr:    addr,
		Handler: s,
		BaseContext: func(net.Listener) context.Context {
			return ctx
		},
	}

	// Ensure no golden base VM templates are left running on startup
	go s.stopGoldenTemplates(context.Background())
	errCh := make(chan error, 1)
	go func() {
		if err := s.httpSrv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			errCh <- err
		}
		close(errCh)
	}()

	select {
	case <-ctx.Done():
		return s.httpSrv.Shutdown(context.Background())
	case err := <-errCh:
		return err
	}
}
