import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

/**
 * Provide screen relevant functionalities.
 */
@Injectable({
  providedIn: 'root',
})
export class ScreenService {

  private isWidescreenSubject: BehaviorSubject<boolean>;

  constructor() {
    this.isWidescreenSubject = new BehaviorSubject<boolean>(
      localStorage.getItem('isWidescreen') === 'true',
    );
  }

  /**
   * Gets the isWidescreen option.
   */
  public getIsWidescreen(): Observable<boolean> {
    return this.isWidescreenSubject.asObservable();
  }

  /**
   * Toggles the isWidescreen option.
   */
  public toggleIsWidescreen(): void {
    const newIsWidescreenValue = !this.isWidescreenSubject.value;
    localStorage.setItem('isWidescreen', String(newIsWidescreenValue));
    this.isWidescreenSubject.next(newIsWidescreenValue);
  }
}
