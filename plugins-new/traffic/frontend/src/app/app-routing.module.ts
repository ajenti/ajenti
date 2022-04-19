import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';


const routes: Routes = [
  {
    path: '',
    redirectTo: 'traffic',
    pathMatch: 'full',
  },
  {
    path: 'traffic',
    loadChildren: () => import('./traffic/traffic.module')
      .then(m => m.TrafficModule),
  },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ],
})
export class AppRoutingModule {
}
