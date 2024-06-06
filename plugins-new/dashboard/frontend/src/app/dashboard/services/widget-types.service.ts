import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { WidgetTypeDto } from '../models/dashboard/widget-type-dto';

@Injectable({
  providedIn: 'root',
})
export class WidgetTypesService {

  private _widgetTypes: BehaviorSubject<WidgetTypeDto[]>;

  constructor(
    private httpClient: HttpClient,
  ) {
    this._widgetTypes = new BehaviorSubject<WidgetTypeDto[]>([]);
    this.loadAvailableWidgetTypes();
  }

  get widgetTypes(): Observable<WidgetTypeDto[]> {
    return this._widgetTypes.asObservable();
  }

  private loadAvailableWidgetTypes() {
    this.httpClient
      .get<WidgetTypeDto[]>
      ('/api/dashboard/widget-types')
      .subscribe({
          next: (widgetTypes) => {
            this._widgetTypes.next(widgetTypes);
          },
          error: (error: any) => {
            console.error('Error retrieving available widgets:', error);
          },
        },
      );
  }
}
