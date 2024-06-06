/**
 * Defines an extra profile menu item to extend the core menu.
 */
export class ExtraProfileMenuItem {
  constructor(
    public name: string = '',
    public url: string = '',
    // Font awesome icon name: For 'fa-camera-retro' use 'camera-retro'
    public faIconName: string = ''
  ) {
  }
}
