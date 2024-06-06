import {ExtraProfileMenuItem} from './extra-profile-menu-item.model';

export const DEFAULT_THEME_COLOR = 'default';
export const BLUEGREY_THEME_COLOR = 'bluegrey';

export class CorePluginCustomizationSettings {
  constructor(setDefaultThemeColor: boolean = false) {
    this.extraProfileMenuItems = [];
    this.themeColor = setDefaultThemeColor?DEFAULT_THEME_COLOR: BLUEGREY_THEME_COLOR;
  }

  public title?: string;
  public logoURL?: string;
  public bigLogoURL?: string;
  public extraProfileMenuItems: ExtraProfileMenuItem[];
  public themeColor?: string;
  public cssClass?: string;
  public enableMixpanel?: boolean;
  public faviconURL?: string;
  public startupURL?: string;
  public loginRedirectionPath?: string;
}
