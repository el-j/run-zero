package web

import "embed"

// DistFS contains the pre-compiled Vite dashboard UI bundle.
//
//go:embed all:dist
var DistFS embed.FS
