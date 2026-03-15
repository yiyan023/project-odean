package internal

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"strings"
)

// Handler serves cases API.
type Handler struct {
	SeedDir string
	Logger  *slog.Logger
}

// Health returns service health.
func (h *Handler) Health(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]string{
		"status":  "ok",
		"service": "cases-api",
	})
}

// ListCases returns filtered cases (query: case_id, opposing_firm_name).
func (h *Handler) ListCases(w http.ResponseWriter, r *http.Request) {
	cases, err := LoadCases(h.SeedDir)
	if err != nil {
		h.Logger.Error("load cases failed", "err", err)
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}
	caseID := r.URL.Query().Get("case_id")
	if caseID != "" {
		var filtered []Case
		for _, c := range cases {
			if c.CaseID == caseID {
				filtered = append(filtered, c)
			}
		}
		cases = filtered
	}
	opposing := r.URL.Query().Get("opposing_firm_name")
	if opposing != "" {
		var filtered []Case
		low := strings.ToLower(opposing)
		for _, c := range cases {
			if strings.Contains(strings.ToLower(c.OpposingFirmName), low) {
				filtered = append(filtered, c)
			}
		}
		cases = filtered
	}
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]interface{}{
		"total": len(cases),
		"cases": cases,
	})
}

// GetCase returns a single case by ID.
func (h *Handler) GetCase(w http.ResponseWriter, r *http.Request, caseID string) {
	cases, err := LoadCases(h.SeedDir)
	if err != nil {
		h.Logger.Error("load cases failed", "err", err)
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}
	for _, c := range cases {
		if c.CaseID == caseID {
			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(c)
			return
		}
	}
	http.Error(w, `{"error":"not found"}`, http.StatusNotFound)
}
