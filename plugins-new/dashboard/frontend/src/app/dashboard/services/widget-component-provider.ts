import { ComponentFactoryResolver, Injectable, Type, ViewContainerRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { WidgetComponent } from '../components/widget.component';
import { CpuWidgetComponent } from '../components/cpu-widget/cpu-widget.component';
import { HostnameWidgetComponent } from '../components/hostname-widget/hostname-widget.component';
import { LoadavgWidgetComponent } from '../components/loadavg-widget/loadavg-widget.component';
import { MemoryWidgetComponent } from '../components/memory-widget/memory-widget.component';
import { loadRemoteModule } from '@angular-architects/module-federation';
import { UptimeWidgetComponent } from '../components/uptime-widget/uptime-widget.component';
import { WidgetDto } from '../models/user-config-service/widget.dto';
import { firstValueFrom } from 'rxjs';
import { PluginDto } from '@ngx-ajenti/core';

@Injectable({
  providedIn: 'root',
})
export class WidgetComponentProvider {

  private componentTypes: { [widgetTypeId: string]: Type<WidgetComponent> };
  private isInitialized = false;

  constructor(private httpClient: HttpClient) {
    this.componentTypes = {};
  }

  async initializeWidgetComponents() {
    if (this.isInitialized) {
      return;
    }

    this.componentTypes['cpu'] = CpuWidgetComponent;
    this.componentTypes['hostname'] = HostnameWidgetComponent;
    this.componentTypes['loadavg'] = LoadavgWidgetComponent;
    this.componentTypes['uptime'] = UptimeWidgetComponent;
    this.componentTypes['memory'] = MemoryWidgetComponent;

    await this.initializeExternalComponentTypes();
    this.isInitialized = true;
  }

  private async initializeExternalComponentTypes() {
    const externalPlugins = await firstValueFrom(
      this.httpClient.get<PluginDto[]>('resources/plugins.json'));

    for (const externalPlugin of externalPlugins) {
      for (const componentName of externalPlugin.widgetComponents) {
        const remoteModule = await loadRemoteModule(
          {
            remoteEntry: externalPlugin.remoteEntry,
            remoteName: externalPlugin.remoteName,
            exposedModule: `./${ componentName }`,
          });

        const widgetComponent = remoteModule[componentName];
        const widgetTypeId = componentName.split('WidgetComponent')[0].toLowerCase();
        this.componentTypes[widgetTypeId] = widgetComponent;
      }
    }
  }

  initializeComponentInstance(
    widget: WidgetDto,
    componentFactoryResolver: ComponentFactoryResolver,
    viewContainerRef: ViewContainerRef,
  ): WidgetComponent {
    const componentType: Type<WidgetComponent> = this.componentTypes[widget.typeId];
    viewContainerRef.clear();
    const componentRef = viewContainerRef.createComponent(componentType);
    const componentInstance: WidgetComponent = componentRef.instance;
    componentInstance.widget = widget;

    return componentInstance;
  }
}
