const VM_BACKEND_HINTS = ["vm", "orb", "multipass", "wsl"];

/** Whether a runner backend (orbstack, orbstack-vm, multipass, wsl2, ...) is a VM rather than a container. */
export function isVmBackend(backend: string | undefined): boolean {
  if (!backend) return false; // no backend means the default, docker
  const engine = backend.toLowerCase();
  return VM_BACKEND_HINTS.some((hint) => engine.includes(hint));
}
