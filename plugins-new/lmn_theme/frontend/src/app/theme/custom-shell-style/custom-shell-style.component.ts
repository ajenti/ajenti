import {Component, ViewEncapsulation} from '@angular/core';
import {CorePluginCustomizationSettings, CustomizationService, ExtraProfileMenuItem} from "@ngx-ajenti/core";

@Component({
    encapsulation: ViewEncapsulation.None,
    template: '',
    styleUrls: ['./custom-shell-styles.less'],
})
export class CustomShellStyleComponent {
    constructor(
        private customizationService: CustomizationService,
    ) {
        this.customizationService.setPluginCustomizations('core', this.getCustomShellSettings());
    }

    getCustomShellSettings(): CorePluginCustomizationSettings {
        const settings = new CorePluginCustomizationSettings(true);
        settings.title = ' ';
        settings.cssClass = 'examplePluginCssClass'; // Must match the .less file
        settings.logoURL = 'https://www.linuxmuster.net/wp-content/uploads/2017/01/logo_homepage-1.png';
        settings.extraProfileMenuItems = [
            new ExtraProfileMenuItem('Plugin item', '/ssdashboard', 'camera-retro'),
            new ExtraProfileMenuItem('Plugin item 2', '/bookStore', 'book'),
        ];

        return settings;
    }
}
