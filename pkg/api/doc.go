// Package api implements the run-zero HTTP control plane: JSON endpoints for
// fleet status, settings, cache, runner and workflow actions, image builds, a
// Server-Sent Events stream, and the embedded dashboard UI.
//
// The served routes are described by the TypeSpec in spec/main.tsp;
// Server.Routes exposes the registered patterns so tests can detect drift.
package api
