/**
 * Defines a `Deferred` object which represents a task which will finish in the future.
 */
export class Deferred<T> {

  /**
   * The promise which resolves if the deferred task is finished.
   */
  public promise: Promise<T>;

  /**
   * The resolve callback which will be called if the task is finished successfully.
   */
  public resolve: (value: T | PromiseLike<T>) => void;

  /**
   * The reject callback which will be called if the task could not be finished.
   */
  public reject: (reason?: any) => void;


  constructor() {
    this.reject = () => {};
    this.resolve = () => {};

    this.promise = new Promise<T>((resolve, reject) => {
      this.resolve = resolve;
      this.reject = reject;
    });
  }
}
