// Package daemon wires the run-zero runtime together: configuration, state,
// the GitHub poller, the Scaler that spawns and reaps self-hosted runners, and
// the HTTP API server, plus lifecycle and signal handling.
//
// Scaler.ScaleCycle runs one autoscaling pass as a sequence of small steps:
// discover repositories, prune finished runners, collect runners and active
// jobs, reap completed or stale runners, spawn runners for queued jobs, and
// publish the resulting fleet to the shared state.
package daemon
