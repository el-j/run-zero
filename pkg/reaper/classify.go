package reaper

// Classify decides what action to apply to a runner based on age and GitHub registration status.
// Pure function: no I/O, strict age checks (>).
func Classify(ageSeconds float64, reg *Registration, registryConclusive bool, timeouts Timeouts) Action {
	if reg == nil {
		if registryConclusive && ageSeconds > float64(timeouts.UnregisteredSeconds) {
			return ActionReapUnregistered
		}
		return ActionKeep
	}

	if reg.Busy {
		if ageSeconds > float64(timeouts.BusySeconds) {
			return ActionCheckStaleBusy
		}
		return ActionKeep
	}

	if ageSeconds > float64(timeouts.IdleSeconds) {
		return ActionReapIdle
	}

	return ActionKeep
}
