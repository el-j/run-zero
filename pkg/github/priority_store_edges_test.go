package github

import (
	"os"
	"path/filepath"
	"testing"
)

func TestPriorityStoreFilesystemErrors(t *testing.T) {
	root := t.TempDir()
	parentFile := filepath.Join(root, "file")
	if err := os.WriteFile(parentFile, []byte("x"), 0600); err != nil {
		t.Fatal(err)
	}
	if err := (&PriorityManager{filePath: filepath.Join(parentFile, "child.json")}).Save(); err == nil {
		t.Fatal("expected directory creation error")
	}
	writeTarget := filepath.Join(root, "blocked")
	if err := os.Mkdir(writeTarget+".tmp", 0700); err != nil {
		t.Fatal(err)
	}
	if err := (&PriorityManager{filePath: writeTarget}).Save(); err == nil {
		t.Fatal("expected temporary write error")
	}
	directoryTarget := filepath.Join(root, "directory")
	if err := os.Mkdir(directoryTarget, 0700); err != nil {
		t.Fatal(err)
	}
	if err := (&PriorityManager{filePath: directoryTarget}).Save(); err == nil {
		t.Fatal("expected rename-over-directory error")
	}
	if err := (&PriorityManager{filePath: root}).Load(); err == nil {
		t.Fatal("expected read-directory error")
	}
}
