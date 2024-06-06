import { TaskProgress } from './task-progress.model';

export class Task {

  /**
   * Defines the unique identifier of the task.
   */
  public id: string;

  /**
   * Defines the name of a task.
   */
  public name: string;

  /**
   * Defines full task class name (eg. ``aj.plugins.pluginname....``)
   */
  public cls: any;

  /**
   * Defines the task arguments.
   */
  public args: string[];

  /**
   * Defines the task keyword arguments.
   */
  public kwargs: any;

  /**
   * Contains information about the task's progress.
   */
  public progress: TaskProgress;


  /**
   * Instantiates an instance of this class.
   *
   * @param id The unique identifier of the task.
   * @param cls The unique class name of the task.
   * @param args The arguments of the task.
   * @param kwargs the keyword arguments of the task.
   */
  constructor(id: string, cls: any, args: string[], kwargs: any) {
    this.id = id;
    this.name = id;
    this.cls = cls;
    this.args = args;
    this.kwargs = kwargs;
    this.progress = {
      done: 0,
      total: 100,
      message: 'Progress',
    };
  }
}
