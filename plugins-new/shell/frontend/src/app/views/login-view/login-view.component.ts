import { Component, OnInit } from '@angular/core';
import {
  AuthenticationModes,
  CorePluginCustomizationSettings, CustomizationService,
  IdentityService,
  TranslateService,
} from '@ngx-ajenti/core';
import { ActivatedRoute, Router } from '@angular/router';


@Component({
  selector: 'app-login-view',
  templateUrl: './login-view.component.html',
  styleUrls: [ './login-view.component.less' ],
})
export class LoginViewComponent implements OnInit {

  public corePluginCustomizations: CorePluginCustomizationSettings;
  public working: boolean;
  public success: boolean;
  public username: string;
  public password: string;
  public redirectPath?: string;
  public mode: AuthenticationModes;
  public showPassword: boolean;

  constructor(
    private route: ActivatedRoute,
    private routerService: Router,
    private translateService: TranslateService,
    private customizationService: CustomizationService,
    private identityService: IdentityService,
  ) {
    this.corePluginCustomizations = new CorePluginCustomizationSettings();
    this.working = false;
    this.success = false;
    this.username = '';
    this.password = '';
    this.mode = AuthenticationModes.Normal;
    this.showPassword = false;
  }

  ngOnInit(): void {
    this.customizationService
      .getPluginCustomizations<CorePluginCustomizationSettings>('core')
      .subscribe(pluginCustomizations => {
        this.corePluginCustomizations = pluginCustomizations;
      });
    this.route.queryParams.subscribe(queryParams => {
      this.redirectPath = queryParams['redirectPath'];
    });
    this.route.params.subscribe(params => {
      this.username = params['username'];
      this.mode = params['mode'];
    });
  }

  public async login(): Promise<void> {
    if (!this.username || !this.password) {
      return;
    }
    this.working = true;
    this.username = this.username.toLowerCase();

    try {
      await this.identityService.authenticate(this.username, this.password, this.mode);

      this.success = true;

      const path = this.corePluginCustomizations.loginRedirectionPath || this.redirectPath || '/';
      await this.routerService.navigate([ path ]);
    } catch (error) {
      this.working = false;
      console.log('Authentication failed', error);
      // TODO: notify.error(gettext('Authentication failed'));
      console.error(this.translateService.instant('Authentication failed'));
    }
  }

  public toggleShowPassword(): void {
    this.showPassword = !this.showPassword;
  }

}
