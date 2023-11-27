
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {firstValueFrom} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class BasicTemplateService {

  constructor(
    private httpClient: HttpClient,
  ) {
  }

  public  hello_word() {
    return firstValueFrom(this.httpClient.get<string>('/api/basicTemplate'));
  }

}
