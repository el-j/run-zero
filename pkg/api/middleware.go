package api

import (
	"encoding/json"
	"net"
	"net/http"
	"strings"
)

// CheckHostHeader ensures incoming requests match allowed host names.
func CheckHostHeader(allowedHosts []string) func(http.Handler) http.Handler {
	allowedMap := make(map[string]bool)
	for _, h := range allowedHosts {
		allowedMap[strings.ToLower(strings.TrimSpace(h))] = true
	}

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			host := r.Host
			if h, _, err := net.SplitHostPort(host); err == nil {
				host = h
			}
			host = strings.ToLower(strings.TrimSpace(host))

			// If allowedHosts is empty, default to loopback / localhost
			if len(allowedMap) == 0 {
				if host != "127.0.0.1" && host != "localhost" && host != "::1" {
					writeError(w, http.StatusMisdirectedRequest, "Host not allowed: "+host)
					return
				}
			} else if !allowedMap[host] {
				writeError(w, http.StatusMisdirectedRequest, "Host not allowed: "+host)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}

// CORSOptions handles CORS preflight without granting cross-origin permissions.
func CORSOptions(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func writeJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("Cache-Control", "no-store, no-cache, must-revalidate")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(data)
}

func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}
