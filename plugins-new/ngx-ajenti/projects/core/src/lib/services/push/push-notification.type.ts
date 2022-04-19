/**
 * Represents a push notification.
 */
export type PushNotification = {

  /**
   * Defines the plugin identifier which sent the notification.
   */
  plugin: string;

  /**
   * Defines the type of the push notification.
   */
  type: string;

  /**
   * Defines the message.
   */
  message: any;
}
