import { describe, expect, it } from "vitest";
import { isVmBackend } from "./backend";

describe("isVmBackend", () => {
  it.each([
    ["orbstack", true],
    ["OrbStack-VM", true],
    ["multipass", true],
    ["wsl2", true],
    ["docker", false],
    ["", false],
    [undefined, false],
  ])("%s is a VM: %s", (backend, vm) => {
    expect(isVmBackend(backend)).toBe(vm);
  });
});
