package driver

import (
	"encoding/json"
	"os"
	"path/filepath"

	"github.com/el-j/run-zero/pkg/state"
)

func (s *InstanceStore) saveLocked() error {
	if s.filePath == "" {
		return nil
	}
	data, err := json.MarshalIndent(s.instances, "", "  ")
	if err != nil {
		return err
	}
	tmp := s.filePath + ".tmp"
	if err := os.MkdirAll(filepath.Dir(s.filePath), 0755); err != nil && filepath.Dir(s.filePath) != "." {
		return err
	}
	if err := os.WriteFile(tmp, data, 0644); err != nil {
		return err
	}
	return os.Rename(tmp, s.filePath)
}

// Save persists the current instance map to disk.
func (s *InstanceStore) Save() error {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.saveLocked()
}

// Load restores runner instances from disk.
func (s *InstanceStore) Load() error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.filePath == "" {
		return nil
	}
	data, err := os.ReadFile(s.filePath)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}
	var loaded map[string]state.RunnerInfo
	if err := json.Unmarshal(data, &loaded); err != nil {
		return err
	}
	s.instances = loaded
	return nil
}
