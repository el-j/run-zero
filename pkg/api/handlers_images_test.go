package api

import (
	"bytes"
	"encoding/json"
	"net/http"
	"testing"

	"github.com/el-j/run-zero/pkg/builder"
)

func TestImagesEndpoints(t *testing.T) {
	srv, _, _, _, _ := setupTestServer(t)
	defer func() { _ = srv.Shutdown(nil) }()

	baseURL := "http://" + srv.Addr()

	// 1. GET /api/images
	resp, err := http.Get(baseURL + "/api/images")
	if err != nil {
		t.Fatalf("failed to GET /api/images: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("expected 200 OK from /api/images, got %d", resp.StatusCode)
	}

	var imgResp builder.ImagesStatusResponse
	if err := json.NewDecoder(resp.Body).Decode(&imgResp); err != nil {
		t.Fatalf("failed to decode /api/images response: %v", err)
	}

	if len(imgResp.VMImages) != 2 {
		t.Errorf("expected 2 VM images, got %d", len(imgResp.VMImages))
	}
	if len(imgResp.ContainerImages) != 2 {
		t.Errorf("expected 2 container images, got %d", len(imgResp.ContainerImages))
	}

	// 2. POST /api/actions/build-image
	reqBody, _ := json.Marshal(builder.ImageBuildRequest{
		Target: "container",
		Arch:   "arm64",
	})
	postResp, err := http.Post(baseURL+"/api/actions/build-image", "application/json", bytes.NewReader(reqBody))
	if err != nil {
		t.Fatalf("failed to POST /api/actions/build-image: %v", err)
	}
	defer postResp.Body.Close()

	if postResp.StatusCode != http.StatusAccepted {
		t.Fatalf("expected 202 Accepted, got %d", postResp.StatusCode)
	}

	var buildProg builder.ImageBuildProgress
	if err := json.NewDecoder(postResp.Body).Decode(&buildProg); err != nil {
		t.Fatalf("failed to decode build progress: %v", err)
	}
	if buildProg.BuildID == "" {
		t.Error("expected non-empty build_id")
	}

	// 3. GET /api/images/build/{id}
	getProgResp, err := http.Get(baseURL + "/api/images/build/" + buildProg.BuildID)
	if err != nil {
		t.Fatalf("failed to GET /api/images/build/{id}: %v", err)
	}
	defer getProgResp.Body.Close()

	if getProgResp.StatusCode != http.StatusOK {
		t.Errorf("expected 200 OK from get build progress, got %d", getProgResp.StatusCode)
	}

	// 4. POST /api/actions/build-image/cancel
	cancelResp, err := http.Post(baseURL+"/api/actions/build-image/cancel", "application/json", nil)
	if err != nil {
		t.Fatalf("failed to POST cancel: %v", err)
	}
	defer cancelResp.Body.Close()

	if cancelResp.StatusCode != http.StatusOK {
		t.Errorf("expected 200 OK from cancel, got %d", cancelResp.StatusCode)
	}
}
