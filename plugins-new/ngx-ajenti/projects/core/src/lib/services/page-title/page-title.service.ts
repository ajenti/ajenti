import { Injectable } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { BehaviorSubject, Observable } from 'rxjs';
import { IdentityService } from '../identity/identity.service';


/**
 * Service configure the page title.
 */
@Injectable({
  providedIn: 'root',
})
export class PageTitleService {

  private pageTitle: BehaviorSubject<string>;

  constructor(
    private identityService: IdentityService,
    private titleService: Title,
  ) {
    this.pageTitle = new BehaviorSubject<string>('');
    this.setTitle('');
  }

  /**
   * Initializes the service.
   */
  public init(): void {
    this.setTitle('');
  }

  /**
   * Gets the page title.
   *
   * @returns The page title.
   */
  public getTitle(): Observable<string> {
    return this.pageTitle.asObservable();
  }

  /**
   * Sets the page title and updates the windows/tab title.
   *
   * @param title The title to set.
   */
  public setTitle(title: string): void {
    this.pageTitle.next(title);

    const { machine } = this.identityService;
    const machineName = machine.value?.name || '';
    const windowTitle = (title + (title ? ' | ' : '') + machineName) || 'Ajenti';
    this.titleService.setTitle(windowTitle);
  }
}
