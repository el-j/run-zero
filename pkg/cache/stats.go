package cache

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
)

// CategoryUsage describes disk storage for a single cache category.
type CategoryUsage struct {
	Category      string `json:"category"`
	Bytes         int64  `json:"bytes"`
	HumanReadable string `json:"human_readable"`
}

// CacheStats describes overall cache usage matching the TypeSpec contract.
type CacheStats struct {
	TotalBytes int64           `json:"total_bytes"`
	TotalHuman string          `json:"total_human"`
	Categories []CategoryUsage `json:"categories"`
}

// FormatBytes formats byte count to human-readable string.
func FormatBytes(b int64) string {
	const unit = 1024
	if b < unit {
		return fmt.Sprintf("%d B", b)
	}
	div, exp := int64(unit), 0
	for n := b / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %cB", float64(b)/float64(div), "KMGTPE"[exp])
}

func dirSize(path string) int64 {
	var total int64
	_ = filepath.Walk(path, func(_ string, info fs.FileInfo, err error) error {
		if err == nil && info != nil && !info.IsDir() {
			total += info.Size()
		}
		return nil
	})
	return total
}

// CalculateStats scans the host cache directory and computes category usage.
func CalculateStats(hostCacheDir string) CacheStats {
	if hostCacheDir == "" {
		return CacheStats{TotalBytes: 0, TotalHuman: "0 B", Categories: []CategoryUsage{}}
	}

	entries, err := os.ReadDir(hostCacheDir)
	if err != nil {
		return CacheStats{TotalBytes: 0, TotalHuman: "0 B", Categories: []CategoryUsage{}}
	}

	var totalBytes int64
	var categories []CategoryUsage

	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		catPath := filepath.Join(hostCacheDir, entry.Name())
		size := dirSize(catPath)
		totalBytes += size
		categories = append(categories, CategoryUsage{
			Category:      entry.Name(),
			Bytes:         size,
			HumanReadable: FormatBytes(size),
		})
	}

	return CacheStats{
		TotalBytes: totalBytes,
		TotalHuman: FormatBytes(totalBytes),
		Categories: categories,
	}
}
