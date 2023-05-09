import { AfterViewInit, Component, OnInit, QueryList, ViewChildren, ViewContainerRef } from '@angular/core';
import { DataInterface, MessageBox, MessageBoxService } from '@ngx-ajenti/core';

@Component({
  selector: 'app-message-box-container',
  templateUrl: './message-box-container.component.html',
})
export class MessageBoxContainerComponent implements OnInit, AfterViewInit {

  public messageBoxes: MessageBox[];

  @ViewChildren('templateComponent', { read: ViewContainerRef }) templateComponentContainers:
    QueryList<ViewContainerRef> | undefined;

  constructor(
    public messageBoxService: MessageBoxService,
  ) {
    this.messageBoxes = [];
  }

  ngOnInit(): void {
    this.messageBoxService.messageBoxes.subscribe(newMessageBoxes => {
      this.messageBoxes = newMessageBoxes.filter(m => m.visible);
    });
  }

  ngAfterViewInit(): void {
    if (this.templateComponentContainers) {
      this.templateComponentContainers.changes.subscribe(() => {
        this.loadInjectedComponentIfAvailable();
      });
    }
  }

  public async acceptButtonClicked(messageBox: MessageBox) {
    if (!messageBox.accepted) {
      return;
    }

    messageBox.accepted();
    await messageBox.close();
  }

  public async cancelButtonClicked(messageBox: MessageBox) {
    if (messageBox.canceled) {
      messageBox.canceled();
    }

    await messageBox.close();
  }

  private loadInjectedComponentIfAvailable() {
    if (this.messageBoxes.length === 0) {
      return;
    }

    const messageBox = this.messageBoxes[0];
    const injectedComponent = messageBox.injectedComponent;
    const containerForInjectedComponent = this.templateComponentContainers?.first;
    if (!injectedComponent || !containerForInjectedComponent) {
      return;
    }

    containerForInjectedComponent.clear();
    const componentRef = containerForInjectedComponent.createComponent(injectedComponent);

    const instance = componentRef.instance as DataInterface;
    instance.setData(messageBox.injectedComponentData);
    messageBox.injectedComponentInstance = instance;
  }
}
