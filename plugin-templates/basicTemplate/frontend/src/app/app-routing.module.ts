import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';


const routes: Routes = [
  {
    path: '',
    redirectTo: 'basicTemplate',
    pathMatch: 'full',
  },
  {
    path: 'basicTemplate',
    loadChildren: () => import('./basicTemplate/basicTemplate.module')
      .then(m => m.BasicTemplateModule),
  },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ],
})
export class AppRoutingModule {
}

