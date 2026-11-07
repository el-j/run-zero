package bridge

import (
	"context"
	"net/http/httptest"
	"reflect"
	"testing"

	"github.com/el-j/run-zero/pkg/driver"
	"github.com/el-j/run-zero/pkg/state"
)

// capturingDriver records the spec the bridge hands to a VM driver.
type capturingDriver struct {
	mockDriver
	spec driver.RunnerSpec
}

func (c *capturingDriver) SpawnRunner(_ context.Context, spec driver.RunnerSpec) (*state.RunnerInfo, error) {
	c.spec = spec
	return &state.RunnerInfo{ID: "vm-1", Name: spec.Name}, nil
}

// The daemon's BridgeDriver and the bridge server must carry every field a VM
// driver needs: sizing, cache mounts, proxies and image, not only identity.
func TestBridgeRoundTrip_ForwardsTheWholeSpec(t *testing.T) {
	vm := &capturingDriver{mockDriver: mockDriver{backend: "multipass"}}
	s := newTestServer(t, "tok", map[string]driver.RunnerDriver{"multipass": vm})
	ts := httptest.NewServer(s)
	defer ts.Close()

	sent := driver.RunnerSpec{
		Name: "runzero-j1-r2-amd64-o__r-abc", Repo: "o/r", Arch: "amd64", Backend: "multipass",
		Labels: []string{"self-hosted", "vm"}, Token: "reg", Env: map[string]string{"A": "1"},
		CPUs: 3, MemoryMB: 4096, Mounts: map[string]string{"/host/npm": "/home/runner/.npm"},
		Proxies: true, ImageName: "22.04",
	}
	if _, err := driver.NewBridgeDriver(ts.URL, "multipass", "tok", ts.Client()).SpawnRunner(context.Background(), sent); err != nil {
		t.Fatalf("spawn through bridge: %v", err)
	}
	if !reflect.DeepEqual(vm.spec, sent) {
		t.Fatalf("spec changed in transit:\n got %+v\nwant %+v", vm.spec, sent)
	}
}
