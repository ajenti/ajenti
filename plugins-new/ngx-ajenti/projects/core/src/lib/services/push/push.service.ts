import { EventEmitter, Injectable } from '@angular/core';
import { PushNotification } from './push-notification.type';
import { SocketService } from '../socket/socket.service';
import { PluginMessageReceived } from '../socket/plugin-event.model';

/**
 * Provides access to push notifications.
 */
@Injectable({
  providedIn: 'root',
})
export class PushService {

  /**
   * Emits when a notification was received.
   */
  public pushNotification: EventEmitter<PushNotification>;

  constructor(private socketService: SocketService) {
    this.pushNotification = new EventEmitter<PushNotification>();

    socketService.events.subscribe(event => {
      if (event instanceof PluginMessageReceived) {
        this.pushNotification.emit({
          plugin: event.pluginName,
          message: event.messageData,
          type: event.type,
        });
      }
    });
  }
}
