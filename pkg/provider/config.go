package provider

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

// ProviderConfig represents configuration for a single CI provider instance.
type ProviderConfig struct {
	ID       string   `json:"id" yaml:"id"`
	Type     string   `json:"type" yaml:"type"` // "github", "gitlab"
	Name     string   `json:"name" yaml:"name"`
	URL      string   `json:"url" yaml:"url"`
	Token    string   `json:"token" yaml:"token"`
	Owner    string   `json:"owner" yaml:"owner"`
	Org      string   `json:"org" yaml:"org"`
	Group    string   `json:"group" yaml:"group"`
	Projects []string `json:"projects" yaml:"projects"`
}

// ConfigFile holds the root list of configured CI providers.
type ConfigFile struct {
	Providers []ProviderConfig `json:"providers" yaml:"providers"`
}

// LoadConfigFile loads a providers configuration file supporting both JSON and YAML.
func LoadConfigFile(filePath string) (*ConfigFile, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("read provider config %s: %w", filePath, err)
	}

	trimmed := strings.TrimSpace(string(data))
	if strings.HasPrefix(trimmed, "{") {
		var cfg ConfigFile
		if err := json.Unmarshal([]byte(trimmed), &cfg); err != nil {
			return nil, fmt.Errorf("parse provider json %s: %w", filePath, err)
		}
		return &cfg, nil
	}

	return parseSimpleYAML(trimmed)
}

func parseSimpleYAML(content string) (*ConfigFile, error) {
	var providers []ProviderConfig
	var current *ProviderConfig

	scanner := bufio.NewScanner(strings.NewReader(content))
	inProjects := false

	for scanner.Scan() {
		line := scanner.Text()
		trimmed := strings.TrimSpace(line)
		if trimmed == "" || strings.HasPrefix(trimmed, "#") {
			continue
		}

		if strings.HasPrefix(trimmed, "- id:") {
			if current != nil {
				providers = append(providers, *current)
			}
			current = &ProviderConfig{
				ID: strings.Trim(strings.TrimPrefix(trimmed, "- id:"), " \"'"),
			}
			inProjects = false
			continue
		}

		if current == nil {
			continue
		}

		if inProjects {
			if strings.HasPrefix(trimmed, "- ") {
				proj := strings.Trim(strings.TrimPrefix(trimmed, "- "), " \"'")
				current.Projects = append(current.Projects, proj)
				continue
			} else {
				inProjects = false
			}
		}

		parts := strings.SplitN(trimmed, ":", 2)
		if len(parts) == 2 {
			key := strings.TrimSpace(parts[0])
			val := strings.Trim(strings.TrimSpace(parts[1]), " \"'")

			switch key {
			case "type":
				current.Type = val
			case "name":
				current.Name = val
			case "url":
				current.URL = val
			case "token":
				current.Token = val
			case "owner":
				current.Owner = val
			case "org":
				current.Org = val
			case "group":
				current.Group = val
			case "projects":
				if val != "" {
					current.Projects = append(current.Projects, val)
				} else {
					inProjects = true
				}
			}
		}
	}

	if current != nil {
		providers = append(providers, *current)
	}

	return &ConfigFile{Providers: providers}, nil
}
