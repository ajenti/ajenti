import { SocketServiceEventTypes } from './socket-service-event-types.type';


/**
 * Socket service related event.
 */
export class SocketServiceEvent {

  constructor(type: SocketServiceEventTypes) {
    this.type = type;
  }

  /**
   * Defines the type of the event.
   */
  public type: SocketServiceEventTypes;

}
