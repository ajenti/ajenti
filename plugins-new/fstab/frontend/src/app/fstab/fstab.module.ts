import { NgModule } from '@angular/core';
import { FstabComponent } from './view/fstab/fstab.component';
import { RouterModule } from '@angular/router';
import { FSTAB_ROUTES } from './fstab.routes';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { AjentiModule } from '@ajenti/ajenti.module';
import { MatTabsModule } from '@angular/material/tabs';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    FstabComponent,
  ],
  exports: [
    FstabComponent,
  ],
  imports: [
    AjentiModule,
    RouterModule.forChild(FSTAB_ROUTES),
    DragDropModule,
    MatTabsModule,
    BrowserAnimationsModule,
  ],
})
export class FstabModule {
}
