import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { BASICTEMPLATE_ROUTES } from './basicTemplate.routes';
import { AjentiModule } from '@ajenti/ajenti.module';
import { BasicTemplateComponent } from './view/basicTemplate/basicTemplate.component';

@NgModule({
  declarations: [
    BasicTemplateComponent
  ],
  exports: [
    BasicTemplateComponent,
  ],
  imports: [
    AjentiModule,
    RouterModule.forChild(BASICTEMPLATE_ROUTES),
  ],
})
export class BasicTemplateModule {
}
