import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthenticationModes } from './authentication.modes';
import { NavigationEnd, Router } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { Identity } from './identity.model';
import { MachineInfo } from './machine-info.model';
import { IdentityResponse } from './identity-response.dto';
import { AuthenticationRequest } from './authentication-request.dto';
import { AuthenticationResponse } from './authentication-response.dto';


/**
 * Provides functionalities to manage user's identity.
 */
@Injectable({
  providedIn: 'root',
})
export class IdentityService {

  //<editor-fold desc="Properties...">

  /**
   * Defines the current user's identity.
   */
  public identity: BehaviorSubject<Identity | null>;

  /**
   * Defines the server's machine information.
   */
  public machine: BehaviorSubject<MachineInfo | null>;

  /**
   * The user's preferred theme color.
   */
  public themeColor: BehaviorSubject<string>;

  //</editor-fold>


  constructor(
    private httpClient: HttpClient,
    private routerService: Router,
  ) {
    this.identity = new BehaviorSubject<Identity | null>(null);
    this.machine = new BehaviorSubject<MachineInfo | null>(null);
    this.themeColor = new BehaviorSubject<string>('bluegrey');

    this.updateIdentityData().then(() => {
      this.routerService.events.subscribe(event => {
        if (event instanceof NavigationEnd) {
          const isLoginViewOpen = this.routerService.url.includes('/view/login');

          if (!isLoginViewOpen && !this.identity.value?.isUserSignedIn) {
            const redirectPath = this.routerService.url;

            this.redirectToNormalLogin(redirectPath);
          }
        }
        return false;
      });
    });
  }


  /**
   * Initializes the identity service.
   *
   * @returns A promise which resolves if the initialization was successful.
   */
  public async updateIdentityData(): Promise<void> {
    const response = await this.httpClient.get<IdentityResponse>('/api/core/identity').toPromise();
    if (!response) {
      return;
    }

    this.themeColor.next(response.color || 'bluegrey');
    this.identity.next(new Identity(response.identity));
    this.machine.next(new MachineInfo(response.machine));
  }

  /**
   * Authenticates a user to the system.
   *
   * @param username The username of the user.
   * @param password The password of the user.
   * @param mode The authentication mode to user.
   *
   * @returns A promise which resolves if the authentication was successful.
   */
  public async authenticate(username: string, password: string, mode: AuthenticationModes): Promise<void> {
    const request: AuthenticationRequest = {
      username,
      password,
      mode,
    };

    const response = await this.httpClient.post<AuthenticationResponse>('/api/core/auth', request).toPromise();
    if (!response) {
      return;
    }

    if (!response.success) {
      throw new Error(response.error);
    }

    await this.updateIdentityData();
  }

  /**
   * Elevates the current users rights.
   */
  public async elevate(): Promise<void> {
    const currentUser = this.identity.value?.user || '';
    const redirectPath = this.routerService.url;

    await this._logout();
    await this.updateIdentityData();
    await this.redirectToSudoLogin(currentUser, redirectPath);
  }

  /**
   * Logouts the current authenticated user.
   */
  public async logout(): Promise<void> {
    const redirectPath = this.routerService.url;

    await this._logout();
    await this.redirectToNormalLogin(redirectPath);
  }

  /**
   * Redirects to the login view with normal mode.
   *
   * @param redirectPath The path to redirect to. Default is /.
   *
   * @return A promise which resolves if the redirection is complete.
   */
  public redirectToNormalLogin = async (redirectPath: string = '/'): Promise<void> => {
    await this.routerService.navigate(
      [ '/view/login/normal' ],
      {
        queryParams: {
          redirectPath,
        },
      },
    );
  };


  private async _logout(): Promise<void> {
    const redirectPath = this.routerService.url;

    await this.httpClient.post('/api/core/logout').toPromise();
    await this.updateIdentityData();
    await this.redirectToNormalLogin(redirectPath);
  }

  private async redirectToSudoLogin(userToElevate: string, redirectPath: string): Promise<void> {
    await this.routerService.navigate(
      [ '/view/login/sudo', userToElevate ],
      {
        queryParams: {
          redirectPath,
        },
      },
    );
  }
}
