import type { IMessage, StompConfig } from "@stomp/stompjs";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createStompConnectionManager } from "@/composables/websocket/stomp-connection-manager";

class FakeClient {
  active = false;
  connected = false;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onWebSocketClose?: (_event: CloseEvent) => void;
  onStompError?: (_frame: { body?: string; headers?: Record<string, string | undefined> }) => void;
  readonly activate = vi.fn(() => {
    this.active = true;
  });
  readonly deactivate = vi.fn(() => {
    this.active = false;
    this.connected = false;
  });
  readonly subscriptions = new Map<string, { unsubscribe: ReturnType<typeof vi.fn> }>();

  constructor(readonly config: StompConfig) {}

  subscribe(destination: string, callback: (_message: IMessage) => void) {
    const subscription = { id: destination, unsubscribe: vi.fn(), callback };
    this.subscriptions.set(destination, subscription);
    return subscription;
  }
}

function createLoggerMock() {
  return {
    debug: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  };
}

describe("createStompConnectionManager", () => {
  let clients: FakeClient[];

  beforeEach(() => {
    vi.useFakeTimers();
    clients = [];
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  function createManager(options: { token?: string; brokerURL?: string } = {}) {
    return createStompConnectionManager({
      brokerURL: options.brokerURL ?? "ws://localhost/ws",
      clientFactory: (config) => {
        const client = new FakeClient(config);
        clients.push(client);
        return client;
      },
      connectionTimeout: 100,
      getToken: () => options.token ?? "access-token",
      logger: createLoggerMock(),
      maxReconnectAttempts: 2,
      reconnectDelay: 50,
    });
  }

  it("does not activate client when token is missing", () => {
    const manager = createManager({ token: "" });

    manager.connect();

    expect(clients).toHaveLength(0);
    expect(manager.getSnapshot()).toMatchObject({ isConnected: false, reconnectCount: 0 });
  });

  it("activates only once while connection is pending", () => {
    const manager = createManager();

    manager.connect();
    manager.connect();

    expect(clients).toHaveLength(1);
    expect(clients[0].activate).toHaveBeenCalledTimes(1);
  });

  it("subscribes and clears subscriptions on manual disconnect", () => {
    const manager = createManager();
    manager.connect();
    clients[0].connected = true;
    clients[0].onConnect?.();

    const subscriptionId = manager.subscribe("/topic/dict", vi.fn());
    manager.disconnect();

    expect(subscriptionId).toBe("/topic/dict");
    expect(clients[0].subscriptions.get("/topic/dict")?.unsubscribe).toHaveBeenCalled();
    expect(clients[0].deactivate).toHaveBeenCalled();
    expect(manager.getSnapshot()).toMatchObject({ isConnected: false, reconnectCount: 0 });
  });

  it("reconnects after abnormal close but not after manual disconnect", () => {
    const manager = createManager();
    manager.connect();
    clients[0].connected = true;
    clients[0].onConnect?.();

    clients[0].connected = false;
    clients[0].onWebSocketClose?.({ code: 1006, reason: "abnormal" } as CloseEvent);
    vi.advanceTimersByTime(50);

    expect(clients).toHaveLength(1);
    expect(clients[0].activate).toHaveBeenCalledTimes(2);

    clients[0].connected = true;
    clients[0].onConnect?.();
    manager.disconnect();
    clients[0].connected = false;
    clients[0].onWebSocketClose?.({ code: 1006, reason: "manual" } as CloseEvent);
    vi.advanceTimersByTime(50);

    expect(clients).toHaveLength(1);
    expect(clients[0].activate).toHaveBeenCalledTimes(2);
  });
});
