import { NgModule } from '@angular/core';
import { Session_listComponent } from './view/session_list/session_list.component';
import { RouterModule } from '@angular/router';
import { FSTAB_ROUTES } from './session_list.routes';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { AjentiModule } from '@ajenti/ajenti.module';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';

@NgModule({
  declarations: [
    Session_listComponent,
  ],
  exports: [
    Session_listComponent,
  ],
  imports: [
    AjentiModule,
    RouterModule.forChild(FSTAB_ROUTES),
    DragDropModule,
    MatButtonModule,
    MatTabsModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
  ],
})
export class Session_listModule {
}
