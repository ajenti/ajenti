// @ts-ignore
import * as io from 'socket.io-client/dist/socket.io.js'; // TODO: Update socket.io get a fixed version of the lib.
import { EventEmitter, Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { SocketServiceEvent } from './socket-service-event.model';
import { socketIoConfig } from '../../common/socket-io.config';
import { PluginMessageReceived } from './plugin-event.model';

/**
 * Provides socket.io related functionalities.
 */
@Injectable({
  providedIn: 'root',
})
export class SocketService {

  /**
   * Emits socket service relevant events.
   */
  public events: EventEmitter<SocketServiceEvent>;

  private socketConnectionLost: BehaviorSubject<boolean>;
  private socket: { // TODO: Create or even better import types
    on: (event: string, callback: (event: any) => void) => void;
    emit: (ev: any, ...data: any) => void;
  };


  constructor() {
    this.events = new EventEmitter<SocketServiceEvent>();
    this.socketConnectionLost = new BehaviorSubject<boolean>(false);
    this.socket = io.connect('/socket', socketIoConfig);
    this.attachEventHandler();
  }


 /**
   * Sends a message via the socket.
   *
   * @param senderPluginName The name of the plugin which sends a message.
   * @param messageData The data of a plugin which represents the message.
   *
   * @returns A promise which resolves if the message was send successfully.
   */
  public send(senderPluginName: string, messageData: any): Promise<void> {
    return new Promise<void>((resolve) => {
      const msg = {
        plugin: senderPluginName,
        data: messageData,
      };

      this.socket.emit('message', msg, () => resolve());
    });
  }

  private attachEventHandler(): void {
    this.socket.on('connecting', this.onSocketConnecting);
    this.socket.on('connect_failed', this.onSocketConnectFailed);
    this.socket.on('reconnecting', this.onSocketReconnecting);
    this.socket.on('reconnect', this.onSocketReconnect);
    this.socket.on('connect', this.onSocketConnect);
    this.socket.on('disconnect', this.onSocketDisconnect);
    this.socket.on('error', this.onSocketError);
    this.socket.on('message', this.onSocketMessage);
  }

  private onSocketReconnect = (): void => {
    this.socketConnectionLost.next(false);
    console.log('Socket has reconnected');
    this.events.emit(new SocketServiceEvent('reconnect'));
  };

  private onSocketConnect = (): void => {
    this.socketConnectionLost.next(false);
    console.log('Socket has connected');
    this.events.emit(new SocketServiceEvent('connect'));
  };

  private onSocketConnecting = (): void => {
    console.log('Socket is connecting');
  };

  private onSocketConnectFailed = (error: string): void => {
    console.log('Socket is connection failed', error);
  };

  private onSocketReconnecting = (): void => {
    console.log('Socket is reconnecting');
  };

  private onSocketDisconnect = (error: string): void => {
    this.socketConnectionLost.next(true);
    console.error('Socket has disconnected', error);
    this.events.emit(new SocketServiceEvent('disconnect'));
  };

  private onSocketError = (error: string): void => {
    this.socketConnectionLost.next(true);
    console.error('Error', error);
    this.events.emit(new SocketServiceEvent('error'));
  };

  private onSocketMessage = (socketMessage: any): void => {
    if (socketMessage[0] === '{') {
      socketMessage = JSON.parse(socketMessage);
    }
    console.debug('Socket message from', socketMessage.plugin, socketMessage.data);

    this.events.emit(new PluginMessageReceived(socketMessage.plugin, socketMessage.data));
  };

}
