import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { AjentiModule } from '@ajenti/ajenti.module';
import {CustomShellStyleComponent} from "./custom-shell-style/custom-shell-style.component";

@NgModule({
  declarations: [
    CustomShellStyleComponent,
  ],
  exports: [
    CustomShellStyleComponent,
  ],
  imports: [
    AjentiModule,
    RouterModule.forChild([{
      path: '',
      component: CustomShellStyleComponent,
    }]),
  ],
})
export class ThemeModule {
  constructor(
  ) {
  }
}
