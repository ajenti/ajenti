import { SocketServiceEvent } from './socket-service-event.model';


/**
 * Defines a socket message received from a plugin.
 */
export class PluginMessageReceived extends SocketServiceEvent {

  constructor(pluginName: string, data: any) {
    super('message');

    this.pluginName = pluginName;
    this.messageData = data;
  }

  /**
   * The name of the plugin which sent the message.
   */
  public pluginName: string;

  /**
   * The message data.
   */
  public messageData: any;

}
