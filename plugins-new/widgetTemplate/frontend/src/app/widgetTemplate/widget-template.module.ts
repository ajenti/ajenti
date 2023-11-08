import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { WIDGETTEMPLATE_ROUTES } from './widget-template.routes';
import { AjentiModule } from '@ajenti/ajenti.module';
import {WidgetTemplateComponent} from "./components/widget-template-widget/widget-template-widget.component";
import {
  WidgetTemplateConfigComponent
} from "./components/widgetTemplate-widget-config/widget-template-config.component";

@NgModule({
  declarations: [
    WidgetTemplateComponent,
    WidgetTemplateConfigComponent],
  exports: [
    WidgetTemplateComponent,
    WidgetTemplateConfigComponent,
  ],
  imports: [
    AjentiModule,
    RouterModule.forChild(WIDGETTEMPLATE_ROUTES),
  ],
})
export class WidgetTemplateModule {
}
