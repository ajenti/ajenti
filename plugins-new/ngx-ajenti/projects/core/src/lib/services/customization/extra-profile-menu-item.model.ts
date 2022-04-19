/**
 * Defines an extra profile menu item to extend the core menu.
 */
export class ExtraProfileMenuItem {

    constructor() {
        this.url = '';
        this.icon = '';
        this.name = '';
    }

    /**
     * The URL of the extra profile menu item.
     */
    public url: string;

    /**
     * The icon of the extra profile menu item.
     */
    public icon: string;

    /**
     * The name of the extra profile menu item.
     */
    public name: string;

}
