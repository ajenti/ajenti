import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';


const routes: Routes = [
  {
    path: '',
    redirectTo: 'tryout',
    pathMatch: 'full',
  },
  {
    path: 'tryout',
    loadChildren: () => import('./tryout/tryout.module')
      .then(m => m.TryoutModule),
  },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ],
})
export class AppRoutingModule {
}
