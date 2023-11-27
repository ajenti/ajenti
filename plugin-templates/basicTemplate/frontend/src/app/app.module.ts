import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import {HttpClientModule} from "@angular/common/http";
import {BasicTemplateModule} from "./basicTemplate/basicTemplate.module";

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    AppRoutingModule,
    HttpClientModule,
    BasicTemplateModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
