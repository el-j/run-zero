package api

import (
	"context"
	"fmt"
	"net"
	"net/http"
	"time"

	"github.com/el-j/run-zero/pkg/config"
	"github.com/el-j/run-zero/pkg/state"
)

// Server implements the HTTP and SSE control plane daemon.
type Server struct {
	httpServer *http.Server
	listener   net.Listener
	cfg        *config.Config
	state      *state.State
}

// NewServer configures an HTTP control plane matching the TypeSpec specification.
func NewServer(
	cfg *config.Config,
	st *state.State,
	distDir string,
	staticDir string,
	allowedHosts []string,
	heartbeatInterval time.Duration,
) *Server {
	mux := http.NewServeMux()

	// Fleet & logs
	mux.HandleFunc("/api/status", handleStatusAndFleet(st))
	mux.HandleFunc("/api/fleet", handleStatusAndFleet(st))
	mux.HandleFunc("/api/logs", handleLogs(st))

	// Settings & Cache
	mux.HandleFunc("/api/settings", handleSettings(cfg, st))
	mux.HandleFunc("/api/cache", handleCache(cfg, st))
	mux.HandleFunc("/api/cache/purge", handleCachePurge(cfg, st))
	mux.HandleFunc("/api/actions/clean-cache", handleCleanCacheLegacy(st))

	// Actions
	mux.HandleFunc("/api/actions/repo-priority", handleRepoPriority(st))
	mux.HandleFunc("/api/actions/workflow", handleWorkflowAction(st))
	mux.HandleFunc("/api/actions/runner", handleRunnerAction(st))
	mux.HandleFunc("/api/actions/prune", handlePrune(st))

	// Real-time SSE
	sseHandler := handleSSEStream(st, heartbeatInterval)
	mux.HandleFunc("/api/events", sseHandler)
	mux.HandleFunc("/api/stream", sseHandler)

	// Static UI assets
	mux.HandleFunc("/", handleStatic(distDir, staticDir))

	handler := CORSOptions(CheckHostHeader(allowedHosts)(mux))

	addr := fmt.Sprintf("%s:%d", cfg.DashboardHost, cfg.DashboardPort)
	srv := &http.Server{
		Addr:    addr,
		Handler: handler,
	}

	return &Server{
		httpServer: srv,
		cfg:        cfg,
		state:      st,
	}
}

// Start begins listening and serving HTTP traffic.
func (s *Server) Start() error {
	ln, err := net.Listen("tcp", s.httpServer.Addr)
	if err != nil {
		return err
	}
	s.listener = ln
	go func() {
		_ = s.httpServer.Serve(ln)
	}()
	return nil
}

// Addr returns the actual bound network address.
func (s *Server) Addr() string {
	if s.listener != nil {
		return s.listener.Addr().String()
	}
	return s.httpServer.Addr
}

// Shutdown gracefully terminates HTTP connections within ctx deadline.
func (s *Server) Shutdown(ctx context.Context) error {
	return s.httpServer.Shutdown(ctx)
}
