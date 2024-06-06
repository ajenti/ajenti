import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { SideBarItem } from '../../services/side-bar/side-bar-item.type';
import { SideBarService } from '../../services/side-bar/side-bar.service';


@Component({
  selector: 'app-side-bar',
  templateUrl: './side-bar.component.html',
  styleUrls: [ './side-bar.component.less' ],
})
export class SideBarComponent implements OnInit {

  public sideBarRootItem: SideBarItem | null;
  public showSidebar: boolean;
  public showOverlaySidebar: boolean;

  constructor(
    private routerService: Router,
    private sideBarService: SideBarService,
  ) {
    this.sideBarRootItem = null;
    this.showSidebar = false;
    this.showOverlaySidebar = false;
  }

  ngOnInit(): void {
    this.sideBarService
      .getSideBarRootItem()
      .subscribe(sideBarRootItem => {
        this.sideBarRootItem = sideBarRootItem;
      });
    this.sideBarService.getShowSidebar()
      .subscribe(showSidebar => {
        this.showSidebar = showSidebar;
      });
    this.sideBarService.getShowOverlaySidebar()
      .subscribe(showOverlaySidebar => {
        this.showOverlaySidebar = showOverlaySidebar;
      });
  }
}
