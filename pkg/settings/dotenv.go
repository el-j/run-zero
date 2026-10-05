package settings

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// UpdateDotEnv updates key-value pairs in a .env file, adding missing keys at the bottom.
func UpdateDotEnv(filePath string, keyValues map[string]string) error {
	if strings.TrimSpace(filePath) == "" || len(keyValues) == 0 {
		return nil
	}

	existingLines := []string{}
	seenKeys := make(map[string]bool)

	if data, err := os.ReadFile(filePath); err == nil {
		scanner := bufio.NewScanner(strings.NewReader(string(data)))
		for scanner.Scan() {
			line := scanner.Text()
			trimmed := strings.TrimSpace(line)

			if strings.HasPrefix(trimmed, "#") || !strings.Contains(line, "=") {
				existingLines = append(existingLines, line)
				continue
			}

			parts := strings.SplitN(line, "=", 2)
			key := strings.TrimSpace(parts[0])

			if newVal, ok := keyValues[key]; ok {
				existingLines = append(existingLines, fmt.Sprintf("%s=%s", key, newVal))
				seenKeys[key] = true
			} else {
				existingLines = append(existingLines, line)
			}
		}
	}

	for k, v := range keyValues {
		if !seenKeys[k] {
			existingLines = append(existingLines, fmt.Sprintf("%s=%s", k, v))
		}
	}

	outContent := strings.Join(existingLines, "\n")
	if len(existingLines) > 0 && !strings.HasSuffix(outContent, "\n") {
		outContent += "\n"
	}

	tmpFile := filePath + ".tmp"
	if err := os.MkdirAll(filepath.Dir(filePath), 0755); err != nil && filepath.Dir(filePath) != "." {
		return err
	}
	if err := os.WriteFile(tmpFile, []byte(outContent), 0644); err != nil {
		return err
	}
	return os.Rename(tmpFile, filePath)
}
