import { Type } from '@angular/core';
import { DataInterface } from './data.interface';

/**
 * Represents a message box.
 */
export class MessageBox<T = any> {

  constructor(
    close: (message: MessageBox<T>) => Promise<void>,
    text: string = '', promptLabel: string = '', value: string = '',
    acceptButtonLabel: string = '', cancelButtonLabel: string = '', visible: boolean = false,
    scrollable: boolean = false, inProgress: boolean = false,
    title: string = '', injectedComponent?: Type<any>, injectedComponentData?: any,
  ) {

    this.visible = visible;
    this.scrollable = scrollable;
    this.close = () => {
      return close(this);
    };
    this.inProgress = inProgress;
    this.text = text;
    this.title = title;
    this.value = value;
    this.promptLabel = promptLabel;
    this.acceptButtonLabel = acceptButtonLabel;
    this.cancelButtonLabel = cancelButtonLabel;
    this.injectedComponent = injectedComponent;
    this.injectedComponentData = injectedComponentData;
  }

  /**
   * Callback function which will be called if the message was accepted.
   * @param updatedData The accepted (updated) data from the dialog (messagebox).
   */
  public accepted: ((updatedData: T) => void) | undefined;

  /**
   * Callback function which will be called if the message was cancelled.
   */
  public canceled: (() => void) | undefined;

  /**
   * Closes the message within the message box service.
   */
  public close: () => Promise<void>;

  /**
   * Determines if the message is visible.
   */
  public visible: boolean;

  /**
   * Determines if the message is scrollable.
   */
  public scrollable: boolean;

  /**
   * Determines if the message is in progress.
   */
  public inProgress: boolean;

  /**
   * Defines the text of the message.
   */
  public text: string;

  /**
   * Defines a custom component to be shown inside the message box.
   */
  public injectedComponent: Type<any> | undefined;

  /**
   * Defines a custom component to be shown inside the message box.
   */
  public injectedComponentInstance: DataInterface<T> | undefined;

  /**
   * Defines the data of the injected instance
   */
  public injectedComponentData: any;

  /**
   * Defines the title of the message.
   */
  public title: string;

  /**
   * Defines the value of the message.
   */
  public value: string;

  /**
   * Defines the label for the prompt input field of the message box.
   *
   * If defined a prompt input field will be rendered.
   */
  public promptLabel: string;

  /**
   * Defines the text of the accept button.
   */
  public acceptButtonLabel: string;

  /**
   * Defines the text of the cancel button.
   */
  public cancelButtonLabel: string;

}
