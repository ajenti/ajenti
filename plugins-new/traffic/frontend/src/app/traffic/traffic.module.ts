import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { TrafficWidgetComponent } from './components/traffic-widget/traffic-widget.component';
import { TrafficWidgetConfigComponent } from './components/traffic-widget-config/traffic-widget-config.component';
import { TRAFFIC_ROUTES } from './traffic.routes';
import { AjentiModule } from '@ajenti/ajenti.module';

@NgModule({
  declarations: [
    TrafficWidgetComponent,
    TrafficWidgetConfigComponent ],
  exports: [
    TrafficWidgetComponent,
    TrafficWidgetConfigComponent,
  ],
  imports: [
    AjentiModule,
    RouterModule.forChild(TRAFFIC_ROUTES),
  ],
})
export class TrafficModule {
}
