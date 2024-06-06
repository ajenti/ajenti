import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ErrorViewComponent } from './views/error-view/error-view.component';
import { LoginViewComponent } from './views/login-view/login-view.component';
import { getPluginRoutes } from '../../plugin-list-loader';


const routes: Routes = [
  { path: '', redirectTo: 'view', pathMatch: 'full' },
  {
    path: 'view',

    children: [
      { path: 'login', redirectTo: 'login/normal', pathMatch: 'full' },
      { path: 'login/:mode', component: LoginViewComponent },
      { path: 'login/:mode/:username', component: LoginViewComponent },
      { path: 'error', component: ErrorViewComponent },
      ...getPluginRoutes(),
    ],
  },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ],
})
export class RoutingModule {
}
