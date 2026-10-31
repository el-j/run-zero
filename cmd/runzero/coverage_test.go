package main

import (
	"bytes"
	"context"
	"errors"
	"net"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
	"testing"
	"time"
)

type fakeExec struct {
	fn func(name string, args ...string) ([]byte, error)
}

func (f *fakeExec) Run(_ context.Context, name string, args ...string) ([]byte, error) {
	return f.fn(name, args...)
}
func (f *fakeExec) LookPath(file string) (string, error) { return file, nil }

func TestMain_UsesExit(t *testing.T) {
	old, oldArgs := exit, os.Args
	defer func() { exit, os.Args = old, oldArgs }()
	got := -1
	exit = func(c int) { got = c }
	os.Args = []string{"runzero", "-version"}
	main()
	if got != 0 {
		t.Fatalf("exit code %d", got)
	}
}

func TestRun_DispatchAndDaemonSuccess(t *testing.T) {
	var o, e bytes.Buffer
	if code := run([]string{"--build-vm-base", "-arch", "bogus"}, &o, &e); code != 1 {
		t.Fatalf("got %d", code)
	}
	dir := t.TempDir()
	env := filepath.Join(dir, ".env")
	_ = os.WriteFile(env, []byte("DASHBOARD_HOST=127.0.0.1\nDASHBOARD_PORT=0\n"), 0o644)
	go func() {
		time.Sleep(700 * time.Millisecond)
		_ = syscall.Kill(os.Getpid(), syscall.SIGTERM)
	}()
	t.Chdir(dir)
	if code := run([]string{"-config", env}, &o, &e); code != 0 {
		t.Fatalf("got %d: %s", code, e.String())
	}
}

func TestRunDoctor_ConfigPaths(t *testing.T) {
	dir := t.TempDir()
	env := filepath.Join(dir, ".env")
	_ = os.WriteFile(env, []byte("ACCESS_TOKEN=tok\nPROXIES_ENABLED=true\nCACHE_ENABLED=false\n"), 0o644)
	var o, e bytes.Buffer
	code := runDoctor([]string{"-config", env, "-timeout", "300ms"}, &o, &e)
	if code != 0 && code != 1 {
		t.Fatalf("code %d", code)
	}
	if !strings.Contains(o.String(), "Doctor") {
		t.Fatal(o.String())
	}
}

func TestRunDoctor_FailsOnHostCacheMissing(t *testing.T) {
	dir := t.TempDir()
	env := filepath.Join(dir, ".env")
	_ = os.WriteFile(env, []byte("CACHE_ENABLED=true\nHOST_CACHE_DIR="+filepath.Join(dir, "nope")+"\n"), 0o644)
	var o, e bytes.Buffer
	if code := runDoctor([]string{"-config", env, "-timeout", "300ms"}, &o, &e); code != 1 {
		t.Fatalf("code %d: %s", code, o.String())
	}
}

