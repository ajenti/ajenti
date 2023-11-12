import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';


const routes: Routes = [
  {
    path: '',
    redirectTo: 'fstab',
    pathMatch: 'full',
  },
  {
    path: 'fstab',
    loadChildren: () => import('./fstab/fstab.module')
      .then(m => m.FstabModule),
  },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ],
})
export class AppRoutingModule {
}
