import { Component, ComponentFactoryResolver, Input, OnInit, Type, ViewChild } from '@angular/core';
import { WidgetHost } from './widget-host.directive';
import { WidgetDto } from '../../models/user-config-service/widget.dto';
import { DashboardConfigService } from '../../services/dashboard-config.service';
import { WidgetConfigComponent } from '../widget-config.component';
import { WidgetValuesService } from '../../services/widget-values.service';
import { WidgetComponentProvider } from '../../services/widget-component-provider';
import { MessageBoxService, TranslateService } from '@ngx-ajenti/core';
import { WidgetComponent } from '../widget.component';

@Component({
  selector: 'app-widget-container',
  templateUrl: './widget-container.component.html',
  styleUrls: [ '../widget-shared.less',
    './../../../../../node_modules/bootstrap/dist/css/bootstrap.min.css' ],
})
export class WidgetContainerComponent implements OnInit {

  @Input() widget: WidgetDto = new WidgetDto();
  @ViewChild(WidgetHost, { static: true }) widgetHost!: WidgetHost;

  widgetConfigComponent: Type<WidgetConfigComponent> | null = null;

  constructor(
    public componentFactoryResolver: ComponentFactoryResolver,
    public dashboardConfigService: DashboardConfigService,
    private widgetValuesService: WidgetValuesService,
    private widgetComponentProvider: WidgetComponentProvider,
    private messageBoxService: MessageBoxService,
    private translateService: TranslateService,
  ) {
  }

  ngOnInit() {
    if (!this.widget) {
      return;
    }

    const widgetComponentInstance = this.widgetComponentProvider.initializeComponentInstance(
      this.widget,
      this.componentFactoryResolver,
      this.widgetHost.viewContainerRef,
    );

    this.widgetConfigComponent = widgetComponentInstance.configWidgetComponent;
    this.subscribeFetchingWidgetValues(this.widget, widgetComponentInstance);
  }

  private subscribeFetchingWidgetValues(widget: WidgetDto, widgetComponentInstance: WidgetComponent) {
    this.widgetValuesService.widgetValues.subscribe({
      next: (widgetValues) => {
        if (widgetValues.widgetId == widget.id) {
          widgetComponentInstance.updateWidgetWithNewValues(widgetValues.values);
        }
      },
    });
  }

  openConfiguration() {
    if (!this.widgetConfigComponent) {
      return;
    }

    const title = this.translateService.instant('Settings');
    const acceptButtonLabel = this.translateService.instant('Save');
    const cancelButtonLabel = this.translateService.instant('Cancel');
    const messageBox = this.messageBoxService.show({
      title:title,
      acceptButtonLabel:acceptButtonLabel,
      cancelButtonLabel:cancelButtonLabel,
      visible:false,
      injectedComponentType:this.widgetConfigComponent,
      injectComponentData:this.widget.config,
    });

    messageBox.accepted = () => {
      this.dashboardConfigService.changeWidgetConfig(this.widget.id, messageBox.injectedComponentInstance?.getData());
    };
  }
}
