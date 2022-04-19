import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { SideBarService } from '../../services/side-bar/side-bar.service';
import {
  CorePluginCustomizationSettings,
  CustomizationService,
  Identity,
  IdentityService,
  MachineInfo,
  PageTitleService,
  ScreenService,
  SessionService,
} from '@ngx-ajenti/core';


@Component({
  selector: 'app-nav-bar',
  templateUrl: './nav-bar.component.html',
  styleUrls: [ './nav-bar.component.less' ],
})
export class NavBarComponent implements OnInit {

  public corePluginCustomizations: CorePluginCustomizationSettings;
  public isWidescreen: boolean;
  public pageTitle: string;
  public showSessionTimer: boolean;
  public timeLeftInSeconds: number;
  public urlPrefix: string;
  public identity?: Identity | null;
  public machine?: MachineInfo | null;


  constructor(
    private customizationService: CustomizationService,
    private identityService: IdentityService,
    private pageTitleService: PageTitleService,
    private router: Router,
    private screenService: ScreenService,
    private sessionService: SessionService,
    private sideBarService: SideBarService,
  ) {
    this.corePluginCustomizations = new CorePluginCustomizationSettings();
    this.isWidescreen = false;
    this.pageTitle = '';
    this.showSessionTimer = false;
    this.timeLeftInSeconds = 0;
    this.urlPrefix = '';
    this.identity = null;
    this.machine = null;

    this.sessionService.timeLeftInSeconds.subscribe(this.onSessionTimeInSecondsChanged);
    this.sessionService.sessionExpiresSoon.subscribe(this.onSessionExpiresSoonChanged);
  }

  ngOnInit(): void {
    this.screenService
      .getIsWidescreen()
      .subscribe(isWidescreen => {
        this.isWidescreen = isWidescreen;
      });

    this.customizationService
      .getPluginCustomizations<CorePluginCustomizationSettings>('core')
      .subscribe(pluginCustomizations => {
        this.corePluginCustomizations = pluginCustomizations;
      });

    this.pageTitleService
      .getTitle()
      .subscribe(pageTitle => {
        this.pageTitle = pageTitle;
      });

    this.identityService.identity.subscribe(identity => {
      this.identity = identity;
    });

    this.identityService.machine.subscribe(machine => {
      this.machine = machine;
    });
  }


  public toggleOverlayNavigation() {
    this.sideBarService.toggleShowOverlaySideBar();
  }

  public isNavigationPresent(): boolean {
    return !this.router.url.includes('/view/login');
  }

  public getProfileButtonCSSClasses(): string {
    const classes = [
      'btn',
      'btn-default',
      'profile-button',
    ];

    if (this.identityService.identity.value?.isSuperuser) {
      classes.push('superuser');
    }

    return classes.join(' ');
  }

  public onElevateMenuItemClick(): void {
    this.identityService.elevate();
  }

  public onLogoutMenuItemClick(): void {
    this.identityService.logout();
  }

  public onToggleNavigationClick(): void {
    this.sideBarService.toggleShowSideBar();
  }

  public onToggleWidescreenClick(): void {
    this.screenService.toggleIsWidescreen();
  };

  private onSessionTimeInSecondsChanged = (timeLeftInSeconds: number): void => {
    this.timeLeftInSeconds = timeLeftInSeconds;
  };

  private onSessionExpiresSoonChanged = (sessionExpiresSoon: boolean): void => {
    this.showSessionTimer = sessionExpiresSoon;
  };

}
