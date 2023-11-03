import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { TRYOUT_ROUTES } from './tryout.routes';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { AjentiModule } from '@ajenti/ajenti.module';
import { TryoutComponent } from './view/tryout/tryout.component';

@NgModule({
  declarations: [
    TryoutComponent,
  ],
  exports: [
    TryoutComponent,
  ],
  imports: [
    AjentiModule,
    RouterModule.forChild(TRYOUT_ROUTES),
    DragDropModule
  ],
})
export class TryoutModule {
}
