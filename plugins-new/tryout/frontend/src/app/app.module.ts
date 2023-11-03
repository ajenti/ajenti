import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import {HttpClientModule} from "@angular/common/http";
import {TryoutModule} from "./tryout/tryout.module";

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    AppRoutingModule,
    HttpClientModule,
    TryoutModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
