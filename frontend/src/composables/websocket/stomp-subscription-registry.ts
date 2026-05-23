import type { IMessage, StompSubscription } from "@stomp/stompjs";
import type { StompClientLike, StompLogger } from "./stomp-connection-types";

export function createStompSubscriptionRegistry(logger: StompLogger) {
  const subscriptions = new Map<string, StompSubscription>();

  function subscribe(
    client: StompClientLike | null,
    destination: string,
    callback: (_message: IMessage) => void
  ) {
    if (!client || !client.connected) {
      logger.warn(`尝试订阅 ${destination} 失败: 客户端未连接`);
      return "";
    }

    try {
      const subscription = client.subscribe(destination, callback);
      subscriptions.set(subscription.id, subscription);
      logger.info(`订阅成功: ${destination}, ID: ${subscription.id}`);
      return subscription.id;
    } catch (error) {
      logger.error(`订阅 ${destination} 失败:`, error);
      return "";
    }
  }

  function unsubscribe(subscriptionId: string) {
    const subscription = subscriptions.get(subscriptionId);
    if (!subscription) {
      return;
    }
    subscription.unsubscribe();
    subscriptions.delete(subscriptionId);
    logger.debug(`已取消订阅: ${subscriptionId}`);
  }

  function clear() {
    for (const [id, subscription] of subscriptions.entries()) {
      try {
        subscription.unsubscribe();
      } catch (error) {
        logger.warn(`取消订阅 ${id} 时出错:`, error);
      }
    }
    subscriptions.clear();
  }

  return {
    clear,
    subscribe,
    unsubscribe,
  };
}
