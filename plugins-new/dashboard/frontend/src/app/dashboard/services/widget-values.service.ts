import { Injectable } from '@angular/core';
import { HttpClient, HttpContext } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { WidgetValues } from '../components/widget-values';
import { WidgetValuesRequestDto } from '../models/dashboard/widget-values-request.dto';
import { NGX_LOADING_BAR_IGNORED } from '@ngx-loading-bar/http-client';
import { TabService } from './tab.service';
import { WidgetValuesDto } from '../models/dashboard/widget-values.dto';


@Injectable({
  providedIn: 'root',
})
export class WidgetValuesService {

  private _widgetValues: BehaviorSubject<WidgetValues>;

  constructor(
    private httpClient: HttpClient,
    private tabService: TabService,
  ) {
    this._widgetValues = new BehaviorSubject<WidgetValues>(new WidgetValues('', null));
    this.startWidgetsAutoUpdate();
  }

  get widgetValues(): Observable<WidgetValues> {
    return this._widgetValues.asObservable();
  }

  private startWidgetsAutoUpdate() {
    setInterval(() => {
      this.fetchWidgetValues();
    }, 1000);
  }

  private fetchWidgetValues() {
    const widgetValueRequest = this.getWidgetValuesRequest();
    this.httpClient.post<WidgetValuesDto[]>(
      '/api/dashboard/widget-values', widgetValueRequest, {
        context: new HttpContext().set(NGX_LOADING_BAR_IGNORED, true),
      })
      .subscribe({
        next: (widgetValues: WidgetValuesDto[]) => {
          widgetValues.forEach(response => {
            this._widgetValues.next(new WidgetValues(response.widgetId, response.widgetValues));
          });
        },

        error: (error: any) => {
          console.error('Error in retrieving widgets values:', error);
        },
      });
  }

  getWidgetValuesRequest(): WidgetValuesRequestDto[] {
    const widgetValueRequest: WidgetValuesRequestDto[] = [];
    for (const widget of this.tabService.activeWidgets) {
      widgetValueRequest.push(new WidgetValuesRequestDto(widget.id, widget.typeId, widget.config));
    }

    return widgetValueRequest;
  }
}
