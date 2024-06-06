import { HammerGestureConfig, HAMMER_GESTURE_CONFIG } from '@angular/platform-browser';
import * as Hammer from 'hammerjs';
import { Injectable } from '@angular/core';


@Injectable({
  providedIn: 'root',
})
class AjentiHammerJSConfig extends HammerGestureConfig {
  overrides = <any> {
    swipe: { direction: Hammer.DIRECTION_ALL },
  };
}

export const AjentiHammerJSProvider = {
  provide: HAMMER_GESTURE_CONFIG,
  useClass: AjentiHammerJSConfig,
};
