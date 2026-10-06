package bridge

import (
	"context"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"strings"

	"github.com/el-j/run-zero/pkg/driver"
)

// Server coordinates HTTP API routing for the Host VM Bridge.
type Server struct {
	port      int
	host      string
	token     string
	version   string
	gitSHA    string
	driverMap map[string]driver.RunnerDriver
	httpSrv   *http.Server
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
	return &Server{
		port:      port,
		host:      host,
		token:     token,
		version:   version,
		gitSHA:    gitSHA,
		driverMap: drivers,
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
	if path == "" || path == "/health" || path == "/api/health" {
		s.handleHealth(w, r)
		return
	}
	if path == "/api/status" {
		s.handleStatus(w, r)
		return
	}

	if strings.HasPrefix(path, "/api/drivers/") {
		if !s.checkAuth(r) {
			s.writeJSON(w, http.StatusUnauthorized, map[string]string{"error": "Unauthorized"})
			return
		}
		parts := strings.Split(strings.TrimPrefix(path, "/api/drivers/"), "/")
		if len(parts) >= 2 {
			driverName, action := parts[0], parts[1]
			switch {
			case r.Method == http.MethodGet && action == "runners":
				s.handleGetDriverRunners(w, r, driverName)
				return
			case r.Method == http.MethodPost && action == "spawn":
				s.handlePostDriverSpawn(w, r, driverName)
				return
			case r.Method == http.MethodPost && (action == "stop" || action == "destroy"):
				s.handlePostDriverStop(w, r, driverName)
				return
			case r.Method == http.MethodPost && action == "prune":
				s.handlePostDriverPrune(w, r, driverName)
				return
			case r.Method == http.MethodPost && action == "cleanup":
				s.handlePostDriverCleanup(w, r, driverName)
				return
			}
		}
	}
	s.writeJSON(w, http.StatusNotFound, map[string]string{"error": "Endpoint not found: " + path})
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
