import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { CorePluginCustomizationSettings } from './core-plugin-customization-settings.model';


@Injectable({
  providedIn: 'root',
})
export class CustomizationService {

  private readonly pluginCustomizations: { [pluginName: string]: BehaviorSubject<any> };

  constructor() {
    this.pluginCustomizations = {
      'core': new BehaviorSubject(new CorePluginCustomizationSettings()),
    };
  }

  /**
   * Gets the plugin customizations for a specific plugin.
   *
   * @param pluginName The name to get the customizations for.
   *
   * @returns The plugin customizations for a specific plugin.
   *
   * @throws An error if the plugin does not have customizations.
   */
  public getPluginCustomizations<T>(pluginName: string): Observable<T> {
    if (!Object.keys(this.pluginCustomizations).includes(pluginName)) {
      throw new Error(`No customizations for a the plugin ${pluginName} exists.`);
    }

    return this.pluginCustomizations[pluginName].asObservable();
  }

  /**
   * Sets the customizations for a plugin.
   *
   * Note: (WILL BE FIXED WITH A3-58!!!!) New values will be merged with existing values.
   *
   * @param pluginName The unique name of the plugin.
   * @param nextValue The new customization values for the plugin.
   *
   * @example
   *  // To reset an existing value it must be explicitly set to null.
   *  this.customizationService
   *      .setPluginCustomizations<CorePluginCustomizationSettings>(
   *        'core',
   *        {
   *          valueToReset: null,
   *        }
   *      );
   */
  public setPluginCustomizations<T>(pluginName: string, newValue: Partial<T>): void {
    // const previousValue: T = this.pluginCustomizations[pluginName].value;
    // const deeplyMergedValue: T = jQuery.extend(true, {}, previousValue, newValue);

    this.pluginCustomizations[pluginName].next(newValue);
  }
}
