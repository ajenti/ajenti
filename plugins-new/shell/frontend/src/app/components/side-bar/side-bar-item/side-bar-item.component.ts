import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { SideBarItem } from '../../../services/side-bar/side-bar-item.type';


@Component({
  selector: 'app-side-bar-item',
  templateUrl: './side-bar-item.component.html',
  styleUrls: ['./side-bar-item.component.less']
})
export class SideBarItemComponent implements OnInit {

  @Input()
  public item: SideBarItem;

  constructor(
    private routerService: Router,
  ) {
    this.item = {} as SideBarItem;
  }

  ngOnInit(): void {
  }

  public getCSSClasses(): string {

    let cssClasses: string[] = [
      'sidebar-item',
    ];

    if (this.item.isRoot) {
      cssClasses.push('isRoot');
    }

    if (this.item.isTopLevel) {
      cssClasses.push('isTopLevel');
    }

    if (this.item.hasChildren) {
      cssClasses.push('hasChildren');
    }

    if (this.routerService.url === this.item.url) {
      cssClasses.push('active');
    }

    return cssClasses.join(' ');
  }

}
