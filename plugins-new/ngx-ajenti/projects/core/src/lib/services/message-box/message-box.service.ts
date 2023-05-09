/**
 * Provides functionalities to handle message boxes.
 */
import { BehaviorSubject, Observable } from 'rxjs';
import { MessageBox } from './message-box.model';
import { Injectable, Type } from '@angular/core';
import { MessageBoxParams } from './message-box-params.interface';

@Injectable({
  providedIn: 'platform',
})
export class MessageBoxService {

  private readonly _messageBoxes: BehaviorSubject<MessageBox[]>;

  constructor() {
    this._messageBoxes = new BehaviorSubject<MessageBox[]>([]);
  }

  /**
   * Message boxed to be rendered by the message box container.
   */
  public get messageBoxes(): Observable<MessageBox[]> {
    return this._messageBoxes.asObservable();
  };

  /**
   * Shows a message box.
   *
   * @param text The text to be shown in the message box.
   * @param title Defines the title of the message box.
   * @param promptText The text to be shown in a message box of type prompt.
   * @param promptInitialValue The initial value of the prompt's input field.
   * @param acceptButtonLabel The label of the accept button.
   * @param cancelButtonLabel The label of the cancel button.
   * @param visible Determines if the message box is visible or not.
   * @param scrollable Determines if the message box is scrollable or not.
   * @param progress Determines if the message box indicates progress.
   * @param injectedComponent The type of the component to be injected as inner component.
   * @param injectComponentData The data of the injected component.
   *
   * @returns The shown message box object.
   */
  public show(params: Partial<MessageBoxParams> ): MessageBox {
    const defaultValues = {
      text: '',
      title: '',
      promptText: '',
      promptInitialValue: '',
      acceptButtonLabel: '',
      cancelButtonLabel: '',
      visible: true,
      scrollable: false,
      progress: false,
      injectedComponent: undefined,
      injectComponentData: '',
    };
    const options = {...defaultValues, ...params};
    const messageBox = new MessageBox(
      this.close,
      options.text,
      options.promptText,
      options.promptInitialValue,
      options.acceptButtonLabel,
      options.cancelButtonLabel,
      options.visible,
      options.scrollable,
      options.progress,
      options.title,
      options.injectedComponent,
      options.injectComponentData,
    );

    const messageBoxes = this._messageBoxes.value;
    messageBoxes.push(messageBox);
    this._messageBoxes.next(messageBoxes);

    return messageBox;
  }

  /**
   * Shows a message box with a prompt to input a text.
   *
   * @param label The label of the prompt.
   * @param initialValue The initial input value of the prompt.
   *
   * @returns The shown message box object.
   */
  public prompt(label: string, initialValue: string = ''): MessageBox {
    return this.show({title: label, promptInitialValue:initialValue, acceptButtonLabel: 'OK', cancelButtonLabel: 'Cancel'});
  }

  /**
   * Closes a message of the message box.
   *
   * @param messageBox The message to be closed.
   *
   * @returns A promise which resolves as soon as the message is closed.
   */
  public close = (messageBox: MessageBox): Promise<void> => {
    messageBox.visible = false;

    const promise = new Promise<void>(resolve => {
      setTimeout(() => {
        const messageBoxesToKeepOpen = this._messageBoxes.value
          .filter(m => m !== messageBox);

        this._messageBoxes.next(messageBoxesToKeepOpen);

        resolve();
      }, 1000);
    });

    return promise;
  };

}
