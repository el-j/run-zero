/**
 * Late-bound callbacks that let the render/action modules trigger data reloads
 * without importing the data layer (which would create an import cycle).
 * The bootstrap wires the real implementations.
 */
export const hooks = {
  /** Reloads the fleet state from the server. */
  refreshState: async (): Promise<void> => {},
  /** Reloads cache statistics from the server. */
  loadCacheStats: async (): Promise<void> => {},
};
