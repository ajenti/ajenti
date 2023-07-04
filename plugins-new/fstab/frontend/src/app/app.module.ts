import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
// import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FstabModule } from './fstab/fstab.module';

@NgModule({
  declarations: [
    AppComponent,
  ],
  imports: [
    // BrowserModule,
    AppRoutingModule,
    FstabModule,
    HttpClientModule,
  ],
  providers: [],
  bootstrap: [ AppComponent ],
})
export class AppModule {
}
