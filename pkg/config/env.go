package config

import (
	"bufio"
	"io"
	"os"
	"strings"
)

// EnvLookup represents an environment variable resolver.
type EnvLookup interface {
	Lookup(key string) (string, bool)
}

// OSEnv resolves environment variables from the OS environment.
type OSEnv struct{}

// Lookup returns the OS environment variable value.
func (OSEnv) Lookup(key string) (string, bool) {
	return os.LookupEnv(key)
}

// MapEnv resolves environment variables from an in-memory map.
type MapEnv map[string]string

// Lookup returns the map-backed environment variable value.
func (m MapEnv) Lookup(key string) (string, bool) {
	val, ok := m[key]
	return val, ok
}

// CompositeEnv checks a primary source first, falling back to a secondary source.
type CompositeEnv struct {
	Primary   EnvLookup
	Secondary EnvLookup
}

// Lookup checks primary and falls back to secondary.
func (c CompositeEnv) Lookup(key string) (string, bool) {
	if val, ok := c.Primary.Lookup(key); ok && val != "" {
		return val, true
	}
	return c.Secondary.Lookup(key)
}

// ParseDotEnv reads key-value pairs from an io.Reader in .env format.
func ParseDotEnv(r io.Reader) (MapEnv, error) {
	result := make(MapEnv)
	scanner := bufio.NewScanner(r)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		if strings.HasPrefix(line, "export ") {
			line = strings.TrimSpace(line[7:])
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}
		key := strings.TrimSpace(parts[0])
		val := strings.TrimSpace(parts[1])
		if len(val) >= 2 && ((val[0] == '"' && val[len(val)-1] == '"') || (val[0] == '\'' && val[len(val)-1] == '\'')) {
			val = val[1 : len(val)-1]
		}
		if key != "" {
			result[key] = val
		}
	}
	return result, scanner.Err()
}

// LoadDotEnvFile loads key-value pairs from a file path if it exists.
func LoadDotEnvFile(filename string) (MapEnv, error) {
	f, err := os.Open(filename)
	if err != nil {
		if os.IsNotExist(err) {
			return make(MapEnv), nil
		}
		return nil, err
	}
	defer f.Close()
	return ParseDotEnv(f)
}
