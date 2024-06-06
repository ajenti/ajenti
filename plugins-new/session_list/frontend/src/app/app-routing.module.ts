import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';


const routes: Routes = [
  {
    path: '',
    redirectTo: 'session_list',
    pathMatch: 'full',
  },
  {
    path: 'session_list',
    loadChildren: () => import('./session_list/session_list.module')
      .then(m => m.Session_listModule),
  },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ],
})
export class AppRoutingModule {
}
