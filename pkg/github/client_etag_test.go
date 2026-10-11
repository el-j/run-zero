package github

import (
	"context"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"
)

func TestDoRequest_RevalidatesWithETag(t *testing.T) {
	var full, notModified int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("If-None-Match") == `"v1"` {
			atomic.AddInt32(&notModified, 1)
			w.WriteHeader(http.StatusNotModified)
			return
		}
		atomic.AddInt32(&full, 1)
		w.Header().Set("ETag", `"v1"`)
		_, _ = w.Write([]byte(`{"total_count":2}`))
	}))
	defer srv.Close()

	c := NewClient("t", srv.URL, nil)
	for i := 0; i < 3; i++ {
		var out struct {
			TotalCount int `json:"total_count"`
		}
		if _, err := c.DoRequest(context.Background(), "GET", "/x", nil, &out); err != nil {
			t.Fatal(err)
		}
		if out.TotalCount != 2 {
			t.Fatalf("call %d: want cached body total_count=2, got %d", i, out.TotalCount)
		}
	}
	if full != 1 || notModified != 2 {
		t.Fatalf("want 1 full + 2 conditional hits, got %d + %d", full, notModified)
	}
}

func TestDoRequest_SkipsCallsWhileQuotaExhausted(t *testing.T) {
	var hits int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		atomic.AddInt32(&hits, 1)
		w.Header().Set("X-RateLimit-Limit", "5000")
		w.Header().Set("X-RateLimit-Remaining", "0")
		w.Header().Set("X-RateLimit-Reset", "4102444800") // year 2100
		w.WriteHeader(http.StatusForbidden)
	}))
	defer srv.Close()

	c := NewClient("t", srv.URL, nil)
	for i := 0; i < 3; i++ {
		_, _ = c.DoRequest(context.Background(), "GET", "/x", nil, nil)
	}
	if hits != 1 {
		t.Fatalf("want 1 real request then local short-circuit, got %d", hits)
	}
}
