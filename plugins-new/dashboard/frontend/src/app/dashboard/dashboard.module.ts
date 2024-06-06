import { NgModule } from '@angular/core';
import { DashboardComponent } from './view/dashboard/dashboard.component';
import { RouterModule } from '@angular/router';
import { DASHBOARD_ROUTES } from './dashboard.routes';
import { TabBarComponent } from './components/tab-bar/tab-bar.component';
import { CpuWidgetComponent } from './components/cpu-widget/cpu-widget.component';
import { HostnameWidgetComponent } from './components/hostname-widget/hostname-widget.component';
import { WidgetHost } from './components/widget-container/widget-host.directive';
import { WidgetContainerComponent } from './components/widget-container/widget-container.component';
import { LoadavgWidgetComponent } from './components/loadavg-widget/loadavg-widget.component';
import { UptimeWidgetComponent } from './components/uptime-widget/uptime-widget.component';
import { MemoryWidgetComponent } from './components/memory-widget/memory-widget.component';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { AjentiModule } from '@ajenti/ajenti.module';

@NgModule({
  declarations: [
    DashboardComponent, TabBarComponent, CpuWidgetComponent,
    HostnameWidgetComponent, WidgetContainerComponent, WidgetHost,
    LoadavgWidgetComponent, UptimeWidgetComponent, MemoryWidgetComponent,
  ],
  exports: [
    DashboardComponent,
  ],
  imports: [
    AjentiModule,
    RouterModule.forChild(DASHBOARD_ROUTES),
    DragDropModule,
  ],
})
export class DashboardModule {
}
