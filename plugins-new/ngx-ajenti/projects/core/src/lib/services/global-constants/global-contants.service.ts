import { Injectable } from '@angular/core';
import { GlobalConstants } from '../../extensions/Window';


/**
 * Provides functionalities to access global constants.
 */
@Injectable({
  providedIn: 'root',
})
export class GlobalConstantsService {

  /**
   * Gets the global constants.
   */
  public get constants(): GlobalConstants {
    return window.globalConstants;
  }

}
