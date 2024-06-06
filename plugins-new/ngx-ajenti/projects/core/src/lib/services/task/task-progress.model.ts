/**
 * Represents a Ajenti task.
 */
export class TaskProgress {

  /**
   * Defines the message of the progress (eg. ``archiving...``).
   */
  public message: string;

  /**
   * Defines the number of done steps.
   */
  public done: number;

  /**
   * Defines the number of total steps.
   */
  public total: number;


  constructor(message: string, done: number, total: number) {
    this.message = message;
    this.done = done;
    this.total = total;
  }

}
