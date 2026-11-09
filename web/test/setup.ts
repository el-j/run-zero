import { afterEach, beforeEach, vi } from "vitest";

/** Simulated viewport width used by the matchMedia stub. */
export const viewport = { width: 1200 };

/** Minimal EventSource stand-in that lets tests emit server events. */
export class FakeEventSource {
  static instances: FakeEventSource[] = [];
  onerror: ((e: Event) => void) | null = null;
  closed = false;
  private listeners = new Map<string, Array<(e: MessageEvent) => void>>();

  readonly url: string;

  constructor(url: string) {
    this.url = url;
    FakeEventSource.instances.push(this);
  }

  addEventListener(type: string, fn: (e: MessageEvent) => void): void {
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), fn]);
  }

  close(): void {
    this.closed = true;
  }

  emit(type: string, data: string): void {
    for (const fn of this.listeners.get(type) ?? []) fn({ data } as MessageEvent);
  }
}

Object.defineProperty(window, "matchMedia", {
  configurable: true,
  writable: true,
  value: (query: string) => {
    const max = /max-width:\s*(\d+)px/.exec(query);
    const min = /min-width:\s*(\d+)px/.exec(query);
    const matches = max
      ? viewport.width <= Number(max[1])
      : min
        ? viewport.width >= Number(min[1])
        : false;
    return { matches, media: query };
  },
});

HTMLDialogElement.prototype.showModal = function showModal(this: HTMLDialogElement) {
  this.open = true;
};
HTMLDialogElement.prototype.close = function close(this: HTMLDialogElement) {
  this.open = false;
};
Element.prototype.scrollIntoView = function scrollIntoView() {};
(globalThis as unknown as { EventSource: typeof FakeEventSource }).EventSource = FakeEventSource;

beforeEach(() => {
  viewport.width = 1200;
  FakeEventSource.instances = [];
  localStorage.clear();
  delete document.body.dataset.shellRendered;
  document.body.className = "";
  document.body.innerHTML = "";
});

afterEach(() => {
  document.body.innerHTML = "";
  vi.useRealTimers();
});
