/**
 * Provides functionalities to restart the panel.
 */

import { MessageBoxService } from '../message-box/message-box.service';
import { Injectable, Type } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class RestartService {

  constructor(
    private mbs: MessageBoxService,
    private httpClient: HttpClient,
    ) {};

  public pageReload(): void {
    window.location.reload();
  };

  public restart(): void {
    const messageBox = this.mbs.show("Restart the panel ?", "Restart ?", undefined,undefined, "Yes", "No");

    messageBox.accepted = () => {
      this.forceRestart();
    };
  };

  private async forceRestart(): Promise<void> {
    let msg = this.mbs.show('', "Restarting...", '', '', '', '', false, false, true);
    await this.httpClient.post('/api/core/restart-master', '').subscribe((value) => {
      setTimeout(() => {
        msg.close()
        this.mbs.show('', "Restarted !");
        this.pageReload();
        setTimeout(() => {
          this.pageReload();
        }, 5000);
      }, 5000);
    }, () => {
      msg.close();
      console.error("Failed to restart");
    });
  };
}
