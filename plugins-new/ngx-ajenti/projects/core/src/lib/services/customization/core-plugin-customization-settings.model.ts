import { ExtraProfileMenuItem } from './extra-profile-menu-item.model';

export class CorePluginCustomizationSettings {
    constructor() {
        this.extraProfileMenuItems = [];
    }

    public title?: string;
    public logoURL?: string;
    public bigLogoURL?: string;
    public extraProfileMenuItems: ExtraProfileMenuItem[];
    public bodyClass?: string;
    public enableMixpanel?: boolean;
    public faviconURL?: string;
    public startupURL?: string;
    public loginRedirectionPath?: string;
}