func TestRunBuildVMBase_Paths(t *testing.T) {
	dir := t.TempDir()
	t.Chdir(dir)
	script := filepath.Join(dir, "prov.sh")
	_ = os.WriteFile(script, []byte("echo hi"), 0o644)
	old := goldenExec
	defer func() { goldenExec = old }()

	var o, e bytes.Buffer
	t.Setenv("PROVISION_SCRIPT", filepath.Join(dir, "missing.sh"))
	if code := runBuildVMBase(nil, &o, &e); code != 1 {
		t.Fatalf("missing script: %d", code)
	}

	t.Setenv("PROVISION_SCRIPT", "")
	if code := runBuildVMBase(nil, &o, &e); code != 1 {
		t.Fatalf("default script missing: %d", code)
	}
	_ = os.MkdirAll("docker", 0o755)
	_ = os.WriteFile("docker/provision-toolchain.sh", []byte("echo"), 0o644)
	if code := runBuildVMBase([]string{"-arch", "bogus"}, &o, &e); code != 1 {
		t.Fatalf("bogus: %d", code)
	}
	t.Setenv("PROVISION_SCRIPT", script)
	t.Setenv("RUNNER_ARCH", "")
	built := false
	goldenExec = &fakeExec{fn: func(name string, args ...string) ([]byte, error) {
		if name == "orbctl" && len(args) > 0 && args[0] == "list" {
			if built {
				return []byte(`[{"name":"runzero-vm-base-arm64","state":"running"}]`), nil
			}
			return []byte(`[]`), nil
		}
		built = true
		return []byte("ok"), nil
	}}
	o.Reset()
	if code := runBuildVMBase([]string{"-arch", "aarch64"}, &o, &e); code != 0 {
		t.Fatalf("build: %d %s", code, e.String())
	}
	if !strings.Contains(o.String(), "Successfully built") {
		t.Fatal(o.String())
	}

	// Second run: stamp current, so "already up to date".
	o.Reset()
	if code := runBuildVMBase([]string{"-arch", "arm64"}, &o, &e); code != 0 {
		t.Fatalf("second: %d %s", code, e.String())
	}
	if !strings.Contains(o.String(), "already up to date") {
		t.Fatal(o.String())
	}

	if code := runBuildVMBase([]string{"-arch", "x86_64"}, &o, &e); code != 0 && code != 1 {
		t.Fatal(code)
	}

	goldenExec = &fakeExec{fn: func(string, ...string) ([]byte, error) { return nil, errors.New("boom") }}
	e.Reset()
	if code := runBuildVMBase([]string{"-arch", "both"}, &o, &e); code != 1 {
		t.Fatalf("fail: %d", code)
	}
	if !strings.Contains(e.String(), "Failed building") {
		t.Fatal(e.String())
	}
}

func freePort(t *testing.T) int {
	l, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer func() { _ = l.Close() }()
	return l.Addr().(*net.TCPAddr).Port
}

func TestRunBridge_StartStopAndErrors(t *testing.T) {
	home := t.TempDir()
	t.Setenv("HOME", home)
	t.Setenv("RUNZERO_STATE_DIR", t.TempDir())
	t.Chdir(t.TempDir())
	state := filepath.Join(home, ".local-github-runner", "state")
	_ = os.MkdirAll(state, 0o755)
	_ = os.WriteFile(filepath.Join(state, "bridge-instances.json"), []byte("{garbage"), 0o644)

	env := filepath.Join(t.TempDir(), ".env")
	_ = os.WriteFile(env, []byte("RUNZERO_BRIDGE_TOKEN=abc\n"), 0o644)
	t.Setenv("HOST_VM_BRIDGE_PORT", "notanumber")
	t.Setenv("HOST_VM_BRIDGE_HOST", "127.0.0.1")

	port := freePort(t)
	go func() {
		time.Sleep(600 * time.Millisecond)
		_ = syscall.Kill(os.Getpid(), syscall.SIGTERM)
	}()
	var o, e bytes.Buffer
	if code := runBridge([]string{"-port", strconv.Itoa(port), "-config", env}, &o, &e); code != 0 {
		t.Fatalf("code %d: %s", code, e.String())
	}
	if !strings.Contains(e.String(), "could not load") {
		t.Errorf("expected load warning: %s", e.String())
	}

	// Port in use -> Run error.
	l, _ := net.Listen("tcp", "127.0.0.1:0")
	defer func() { _ = l.Close() }()
	busy := l.Addr().(*net.TCPAddr).Port
	t.Setenv("HOST_VM_BRIDGE_PORT", strconv.Itoa(busy))
	e.Reset()
	if code := runBridge([]string{"-port", strconv.Itoa(busy), "-config", env}, &o, &e); code != 1 {
		t.Fatalf("code %d", code)
	}
	if !strings.Contains(e.String(), "[Bridge Error]") {
		t.Fatal(e.String())
	}
}
