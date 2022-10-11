import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'fstab-dialog',
  templateUrl: './fstab-dialog.component.html',
  styleUrls: ['./fstab-dialog.component.less']
})
export class FstabDialogComponent {

  constructor(
    public dialogRef: MatDialogRef<FstabDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
  ) { }

  onCancel(): void {
    this.dialogRef.close();
  }

}
