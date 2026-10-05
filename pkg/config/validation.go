package config

import (
	"fmt"
	"strconv"
	"strings"
)

// ConfigError indicates an invalid configuration value.
type ConfigError struct {
	Message string
}

func (e *ConfigError) Error() string {
	return e.Message
}

var trueValues = map[string]bool{
	"true": true,
	"1":    true,
	"yes":  true,
	"on":   true,
}

var falseValues = map[string]bool{
	"false": true,
	"0":     true,
	"no":    true,
	"off":   true,
}

var validBackends = map[string]bool{
	"auto":                true,
	"hybrid":              true,
	"docker":              true,
	"container":           true,
	"orb":                 true,
	"orbstack":            true,
	"orbstack-vm":         true,
	"vm-orb":              true,
	"wsl":                 true,
	"wsl2":                true,
	"windows":             true,
	"multipass":           true,
	"canonical-multipass": true,
}

var archAliases = map[string]string{
	"both":    "both",
	"arm64":   "arm64",
	"aarch64": "arm64",
	"amd64":   "amd64",
	"x64":     "amd64",
	"x86_64":  "amd64",
}

func parseInt(env EnvLookup, name string, defaultValue int, min int, max *int) (int, error) {
	raw, ok := env.Lookup(name)
	if !ok || strings.TrimSpace(raw) == "" {
		return defaultValue, nil
	}
	raw = strings.TrimSpace(raw)
	val, err := strconv.Atoi(raw)
	if err != nil {
		return 0, &ConfigError{Message: fmt.Sprintf("%s='%s' is not an integer", name, raw)}
	}
	if val < min || (max != nil && val > *max) {
		bound := fmt.Sprintf(">= %d", min)
		if max != nil {
			bound = fmt.Sprintf("between %d and %d", min, *max)
		}
		return 0, &ConfigError{Message: fmt.Sprintf("%s=%d must be %s", name, val, bound)}
	}
	return val, nil
}

func parseBool(env EnvLookup, name string, defaultValue bool) (bool, error) {
	raw, ok := env.Lookup(name)
	if !ok || strings.TrimSpace(raw) == "" {
		return defaultValue, nil
	}
	cleaned := strings.ToLower(strings.TrimSpace(raw))
	if trueValues[cleaned] {
		return true, nil
	}
	if falseValues[cleaned] {
		return false, nil
	}
	return false, &ConfigError{Message: fmt.Sprintf("%s='%s' is not a boolean (use true/false)", name, strings.TrimSpace(raw))}
}

func parseChoice(env EnvLookup, name string, defaultValue string, choices map[string]bool) (string, error) {
	raw, ok := env.Lookup(name)
	if !ok || strings.TrimSpace(raw) == "" {
		return defaultValue, nil
	}
	cleaned := strings.ToLower(strings.TrimSpace(raw))
	if !choices[cleaned] {
		var list []string
		for k := range choices {
			list = append(list, k)
		}
		return "", &ConfigError{Message: fmt.Sprintf("%s='%s' must be one of: %s", name, strings.TrimSpace(raw), strings.Join(list, ", "))}
	}
	return cleaned, nil
}

func parseArch(env EnvLookup, name string, defaultValue string) (string, error) {
	raw, ok := env.Lookup(name)
	if !ok || strings.TrimSpace(raw) == "" {
		return defaultValue, nil
	}
	cleaned := strings.ToLower(strings.TrimSpace(raw))
	canonical, exists := archAliases[cleaned]
	if !exists {
		return "", &ConfigError{Message: fmt.Sprintf("%s='%s' must be one of: both, arm64, amd64, x64, x86_64, aarch64", name, strings.TrimSpace(raw))}
	}
	return canonical, nil
}
