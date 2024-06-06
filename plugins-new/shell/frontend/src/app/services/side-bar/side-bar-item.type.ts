export class SideBarItem {

  constructor(item: SideBarItem) {
    this.id = item.id;
    this.name = item.name || '';
    this.url = item.url;
    this.icon = item.icon;
    this.attach = item.attach;
    this.isRoot = item.isRoot === true;
    this.isTopLevel = item.isTopLevel === true;
    this.expanded = item.isTopLevel !== false;
    this.children = [];
    for (let child of item.children) {
      this.children.push(new SideBarItem(child));
    }
    item.children.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
  }

  public id: string | null;
  public icon?: string;
  public name: string;
  public url?: string;
  public attach?: string;
  public children: SideBarItem[];
  public isRoot: boolean;
  public isTopLevel: boolean;
  public expanded: boolean;

  /**
   * Determines if the side bar item has children.
   */
  public get hasChildren(): boolean {
    return this.children.length > 0;
  };

  public findFirstUrlInTree(): string | undefined {
    if (this.url !== undefined) {
      return this.url;
    }

    for (const child of this.children) {
      const childUrl = child.findFirstUrlInTree();
      if (childUrl !== undefined) {
        return childUrl;
      }
    }

    return undefined;
  }

}
