import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';


const routes: Routes = [
  {
    path: '',
    redirectTo: 'widget-template',
    pathMatch: 'full',
  },
  {
    path: 'widget-template',
    loadChildren: () => import('./widgetTemplate/widget-template.module')
      .then(m => m.WidgetTemplateModule),
  },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ],
})
export class AppRoutingModule {
}
