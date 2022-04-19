import { Component, Input, OnInit } from '@angular/core';


@Component({
  selector: 'ajenti-smart-progress',
  templateUrl: './smart-progress.component.html',
  styleUrls: [ './smart-progress.component.less' ],
})
export class SmartProgressComponent implements OnInit {

  @Input() type: string = 'warning';
  @Input() max: number = 100;
  @Input() value: number = 0;
  @Input() text?: string;
  @Input() maxText?: any;
  @Input() animate?: boolean;

  constructor() {
  }

  ngOnInit(): void {
  }

}
