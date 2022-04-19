import { loadRemoteEntry, loadRemoteModule } from '@angular-architects/module-federation';
import { Routes } from '@angular/router';
import { PluginDto } from '@ngx-ajenti/core';

const xmlHttp = new XMLHttpRequest();
xmlHttp.open('GET', 'resources/plugins.json', false); // false for synchronous request
xmlHttp.send(null);

export const plugins: PluginDto[] = JSON.parse(xmlHttp.responseText) || [];

export function loadAllPluginsEntries(): Promise<void>[] {
  const promises = new Array<Promise<void>>();

  for (let plugin of plugins) {
    promises.push(loadRemoteEntry({
      type: 'script',
      remoteEntry: plugin.remoteEntry,
      remoteName: plugin.remoteName,
    }));
  }

  return promises;
}

export function getPluginRoutes(): Routes {
  const pluginRoutes: Routes = [];

  for (let plugin of plugins) {
    pluginRoutes.push({
      path: plugin.routePath,
      loadChildren: () => loadRemoteModule({
        type: 'script',
        remoteEntry: plugin.remoteEntry,
        remoteName: plugin.remoteName,
        exposedModule: plugin.exposedModule,
      })
        .then(m => m[plugin.ngModuleName]),
    });
  }

  return pluginRoutes;
}
