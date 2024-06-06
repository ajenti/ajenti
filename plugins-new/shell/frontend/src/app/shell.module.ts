import { NgModule } from '@angular/core';
import { ShellComponent } from './shell.component';
import { NavBarComponent } from './components/nav-bar/nav-bar.component';
import { ErrorViewComponent } from './views/error-view/error-view.component';
import { LoginViewComponent } from './views/login-view/login-view.component';
import { SideBarComponent } from './components/side-bar/side-bar.component';
import { SideBarItemComponent } from './components/side-bar/side-bar-item/side-bar-item.component';
import { LoadingBarModule } from '@ngx-loading-bar/core';
import { LoadingBarRouterModule } from '@ngx-loading-bar/router';
import { LoadingBarHttpClientModule } from '@ngx-loading-bar/http-client';
import { SideBarTasksComponent } from './components/side-bar-tasks/side-bar-tasks.component';
import { AjentiModule } from '@ajenti/ajenti.module';
import { MessageBoxContainerComponent } from './components/message-box-container/message-box-container.component';
import { TOASTER_SERVICE_ADAPTER, TranslateService } from '@ngx-ajenti/core';
import { RoutingModule } from './routing.module';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ToastrService } from 'ngx-toastr';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { UnauthenticatedInterceptor } from './interceptors/unauthenticated.interceptor';
import { UrlPrefixInterceptor } from './interceptors/urlPrefix.interceptor';
import {CustomThemeLoaderComponent} from "./components/custom-theme-loader/custom-theme-loader.component";
import {ThemeHost} from "./components/custom-theme-loader/theme-host.directive";
import { SharedStylesComponent } from './components/shared-styles/shared-styles.component';

@NgModule({
  declarations: [
    ShellComponent,
    CustomThemeLoaderComponent,
    SharedStylesComponent,
    NavBarComponent,
    ErrorViewComponent,
    LoginViewComponent,
    MessageBoxContainerComponent,
    SideBarComponent,
    SideBarItemComponent,
    SideBarTasksComponent,
    ThemeHost,
  ],
  providers: [ TranslateService,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: UnauthenticatedInterceptor,
      multi: true,
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: UrlPrefixInterceptor,
      multi: true,
    },
    {
      provide: TOASTER_SERVICE_ADAPTER,
      useExisting: ToastrService,
    },
  ],
  imports: [
    AjentiModule,
    RoutingModule,
    LoadingBarHttpClientModule,
    LoadingBarRouterModule,
    LoadingBarModule,
    BrowserAnimationsModule,
  ],
  bootstrap: [ ShellComponent ],
})
export class ShellModule {
}
