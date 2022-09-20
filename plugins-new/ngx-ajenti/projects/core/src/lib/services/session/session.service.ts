import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NavigationEnd, Router } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { IdentityService } from '../identity/identity.service';


const DEFAULT_TIME_LEFT_IN_SECONDS = 3600; // 1 hour


/**
 * Provides session relevant functionalities.
 */
@Injectable({
  providedIn: 'root',
})
export class SessionService {

  /**
   * Defines the time in seconds which is left until the session expires.
   */
  public timeLeftInSeconds: BehaviorSubject<number>;

  /**
   * Determines if the session does expire soon.
   */
  public sessionExpiresSoon: BehaviorSubject<boolean>;

  /**
   * Determines if the session is already expired.
   */
  public isSessionExpired: BehaviorSubject<boolean>;

  private countDownInterval: ReturnType<typeof setTimeout> | null;


  constructor(
    private httpClient: HttpClient,
    private routerService: Router,
    private identityService: IdentityService,
  ) {
    this.countDownInterval = null;
    this.sessionExpiresSoon = new BehaviorSubject<boolean>(false);
    this.timeLeftInSeconds = new BehaviorSubject<number>(DEFAULT_TIME_LEFT_IN_SECONDS);
    this.isSessionExpired = new BehaviorSubject<boolean>(false);

    this.timeLeftInSeconds.subscribe(this.onTimeLeftInSecondsChanged);
    this.isSessionExpired.subscribe((isSessionTimedOut) => this.onIsSessionTimedOutChanged(isSessionTimedOut));
    this.routerService.events.subscribe(this.onRouterServiceEvent);

    this.initialize();
  }


  private clearCountDownInterval = (): void => {
    if (!this.countDownInterval) {
      return;
    }

    clearInterval(this.countDownInterval);
    this.timeLeftInSeconds.next(DEFAULT_TIME_LEFT_IN_SECONDS);
    this.countDownInterval = null;
  };

  private countDown = (): void => {
    const timeLeftInSeconds = this.timeLeftInSeconds.value;

    if (timeLeftInSeconds > 0) {
      this.timeLeftInSeconds.next(timeLeftInSeconds - 1);
    }
  };

  private async initialize() {
    if (!this.identityService.identity.value?.isUserSignedIn) {
      await this.clearCountDownInterval();
      return;
    }

    await this.updateTimeLeftFromBackend();
    await this.initializeCounter();
  }

  private initializeCounter = (): void => {
    if (this.countDownInterval) {
      return;
    }

    this.countDownInterval = setInterval(this.countDown, 1000);
  };

  private async onIsSessionTimedOutChanged(isSessionTimedOut: boolean): Promise<void> {
    if (!isSessionTimedOut) {
      return;
    }

    await this.identityService.logout();
    await this.clearCountDownInterval();
  }

  private onRouterServiceEvent = async (event: unknown): Promise<void> => {
    if (event instanceof NavigationEnd) {
      await this.initialize();
    }
  };

  private onTimeLeftInSecondsChanged = async (timeLeftInSeconds: number): Promise<void> => {
    this.updateSessionExpiresSoon(timeLeftInSeconds);
    this.updateIsSessionExpired(timeLeftInSeconds);
  };

  private updateIsSessionExpired(timeLeftInSeconds: number): void {
    const isSessionExpired = timeLeftInSeconds <= 0;
    this.isSessionExpired.next(isSessionExpired);
  };

  private updateSessionExpiresSoon(timeLeftInSeconds: number): void {
    const isCriticalTimeReached = timeLeftInSeconds <= 1800; // 30 min
    this.sessionExpiresSoon.next(isCriticalTimeReached);
  };

  private async updateTimeLeftFromBackend(): Promise<void> {
    const timeLeftInSeconds = await this.httpClient.get<number>('/api/core/session-time').toPromise();
    this.timeLeftInSeconds.next(timeLeftInSeconds || 0);
  }
}
