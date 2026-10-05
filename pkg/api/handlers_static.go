package api

import (
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

func handleStatic(distDir string, staticDir string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		path := r.URL.Path
		if path == "/" || path == "" || path == "/index.html" {
			serveIndex(w, distDir, staticDir)
			return
		}

		if strings.HasPrefix(path, "/assets/") {
			serveAsset(w, r, distDir, path[len("/assets/"):])
			return
		}

		if strings.HasPrefix(path, "/fonts/") {
			serveFont(w, path[len("/fonts/"):], distDir, staticDir)
			return
		}

		// Legacy files
		if path == "/dashboard.css" || path == "/dashboard.js" {
			serveLegacy(w, r, staticDir, path[1:])
			return
		}

		writeError(w, http.StatusNotFound, "Not found")
	}
}

func serveIndex(w http.ResponseWriter, distDir, staticDir string) {
	distIndex := filepath.Join(distDir, "index.html")
	if data, err := os.ReadFile(distIndex); err == nil {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write(data)
		return
	}

	staticIndex := filepath.Join(staticDir, "index.html")
	if data, err := os.ReadFile(staticIndex); err == nil {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write(data)
		return
	}

	writeError(w, http.StatusNotFound, "Index not found")
}

func serveAsset(w http.ResponseWriter, r *http.Request, distDir, assetRel string) {
	if strings.Contains(assetRel, "..") {
		writeError(w, http.StatusNotFound, "Invalid asset path")
		return
	}
	full := filepath.Join(distDir, "assets", assetRel)
	data, err := os.ReadFile(full)
	if err != nil {
		writeError(w, http.StatusNotFound, "Asset not found")
		return
	}

	if strings.HasSuffix(assetRel, ".css") {
		w.Header().Set("Content-Type", "text/css; charset=utf-8")
	} else if strings.HasSuffix(assetRel, ".js") {
		w.Header().Set("Content-Type", "application/javascript; charset=utf-8")
	}
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write(data)
}

func serveFont(w http.ResponseWriter, fontName, distDir, staticDir string) {
	if strings.Contains(fontName, "..") || strings.Contains(fontName, "/") || strings.Contains(fontName, "\\") || !strings.HasSuffix(fontName, ".woff2") {
		writeError(w, http.StatusNotFound, "Font not found")
		return
	}

	candidates := []string{
		filepath.Join(distDir, "fonts", fontName),
		filepath.Join(staticDir, "fonts", fontName),
		filepath.Join("web/public/fonts", fontName),
		filepath.Join("src/dashboard/static/fonts", fontName),
	}

	for _, cand := range candidates {
		if data, err := os.ReadFile(cand); err == nil {
			w.Header().Set("Content-Type", "font/woff2")
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write(data)
			return
		}
	}
	writeError(w, http.StatusNotFound, "Font not found")
}

func serveLegacy(w http.ResponseWriter, r *http.Request, staticDir, filename string) {
	full := filepath.Join(staticDir, filename)
	data, err := os.ReadFile(full)
	if err != nil {
		writeError(w, http.StatusNotFound, "File not found")
		return
	}
	if strings.HasSuffix(filename, ".css") {
		w.Header().Set("Content-Type", "text/css; charset=utf-8")
	} else {
		w.Header().Set("Content-Type", "application/javascript; charset=utf-8")
	}
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write(data)
}
