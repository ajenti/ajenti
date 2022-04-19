import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TrafficModule } from './traffic/traffic.module';

@NgModule({
  declarations: [
    AppComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    TrafficModule,
    HttpClientModule,
  ],
  providers: [],
  bootstrap: [ AppComponent ],
})
export class AppModule {
}
