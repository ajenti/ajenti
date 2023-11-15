import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
// import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { Session_listModule } from './session_list/session_list.module';

@NgModule({
  declarations: [
    AppComponent,
  ],
  imports: [
    // BrowserModule,
    AppRoutingModule,
    Session_listModule,
    HttpClientModule,
  ],
  providers: [],
  bootstrap: [ AppComponent ],
})
export class AppModule {
}
