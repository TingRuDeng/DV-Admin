import { Client, type StompConfig } from "@stomp/stompjs";
import type { StompClientLike, StompLogger } from "./stomp-connection-types";

const DEFAULT_HEARTBEAT_MS = 4000;
const NO_RECONNECT_DELAY = 0;

interface StompClientFactoryOptions {
  brokerURL: string;
  clientFactory?: (_config: StompConfig) => StompClientLike;
  debug?: boolean;
  logger: StompLogger;
  token: string;
}

export function buildStompClient(options: StompClientFactoryOptions) {
  const config = createStompClientConfig(options);
  return options.clientFactory
    ? options.clientFactory(config)
    : (new Client(config) as StompClientLike);
}

function createStompClientConfig(options: StompClientFactoryOptions): StompConfig {
  return {
    brokerURL: options.brokerURL,
    connectHeaders: { Authorization: `Bearer ${options.token}` },
    debug: options.debug ? (message) => options.logger.debug(message) : () => {},
    heartbeatIncoming: DEFAULT_HEARTBEAT_MS,
    heartbeatOutgoing: DEFAULT_HEARTBEAT_MS,
    reconnectDelay: NO_RECONNECT_DELAY,
  };
}
