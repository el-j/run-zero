// Mutation testing for the dashboard: Stryker changes src/ one operator or
// literal at a time and re-runs the Vitest suite; a change no test notices
// "survives". Run with `pnpm run mutate` (or `make mutate-web`).
// See ../MUTATION_TESTING.md.

/** @type {import('@stryker-mutator/api/core').PartialStrykerOptions} */
export default {
  testRunner: "vitest",
  plugins: ["@stryker-mutator/vitest-runner"],
  vitest: { configFile: "vite.config.ts" },
  mutate: ["src/**/*.ts", "!src/**/*.test.ts", "!src/types/api.ts"],
  coverageAnalysis: "perTest",
  // Stryker rewrites the sandbox's tsconfig with the TypeScript JS API, which
  // TypeScript 7 (the native compiler) no longer ships. Our tsconfig has no
  // extends or project references to rewrite, so point Stryker at a file
  // that does not exist and it skips the rewrite.
  tsconfigFile: "tsconfig.stryker-skip.json",
  reporters: ["clear-text", "progress", "html"],
  htmlReporter: { fileName: "reports/mutation/index.html" },
  incremental: true,
  incrementalFile: "reports/stryker-incremental.json",
  // break is the baseline from the first full run (72.47%); raise it as
  // survivors are killed. See ../MUTATION_TESTING.md.
  thresholds: { high: 95, low: 85, break: 72 },
};
