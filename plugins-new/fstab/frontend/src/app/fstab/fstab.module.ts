import { NgModule } from '@angular/core';
import { FstabComponent } from './view/fstab/fstab.component';
import { RouterModule } from '@angular/router';
import { FSTAB_ROUTES } from './fstab.routes';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { AjentiModule } from '@ajenti/ajenti.module';
import { MatTabsModule } from '@angular/material/tabs';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDialogModule } from "@angular/material/dialog";
import { MatInputModule } from "@angular/material/input";
import { FstabDialogComponent } from './view/fstab-dialog/fstab-dialog.component';
import {MatCommonModule} from '@angular/material/core';
import {MatButtonModule} from '@angular/material/button';

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
    MatDialogModule,
    DragDropModule,
    MatTabsModule,
    BrowserAnimationsModule,
    MatButtonModule,
    MatCommonModule,
    MatDialogModule,
    MatInputModule,
  ],
})
export class FstabModule {
}
