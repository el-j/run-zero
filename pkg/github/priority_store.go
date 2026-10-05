package github

import (
	"encoding/json"
	"os"
	"path/filepath"
)

type priorityFileSchema struct {
	Priority []string `json:"priority"`
	Paused   []string `json:"paused"`
}

// Load reads priority and pause lists from disk if the file exists.
func (pm *PriorityManager) Load() error {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	data, err := os.ReadFile(pm.filePath)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}

	var schema priorityFileSchema
	if err := json.Unmarshal(data, &schema); err != nil {
		return err
	}

	pm.priority = schema.Priority
	pm.paused = make(map[string]bool)
	for _, p := range schema.Paused {
		pm.paused[p] = true
	}
	return nil
}

// Save atomically writes the current priority order and pause states to disk.
func (pm *PriorityManager) Save() error {
	pm.mu.RLock()
	pausedList := make([]string, 0, len(pm.paused))
	for p := range pm.paused {
		pausedList = append(pausedList, p)
	}
	schema := priorityFileSchema{
		Priority: pm.priority,
		Paused:   pausedList,
	}
	filePath := pm.filePath
	pm.mu.RUnlock()

	if filePath == "" {
		return nil
	}

	data, err := json.MarshalIndent(schema, "", "  ")
	if err != nil {
		return err
	}

	tmpFile := filePath + ".tmp"
	if err := os.MkdirAll(filepath.Dir(filePath), 0755); err != nil && filepath.Dir(filePath) != "." {
		return err
	}
	if err := os.WriteFile(tmpFile, data, 0644); err != nil {
		return err
	}
	return os.Rename(tmpFile, filePath)
}

// Update sets the priorities and pause states, then persists them to disk.
func (pm *PriorityManager) Update(priority, paused []string) error {
	pm.mu.Lock()
	pm.priority = make([]string, len(priority))
	copy(pm.priority, priority)

	pm.paused = make(map[string]bool)
	for _, p := range paused {
		pm.paused[p] = true
	}
	pm.mu.Unlock()

	return pm.Save()
}
