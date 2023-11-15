import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NotificationService, TranslateService } from '@ngx-ajenti/core';
import { lastValueFrom, interval, Subscription } from 'rxjs';
import { Session } from './session.type';

@Component({
  selector: 'app-session_list',
  templateUrl: './session_list.component.html',
  styleUrls: [ './session_list.component.less' ],
})
export class Session_listComponent {

  sessions: Array<Session> = [];
  session_max_time: number = 0;
  refreshInterval = interval(15000);
  refreshSubscription: Subscription;

  constructor (
    private httpClient: HttpClient,
    private translate: TranslateService,
    private notify: NotificationService,
  ) {
    this.load_session_list();
    this.refreshSubscription = this.refreshInterval.subscribe(value => this.load_session_list());
  };

  ngOnDestroy() {
    this.refreshSubscription.unsubscribe();
  }

  public async load_session_list(): Promise<void> {
    try {
      this.sessions = await lastValueFrom(this.httpClient.get<Array<Session>>('/api/session_list/sessions'));
      this.session_max_time = 1800;
    } catch (error) {
      // error of type unknown, must be converted or be handled at top level
      this.notify.error('', 'error');
    };
  };
}
