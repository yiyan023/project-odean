// Cases API: case metadata (docket, court, parties, verdict, outcomes).
// Serves CSV-backed case data with camelCase JSON responses.
package main

import (
	"log/slog"
	"net/http"
	"os"
	"strings"

	"halcyon/cases-api/internal"
)

func main() {
	seedDir := os.Getenv("SEED_DATA_DIR")
	if seedDir == "" {
		seedDir = "/app/seed_data"
	}
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
	logger.Info("starting cases-api", "seed_dir", seedDir)

	h := &internal.Handler{SeedDir: seedDir, Logger: logger}
	mux := http.NewServeMux()
	mux.HandleFunc("/health", h.Health)
	mux.HandleFunc("/cases/", func(w http.ResponseWriter, r *http.Request) {
		path := strings.TrimPrefix(r.URL.Path, "/cases/")
		if path == "" {
			h.ListCases(w, r)
			return
		}
		// single case: /cases/C-2020-0312
		h.GetCase(w, r, path)
	})
	mux.HandleFunc("/cases", h.ListCases)

	addr := ":5000"
	logger.Info("listening", "addr", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		logger.Error("server failed", "err", err)
		os.Exit(1)
	}
}
