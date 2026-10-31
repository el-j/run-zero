package config

import "testing"

func TestVMTriggerLabelsDedupAndBlank(t *testing.T) {
	cfg, err := LoadConfig(MapEnv{"VM_TRIGGER_LABELS": "VM, ,db,vm"})
	if err != nil {
		t.Fatal(err)
	}
	if len(cfg.VMTriggerLabels) != 2 {
		t.Errorf("got %v", cfg.VMTriggerLabels)
	}
}
