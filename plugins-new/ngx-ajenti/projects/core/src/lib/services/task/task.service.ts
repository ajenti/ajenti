import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { TranslateService } from '@ngx-translate/core';
import { Deferred } from '../../common/deferred';
import { PushService } from '../push/push.service';
import { NotificationService } from '../notification/notification.service';
import { SocketService } from '../socket/socket.service';
import { Task } from './task.model';
import { PushNotification } from '../push/push-notification.type';

/**
 * Provides task related functionalities.
 */
@Injectable({
  providedIn: 'root',
})
export class TaskService {

  /**
   * Defines the currently running tasks.
   */
  public tasks: BehaviorSubject<Task[]>;

  private readonly deferredTasks: { [taskId: string]: Deferred<void> };

  constructor(
    private httpClient: HttpClient,
    private pushService: PushService,
    private notifyService: NotificationService,
    private socketService: SocketService,
    private translateService: TranslateService,
  ) {
    this.tasks = new BehaviorSubject<Task[]>([]);
    this.deferredTasks = {};

    this.socketService.events.subscribe(event => {
      if (event.type === 'connect') {
        this.requestTasksUpdate();
      }
    });
    this.pushService.pushNotification.subscribe(this.onPushNotificationEmitted);
  }

  /**
   * Starts a task.
   *
   * @param cls Defines the unique class name of the task.
   * @param args Defines the arguments of the task.
   * @param kwargs Defines the keyword arguments of the task.
   *
   * @returns the id and the promise of the task.
   */
  public async start(cls: string, args: string[] = [], kwargs: string[] = []): Promise<{ id: string; promise: Promise<void>; }> {
    const data = {
      cls,
      args,
      kwargs,
    };

    const taskId = await this.httpClient.post<string>('/api/core/tasks/start', data).toPromise() || '';
    const taskDeferred = new Deferred<void>();
    this.deferredTasks[taskId] = taskDeferred;

    return {
      id: taskId,
      promise: taskDeferred.promise,
    };
  }

  private onPushNotificationEmitted = (notification: PushNotification): void => {
    if (notification.plugin !== 'push' && notification.message.plugin !== 'tasks') {
      return;
    }
    const taskMessage = notification.message.message;

    switch (taskMessage.type) {
      case 'update':
        this.updateTasks(taskMessage.tasks);
        break;
      case 'message':
        if (taskMessage.type === 'done') {
          const deferred = this.deferredTasks[taskMessage.task.id];
          if (deferred) {
            deferred.resolve();
          }

          this.notifyService.success(
            this.translateService.instant(taskMessage.task.name),
            this.translateService.instant('Done'),
          );
        } else if (taskMessage.type === 'expection') {
          const deferred = this.deferredTasks[taskMessage.task.id];
          if (deferred) {
            deferred.reject(notification.message);
          }

          this.notifyService.error(
            this.translateService.instant(taskMessage.task.name),
            this.translateService.instant(`Failed: ${ taskMessage.exception }`),
          );
        }
        break;

      default:

    }
  };

  private updateTasks(tasks: Task[]) {
    this.tasks.next(tasks);
  }

  private requestTasksUpdate(): Promise<void> {
    return this.httpClient.get<void>('/api/core/tasks/request-update').toPromise();
  }
}
