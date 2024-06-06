import { NgModule } from '@angular/core';
import { FstabComponent } from './view/fstab/fstab.component';
import { RouterModule } from '@angular/router';
import { FSTAB_ROUTES } from './fstab.routes';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { AjentiModule } from '@ajenti/ajenti.module';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { FstabDialogComponent } from './components/fstab-dialog/fstab-dialog.component';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';

@NgModule({
  declarations: [
    FstabComponent,
    FstabDialogComponent,
  ],
  exports: [
    FstabComponent,
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
export class FstabModule {
}
