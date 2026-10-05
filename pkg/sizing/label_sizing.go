package sizing

import (
	"regexp"
	"strconv"
	"strings"
)

var customTierRe = regexp.MustCompile(`^(\d+)cpu-(\d+)g[ib]*$`)

// ParseLabelSizing extracts dynamic resource allocations declared in job labels.
func ParseLabelSizing(labels []string) (cpus *int, memoryMiB *int) {
	for _, l := range labels {
		label := strings.ToLower(strings.TrimSpace(l))

		if m := customTierRe.FindStringSubmatch(label); m != nil {
			c, errC := strconv.Atoi(m[1])
			g, errG := strconv.Atoi(m[2])
			if errC == nil && errG == nil && c > 0 && g > 0 {
				mem := g * 1024
				return &c, &mem
			}
		}

		switch label {
		case "xlarge":
			c := 8
			m := 16384
			return &c, &m
		case "large":
			c := 4
			m := 8192
			return &c, &m
		case "medium":
			c := 2
			m := 4096
			return &c, &m
		case "small":
			c := 1
			m := 2048
			return &c, &m
		case "highmem":
			m := 32768
			memoryMiB = &m
		}
	}
	return cpus, memoryMiB
}
