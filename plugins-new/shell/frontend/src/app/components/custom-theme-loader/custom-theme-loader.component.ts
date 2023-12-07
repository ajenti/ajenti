import {Component, OnInit, Type, ViewChild} from '@angular/core';
import {loadRemoteModule} from '@angular-architects/module-federation';
import {PluginDto} from "@ngx-ajenti/core";
import {firstValueFrom} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {ThemeHost} from "./theme-host.directive";

@Component({
    selector: 'theme-loader',
    template: `<ng-template themeHost></ng-template>`,
})
export class CustomThemeLoaderComponent implements OnInit {

    @ViewChild(ThemeHost, {static: true}) themeHost!: ThemeHost;

    constructor(
        private httpClient: HttpClient,
    ) {
    }

    async ngOnInit() {
        await this.loadCustomThemeFromRemoteModule();
    }

    private async loadCustomThemeFromRemoteModule() {
        const externalPlugins = await firstValueFrom(
            this.httpClient.get<PluginDto[]>('resources/plugins.json'));
        for (const externalPlugin of externalPlugins) {
            if (externalPlugin.themeComponent) {
                const remoteModule = await loadRemoteModule(
                    {
                        remoteEntry: externalPlugin.remoteEntry,
                        remoteName: externalPlugin.remoteName,
                        exposedModule: `./${externalPlugin.themeComponent}`,
                    });
                let componentType: Type<any> = remoteModule[externalPlugin.themeComponent];
                const viewContainerRef = this.themeHost.viewContainerRef;
                viewContainerRef.clear();
                viewContainerRef.createComponent(componentType);

                return;
            }
        }
    }
}
