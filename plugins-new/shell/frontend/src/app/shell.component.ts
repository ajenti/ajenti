import { Component, OnInit } from '@angular/core';
import { SideBarService } from './services/side-bar/side-bar.service';
import { Meta } from '@angular/platform-browser';
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
    private metaService: Meta,
    private identityService: IdentityService,
    private screenService: ScreenService,
    private customizationService: CustomizationService,
    private pageTitleService: PageTitleService,
    private routerService: Router,
    private configService: ConfigService,
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
      });

    this.identityService.identity.subscribe(this.onIdentityChanged);
  }


  public getComponentCssClasses(): string {
    const { bodyClass } = this.corePluginCustomizations;
    const themeColor = this.identityService.themeColor.value;

    const cssClasses: string[] = [
      'app-component',
      `global-color-${ themeColor }`,
      `widescreen-mode-${ this.isWidescreen ? 'on' : 'off' }`,
    ];

    if (bodyClass) {
      cssClasses.push(bodyClass);
    }

    return cssClasses.join(' ');
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
      this.metaService.addTag({
        name: 'theme-color',
        content: this.identityService.themeColor.value,
      });

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
