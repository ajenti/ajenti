import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { GetSideBarItemResponse } from './get-side-bar-item-response.type';
import { SideBarItem } from './side-bar-item.type';
import { Event, NavigationEnd, Router, RouterEvent } from '@angular/router';
import { Identity, IdentityService } from '@ngx-ajenti/core';


@Injectable({
  providedIn: 'root',
})
export class SideBarService {

  private showSidebar: BehaviorSubject<boolean>;
  private showOverlaySidebar: BehaviorSubject<boolean>;
  private sideBarRootItem: BehaviorSubject<SideBarItem | null>;

  constructor(
    private httpClient: HttpClient,
    private identityService: IdentityService,
    private routerService: Router,
  ) {
    this.showSidebar = new BehaviorSubject<boolean>(false);
    this.showOverlaySidebar = new BehaviorSubject<boolean>(false);
    this.sideBarRootItem = new BehaviorSubject<SideBarItem | null>(null);

    this.identityService.identity.subscribe(this.onIdentityChanged);
    this.routerService.events.subscribe(this.onNavigation);
  }

  /**
   * Gets the root item of the side bar if any.
   */
  public getSideBarRootItem(): Observable<SideBarItem | null> {
    return this.sideBarRootItem.asObservable();
  }

  /**
   * Gets the showSidebar option.
   */
  public getShowSidebar(): Observable<boolean> {
    return this.showSidebar.asObservable();
  }

  /**
   * Sets the showSidebar option.
   */
  public setShowSideBar(value: boolean): void {
    localStorage.setItem('showSidebar', String(value));
    this.showSidebar.next(value);
  }

  /**
   * Toggles the showSidebar state.
   */
  public toggleShowSideBar(): void {
    const newShowSideBarValue = !this.showSidebar.value;
    this.setShowSideBar(newShowSideBarValue);
  }

  /**
   * Gets the showOverlaySidebar option.
   */
  public getShowOverlaySidebar(): Observable<boolean> {
    return this.showOverlaySidebar.asObservable();
  }

  /**
   * Sets the showOverlaySidebar option.
   */
  public setShowOverlaySideBar(value: boolean): void {
    localStorage.setItem('showOverlaySidebar', String(value));
    this.showOverlaySidebar.next(value);
  }

  /**
   * Toggles the showOverlaySidebar state.
   */
  public toggleShowOverlaySideBar(): void {
    const newShowOverlaySideBarValue = !this.showOverlaySidebar.value;
    this.setShowOverlaySideBar(newShowOverlaySideBarValue);
  }

  private async loadSideBarItems(): Promise<void> {
    const response = await this.httpClient.get<GetSideBarItemResponse>('/api/core/sidebar').toPromise();
    if (!response) {
      return;
    }
    const sideBarItem = new SideBarItem(response.sidebar);

    // TODO: This workaround must be solved in a nicer way! At least it should happen in the backend!
    sideBarItem.isRoot = true;
    for (let child of sideBarItem.children) {
      child.isTopLevel = true;
    }

    this.sideBarRootItem.next(sideBarItem);

    const firstUrlInNavigationTree = sideBarItem.findFirstUrlInTree();
    if (this.routerService.url === '/view' && firstUrlInNavigationTree) {
      await this.routerService.navigate([ sideBarItem.findFirstUrlInTree() ]);
    }
  }

  private getInitialShowSideBarValue(isUserSignedIn?: boolean): boolean {
    const persistedShowSideBar = localStorage.getItem('showSidebar');

    let initialShowSideBarValue = !!isUserSignedIn;

    if (this.routerService.url.includes('/view/login')) {
      initialShowSideBarValue = false;
    } else if (isUserSignedIn && persistedShowSideBar !== null) {
      initialShowSideBarValue = persistedShowSideBar === 'true';
    }

    return initialShowSideBarValue;
  }

  private onIdentityChanged = async (identity: Identity | null): Promise<void> => {
    if (!identity) {
      return;
    }
    await this.loadSideBarItems();
    this.resetShowSideBar(identity);
  };

  private onNavigation = (event: unknown): void => {
    if (event instanceof NavigationEnd && event.url.includes('/view/login')) {
      this.showSidebar.next(false);
      this.showOverlaySidebar.next(false);
    } else {
      this.resetShowSideBar(this.identityService.identity.value);
    }
  };

  private resetShowSideBar(identity: Identity | null) {
    const showSideBar = this.getInitialShowSideBarValue(identity?.isUserSignedIn);
    this.showSidebar.next(showSideBar);
    this.showOverlaySidebar.next(showSideBar);
  }

}
