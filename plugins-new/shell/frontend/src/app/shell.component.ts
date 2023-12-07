import { Component, Inject, OnInit } from '@angular/core';
import { SideBarService } from './services/side-bar/side-bar.service';
import { Router } from '@angular/router';
import {
  ConfigService,
  CorePluginCustomizationSettings,
  CustomizationService,
  Identity,
  IdentityService,
  PageTitleService,
  ScreenService,
} from '@ngx-ajenti/core';
import { DOCUMENT } from '@angular/common';


@Component({
  selector: 'ajenti-shell',
  templateUrl: './shell.component.html',
  styleUrls: [ './shell.component.less' ],
})
export class ShellComponent implements OnInit {

  public appReady: boolean;
  public isWidescreen: boolean;
  public showOverlaySidebar: boolean;
  public showSidebar: boolean;
  public corePluginCustomizations: CorePluginCustomizationSettings;


  constructor(
    public sideBarService: SideBarService,
    private identityService: IdentityService,
    private screenService: ScreenService,
    private customizationService: CustomizationService,
    private pageTitleService: PageTitleService,
    private routerService: Router,
    private configService: ConfigService,
    @Inject(DOCUMENT) private document: Document,
  ) {
    this.appReady = false;
    this.isWidescreen = false;
    this.showSidebar = false;
    this.showOverlaySidebar = false;
    this.corePluginCustomizations = new CorePluginCustomizationSettings();
  }

  async ngOnInit() {
    this.screenService
      .getIsWidescreen()
      .subscribe(isWidescreen => {
        this.isWidescreen = isWidescreen;
      });
    this.sideBarService
      .getShowSidebar()
      .subscribe(showSidebar => {
        this.showSidebar = showSidebar;
      });
    this.sideBarService
      .getShowOverlaySidebar()
      .subscribe(showOverlaySidebar => {
        this.showOverlaySidebar = showOverlaySidebar;
      });
    this.customizationService
      .getPluginCustomizations<CorePluginCustomizationSettings>('core')
      .subscribe(pluginCustomizations => {
        this.corePluginCustomizations = pluginCustomizations;
        this.setBodyCssClasses();
      });

    this.identityService.identity.subscribe(this.onIdentityChanged);
  }


  public setBodyCssClasses(): void {
    const { cssClass } = this.corePluginCustomizations;
    const themeColor = this.corePluginCustomizations.themeColor;
    const cssClasses: string[] = [
      'app-component',
      `global-color-${ themeColor }`,
      `widescreen-mode-${ this.isWidescreen ? 'on' : 'off' }`,
    ];

    if (cssClass) {
      cssClasses.push(cssClass);
    }
    const classListCopy = Array.from(this.document.body.classList);
    classListCopy.forEach((className) => {this.document.body.classList.remove(className)});
    cssClasses.forEach(cssClass => this.document.body.classList.add(cssClass));
  }

  public get isLoginViewOpen(): boolean {
    return !this.routerService.url.includes('view/login');
  }

  private onIdentityChanged = async (identity: Identity | null): Promise<void> => {
    if (!identity) {
      return;
    }

    console.info(`Identity "${ identity.user }"`);

    try {
      this.pageTitleService.init();

      const isLoginViewOpen = this.routerService.url.includes('/view/login');
      if (!isLoginViewOpen && !identity.isUserSignedIn) {
        await this.routerService.navigate([ 'view/login/normal' ]);
      }

      await this.configService.load();
    } catch (error: any) {
      if (!error) {
        return;
      }

      if (error.message) {
        console.error(error.message);
      } else {
        console.error(error);
      }
    } finally {
      this.appReady = true;
    }
  };
}
